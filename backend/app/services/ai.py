import json
import logging
from typing import Iterable, List

import aiohttp

from chat_history import Message
from ..config import settings

logger = logging.getLogger(__name__)

MAX_MESSAGES = 20


class AIServiceError(Exception):
    """AI 服务调用异常"""


def _normalize_image_url(image: str) -> str:
    """将 base64 或 data URL 转为 OpenAI 要求的 image_url 格式。"""
    image = (image or "").strip()
    if not image:
        return ""
    if image.startswith("data:"):
        return image
    if image.startswith("http://") or image.startswith("https://"):
        return image
    return f"data:image/jpeg;base64,{image}"


def _build_payload_messages(
    messages: Iterable[Message], image_for_last_user: str | None = None
) -> List[dict]:
    payload = []
    if settings.openai_system_prompt:
        payload.append({"role": "system", "content": settings.openai_system_prompt})

    message_list = list(messages)
    for i, msg in enumerate(message_list):
        is_last_user = (
            msg.role == "user"
            and i == len(message_list) - 1
            and image_for_last_user
        )
        if is_last_user and image_for_last_user:
            url = _normalize_image_url(image_for_last_user)
            content = [
                {"type": "text", "text": msg.content or ""},
                {"type": "image_url", "image_url": {"url": url}},
            ]
            payload.append({"role": msg.role, "content": content})
        else:
            payload.append({"role": msg.role, "content": msg.content})
    return payload


async def generate_ai_reply(
    messages: Iterable[Message], model: str | None = None, image_base64: str | None = None
) -> str:
    """
    调用外部 AI 服务生成回复

    :param messages: 对话消息列表（从旧到新排序）
    :param model: 可选模型名，不传则使用配置默认
    """
    if not settings.openai_api_key:
        raise AIServiceError("未配置 OPENAI_API_KEY，无法调用 AI 服务。")

    message_list = list(messages)
    if not message_list:
        raise AIServiceError("当前对话无历史消息。")

    payload_messages = _build_payload_messages(
        message_list[-MAX_MESSAGES:], image_for_last_user=image_base64
    )

    url = f"{settings.openai_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or settings.openai_model,
        "messages": payload_messages,
        "temperature": 0.7,
    }

    logger.info(
        "发送到 AI API 的原始请求: url=%s payload=%s",
        url,
        payload,
    )

    timeout = aiohttp.ClientTimeout(total=settings.openai_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            raw_response_text = await response.text()
            if len(raw_response_text) > 2000:
                response_preview = raw_response_text[:2000] + "...(truncated)"
            else:
                response_preview = raw_response_text
            logger.info(
                "AI API 原始响应: status=%s body=%s",
                response.status,
                response_preview or "(empty)",
            )

            if response.status >= 400:
                raise AIServiceError(
                    f"AI 服务返回错误状态码 {response.status}: {raw_response_text}"
                )

            try:
                data = json.loads(raw_response_text)
            except json.JSONDecodeError:
                logger.exception("AI API 响应非 JSON: %s", raw_response_text[:500])
                raise AIServiceError("AI 服务返回非 JSON 响应。")
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as exc:
                logger.exception("解析 AI 响应失败: %s", data)
                raise AIServiceError("解析 AI 响应失败。") from exc

