import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from chat_history import chat_manager
from ...schemas.chat import (
    ChatMetadataResponse,
    CreateChatRequest,
    ImageResultRequest,
    MessageResponse,
    OpenAIChatCompletionRequest,
    OpenAIChatCompletionResponse,
    OpenAIChoice,
    OpenAIChoiceMessage,
    SendMessageRequest,
    UpdateChatTitleRequest,
    VideoResultRequest,
)
from ...services.ai import AIServiceError, generate_ai_reply

logger = logging.getLogger(__name__)

# 对话管理：/api/chats，消息路径为 /messages/{chat_id}（message 在前，chat_id 在后）
chats_router = APIRouter(prefix="/api/chats", tags=["Chat"])

# OpenAI 标准：/api/chat/completions
completions_router = APIRouter(prefix="/api/chat/completions", tags=["ChatCompletion"])


# ========== 对话 CRUD（chats_router）==========

@chats_router.get("", response_model=List[ChatMetadataResponse])
async def get_all_chats():
    """获取所有对话列表"""
    chats = chat_manager.get_all_chats()
    return [chat.to_dict() for chat in chats]


@chats_router.post("", response_model=ChatMetadataResponse)
async def create_chat(chat_id: str, request: CreateChatRequest):
    """创建新对话"""
    if chat_manager.get_chat_metadata(chat_id):
        raise HTTPException(status_code=400, detail="对话ID已存在")
    metadata = chat_manager.create_chat(chat_id, request.title)
    return metadata.to_dict()


@chats_router.get("/{chat_id}", response_model=ChatMetadataResponse)
async def get_chat_metadata(chat_id: str):
    """获取对话元数据"""
    metadata = chat_manager.get_chat_metadata(chat_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="对话不存在")
    return metadata.to_dict()


@chats_router.put("/{chat_id}/title")
async def update_chat_title(chat_id: str, request: UpdateChatTitleRequest):
    """更新对话标题"""
    success = chat_manager.update_chat_title(chat_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "标题已更新"}


@chats_router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    """删除对话"""
    success = chat_manager.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "对话已删除"}


# ========== 消息：路径为 /messages/{chat_id} ==========

@chats_router.get("/messages/{chat_id}", response_model=List[MessageResponse])
async def get_messages(chat_id: str, limit: Optional[int] = None):
    """获取对话消息列表"""
    messages = chat_manager.get_messages(chat_id, limit)
    return [msg.to_dict() for msg in messages]


@chats_router.post("/messages/{chat_id}/video-result", response_model=MessageResponse)
async def add_video_result(chat_id: str, request: VideoResultRequest):
    """将视频生成结果写入对话历史：先添加用户消息，再添加助手消息（内容为 video_url）"""
    chat_manager.add_message(
        chat_id=chat_id,
        role="user",
        content=request.user_content,
    )
    assistant_message = chat_manager.add_message(
        chat_id=chat_id,
        role="assistant",
        content=request.video_url,
    )
    return assistant_message.to_dict()


@chats_router.post("/messages/{chat_id}/image-result", response_model=MessageResponse)
async def add_image_result(chat_id: str, request: ImageResultRequest):
    """将图片生成结果写入对话历史：先添加用户消息，再添加助手消息（内容为 image_url）"""
    chat_manager.add_message(
        chat_id=chat_id,
        role="user",
        content=request.user_content,
    )
    assistant_message = chat_manager.add_message(
        chat_id=chat_id,
        role="assistant",
        content=request.image_url,
    )
    return assistant_message.to_dict()


@chats_router.post("/messages/{chat_id}", response_model=MessageResponse)
async def send_message(chat_id: str, request: SendMessageRequest):
    """发送消息并获取 AI 回复"""
    chat_manager.add_message(
        chat_id=chat_id,
        role="user",
        content=request.content,
    )
    try:
        ai_response = await generate_ai_reply(
            chat_manager.get_messages(chat_id), model=request.model
        )
    except AIServiceError as exc:
        logger.warning("AI 服务调用失败，将使用回声回复: %s", exc)
        ai_response = f"收到您的消息: {request.content}"
    assistant_message = chat_manager.add_message(
        chat_id=chat_id,
        role="assistant",
        content=ai_response,
    )
    return assistant_message.to_dict()


# ========== OpenAI 标准格式（completions_router）==========

@completions_router.post("", response_model=OpenAIChatCompletionResponse)
async def chat_completions(request: OpenAIChatCompletionRequest):
    """
    OpenAI 标准 Chat Completions 接口。
    请求体：{ "model": "...", "messages": [ {"role":"user","content":"..."} ] }
    响应体：{ "id", "choices": [ { "message": { "role", "content" }, "finish_reason" } ], "usage" }
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages 不能为空")
    # 转成内部 Message 格式调用 AI
    from chat_history import Message
    history = [
        Message(role=m.role, content=m.content, timestamp="")
        for m in request.messages
    ]
    try:
        content = await generate_ai_reply(history)
    except AIServiceError as exc:
        logger.warning("AI 服务调用失败: %s", exc)
        content = "服务暂时不可用，请稍后重试。"
    import time
    resp_id = f"chatcmpl-{int(time.time() * 1000)}"
    return OpenAIChatCompletionResponse(
        id=resp_id,
        choices=[
            OpenAIChoice(
                message=OpenAIChoiceMessage(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
        usage=None,
    )
