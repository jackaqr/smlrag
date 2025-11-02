"""
聊天后端服务 - FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from chat_history import chat_manager, Message, ChatMetadata

app = FastAPI(title="Smlrag Chat API", version="1.0.0")

# CORS 配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 请求/响应模型 ==========

class CreateChatRequest(BaseModel):
    title: str = "新对话"


class SendMessageRequest(BaseModel):
    content: str


class UpdateChatTitleRequest(BaseModel):
    title: str


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatMetadataResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


# ========== API 端点 ==========

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "service": "Smlrag Chat API"}


@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    return chat_manager.get_stats()


@app.get("/api/chats", response_model=List[ChatMetadataResponse])
async def get_all_chats():
    """获取所有对话列表"""
    chats = chat_manager.get_all_chats()
    return [chat.to_dict() for chat in chats]


@app.post("/api/chats", response_model=ChatMetadataResponse)
async def create_chat(chat_id: str, request: CreateChatRequest):
    """创建新对话"""
    # 检查是否已存在
    if chat_manager.get_chat_metadata(chat_id):
        raise HTTPException(status_code=400, detail="对话ID已存在")
    
    metadata = chat_manager.create_chat(chat_id, request.title)
    return metadata.to_dict()


@app.get("/api/chats/{chat_id}", response_model=ChatMetadataResponse)
async def get_chat_metadata(chat_id: str):
    """获取对话元数据"""
    metadata = chat_manager.get_chat_metadata(chat_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="对话不存在")
    return metadata.to_dict()


@app.get("/api/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: str, limit: Optional[int] = None):
    """获取对话消息列表"""
    messages = chat_manager.get_messages(chat_id, limit)
    return [msg.to_dict() for msg in messages]


@app.post("/api/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message(chat_id: str, request: SendMessageRequest):
    """
    发送消息并获取AI回复
    这里简化处理，实际应该调用AI服务
    """
    # 保存用户消息
    user_message = chat_manager.add_message(
        chat_id=chat_id,
        role="user",
        content=request.content
    )
    
    # TODO: 调用AI服务获取回复
    # 这里先用简单的回声作为演示
    ai_response = f"收到您的消息: {request.content}"
    
    # 保存AI回复
    assistant_message = chat_manager.add_message(
        chat_id=chat_id,
        role="assistant",
        content=ai_response
    )
    
    return assistant_message.to_dict()


@app.put("/api/chats/{chat_id}/title")
async def update_chat_title(chat_id: str, request: UpdateChatTitleRequest):
    """更新对话标题"""
    success = chat_manager.update_chat_title(chat_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "标题已更新"}


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """删除对话"""
    success = chat_manager.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "ok", "message": "对话已删除"}


@app.post("/api/admin/clear")
async def clear_all_data():
    """清除所有数据（管理接口）"""
    chat_manager.clear_all()
    return {"status": "ok", "message": "所有数据已清除"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

