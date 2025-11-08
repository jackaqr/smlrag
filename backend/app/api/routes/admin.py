from fastapi import APIRouter

from chat_history import chat_manager

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/clear")
async def clear_all_data():
    """清除所有数据（管理接口）"""
    chat_manager.clear_all()
    return {"status": "ok", "message": "所有数据已清除"}

