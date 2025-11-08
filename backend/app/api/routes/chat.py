import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from chat_history import chat_manager
from ...schemas.chat import (
    ChatMetadataResponse,
    CreateChatRequest,
    MessageResponse,
    SendMessageRequest,
    UpdateChatTitleRequest,
)
from ...services.ai import AIServiceError, generate_ai_reply

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chats", tags=["Chat"])


@router.get("", response_model=List[ChatMetadataResponse])
async def get_all_chats():
    """获取所有对话列表"""
    chats = chat_manager.get_all_chats()
    return [chat.to_dict() for chat in chats]


@router.post("", response_model=ChatMetadataResponse)
async def create_chat(chat_id: str, request: CreateChatRequest):
    """创建新对话"""
    if chat_manager.get_chat_metadata(chat_id):
        raise HTTPException(status_code=400, detail="对话ID已存在")

    metadata = chat_manager.create_chat(chat_id, request.title)
    return metadata.to_dict()


@router.get("/{chat_id}", response_model=ChatMetadataResponse)
async def get_chat_metadata(chat_id: str):
    """获取对话元数据"""
    metadata = chat_manager.get_chat_metadata(chat_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="对话不存在")
    return metadata.to_dict()


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: str, limit: Optional[int] = None):
    """获取对话消息列表"""
    messages = chat_manager.get_messages(chat_id, limit)
    return [msg.to_dict() for msg in messages]


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(chat_id: str, request: SendMessageRequest):
    """发送消息并获取 AI 回复"""
    chat_manager.add_message(
        chat_id=chat_id,
        role="user",
        content=request.content,
    )

    try:
        ai_response = await generate_ai_reply(chat_manager.get_messages(chat_id))
    except AIServiceError as exc:
        logger.warning("AI 服务调用失败，将使用回声回复: %s", exc)
        ai_response = f"收到您的消息: {request.content}"

    assistant_message = chat_manager.add_message(
        chat_id=chat_id,
        role="assistant",
        content=ai_response,
    )

    return assistant_message.to_dict()


@router.put("/{chat_id}/title")
async def update_chat_title(chat_id: str, request: UpdateChatTitleRequest):
    """更新对话标题"""
    success = chat_manager.update_chat_title(chat_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "标题已更新"}


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    """删除对话"""
    success = chat_manager.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "对话已删除"}

