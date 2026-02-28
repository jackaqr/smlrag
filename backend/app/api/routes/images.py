import json
import logging

import aiohttp

from fastapi import APIRouter, HTTPException

from ...config import settings
from ...schemas.image import ImageCreateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["Images"])


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


@router.post("/generations")
async def create_image(request: ImageCreateRequest):
    """
    提交图片生成请求，转发至上游图片生成 API（如 aiping.cn）。
    请求体参数平铺，与 video 接口一致，支持 model、prompt、negative_prompt、image、extra_body 等。
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="未配置 OPENAI_API_KEY，无法调用图片生成服务。",
        )
    url = settings.image_api_url
    payload = request.model_dump(mode="json", exclude_none=True)
    if not payload.get("model"):
        payload["model"] = settings.image_model
    logger.info("给 aiping 发送请求: url=%s body=%s", url, payload)
    timeout = aiohttp.ClientTimeout(total=settings.openai_timeout)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=_headers(), json=payload) as response:
                text = await response.text()
                logger.info("收到 aiping 响应: status=%s body=%s", response.status, text or "(empty)")
                if response.content_type and "application/json" in response.content_type and text:
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        result = {"raw": text}
                else:
                    result = {"raw": text} if text else {}
                if response.status >= 400:
                    logger.warning("图片生成失败: status=%s body=%s", response.status, text)
                    raise HTTPException(
                        status_code=response.status,
                        detail=result if isinstance(result, dict) else {"message": text},
                    )
                return result
    except aiohttp.ClientError as e:
        logger.exception("请求图片 API 失败: %s", e)
        raise HTTPException(status_code=502, detail=f"请求图片服务失败: {e}") from e
