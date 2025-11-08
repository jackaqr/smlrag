from fastapi import APIRouter

from chat_history import chat_manager

router = APIRouter()


@router.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "service": "Smlrag API", "modules": ["chat", "scan"]}


@router.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    return chat_manager.get_stats()

