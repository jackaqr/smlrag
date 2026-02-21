import logging
from typing import Iterable, List

import aiohttp

from chat_history import Message
from ..config import settings

logger = logging.getLogger(__name__)

MAX_MESSAGES = 20


class AIServiceError(Exception):
    """AI 服务调用异常"""


def _build_payload_messages(messages: Iterable[Message]) -> List[dict]:
    payload = []
    if settings.openai_system_prompt:
        payload.append({"role": "system", "content": settings.openai_system_prompt})

    payload.extend({"role": msg.role, "content": msg.content} for msg in messages)
    return payload


async def generate_ai_reply(
    messages: Iterable[Message], model: str | None = None
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

    payload_messages = _build_payload_messages(message_list[-MAX_MESSAGES:])

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

    timeout = aiohttp.ClientTimeout(total=settings.openai_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise AIServiceError(
                    f"AI 服务返回错误状态码 {response.status}: {error_text}"
                )

            data = await response.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as exc:
                logger.exception("解析 AI 响应失败: %s", data)
                raise AIServiceError("解析 AI 响应失败。") from exc

