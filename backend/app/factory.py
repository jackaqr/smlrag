import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from .config import settings
from .api.routes import router as api_router

logger = logging.getLogger(__name__)


async def log_raw_request_middleware(request: Request, call_next):
    """记录接收到的完整原始请求与响应：URL、请求体；响应状态、体（单行、不含 headers）"""
    body = await request.body()
    full_url = str(request.url)
    method = request.method
    body_str = body.decode("utf-8", errors="replace") if body else "(empty)"
    if len(body_str) > 50000:
        body_str = body_str[:50000] + "...(truncated, total %d chars)" % len(body_str)
    logger.info("收到原始请求: method=%s url=%s body=%s", method, full_url, body_str)

    async def receive():
        return {"type": "http.request", "body": body}

    new_request = Request(request.scope, receive)
    response = await call_next(new_request)

    # 记录完整原始响应：状态码、响应体（单行、不含 headers）
    resp_body = b""
    async for chunk in response.body_iterator:
        resp_body += chunk
    resp_status = response.status_code
    resp_body_str = resp_body.decode("utf-8", errors="replace") if resp_body else "(empty)"
    if len(resp_body_str) > 50000:
        resp_body_str = resp_body_str[:50000] + "...(truncated, total %d chars)" % len(resp_body_str)
    logger.info("原始响应: status=%s body=%s", resp_status, resp_body_str)
    return Response(
        content=resp_body,
        status_code=resp_status,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


def create_app() -> FastAPI:
    """创建并返回 FastAPI 应用实例"""
    app = FastAPI(title=settings.app_title, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(log_raw_request_middleware)

    app.include_router(api_router)

    return app

