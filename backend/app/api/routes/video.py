import json
import logging

import aiohttp

from fastapi import APIRouter, HTTPException

from ...config import settings
from ...schemas.video import VideoCreateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["Video"])


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


@router.post("")
async def create_video_task(request: VideoCreateRequest):
    """
    提交视频生成任务，请求即梦视频生成 API。
    返回任务 id、status、model 等，可用于后续轮询结果。
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="未配置 OPENAI_API_KEY，无法调用视频生成服务。",
        )
    url = settings.video_api_url
    payload = {
        "model": request.model or settings.video_model,
        "prompt": request.prompt,
        "aspect_ratio": request.aspect_ratio,
        "seconds": request.seconds,
    }
    if request.image is not None:
        payload["image"] = request.image
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
                    logger.warning("视频任务提交失败: status=%s body=%s", response.status, text)
                    raise HTTPException(
                        status_code=response.status,
                        detail=result if isinstance(result, dict) else {"message": text},
                    )
                return result
    except aiohttp.ClientError as e:
        logger.exception("请求视频 API 失败: %s", e)
        raise HTTPException(status_code=502, detail=f"请求视频服务失败: {e}") from e


@router.get("/{task_id}")
async def get_video_task_result(task_id: str, provider: str | None = None):
    """
    根据任务 ID 查询视频生成结果。
    状态：queued / in_progress / completed / failed。
    完成时响应含 video_url；失败时含 error。
    可选 Query：provider（如 火山方舟）加快查询。
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="未配置 OPENAI_API_KEY，无法调用视频生成服务。",
        )
    url = f"{settings.video_api_url}/{task_id}"
    params = {"provider": provider} if provider else None
    logger.info("给 aiping 发送请求: url=%s params=%s", url, params)
    timeout = aiohttp.ClientTimeout(total=settings.openai_timeout)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=_headers(), params=params) as response:
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
                    logger.warning("查询视频任务失败: task_id=%s status=%s body=%s", task_id, response.status, text)
                    raise HTTPException(
                        status_code=response.status,
                        detail=result if isinstance(result, dict) else {"message": text},
                    )
                return result
    except aiohttp.ClientError as e:
        logger.exception("请求视频 API 失败: %s", e)
        raise HTTPException(status_code=502, detail=f"请求视频服务失败: {e}") from e
