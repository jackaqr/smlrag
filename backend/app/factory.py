import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import router as api_router

logger = logging.getLogger(__name__)


async def log_raw_request_middleware(request: Request, call_next):
    """记录接收到的原始请求：方法、路径、查询串、请求体"""
    body = await request.body()
    path = request.url.path
    query = str(request.query_params) if request.query_params else ""
    method = request.method
    body_preview = body.decode("utf-8", errors="replace") if body else ""
    if len(body_preview) > 2000:
        body_preview = body_preview[:2000] + "...(truncated)"
    logger.info(
        "收到原始请求: method=%s path=%s query=%s body=%s",
        method,
        path,
        query or "(none)",
        body_preview or "(empty)",
    )

    async def receive():
        return {"type": "http.request", "body": body}

    new_request = Request(request.scope, receive)
    return await call_next(new_request)


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

