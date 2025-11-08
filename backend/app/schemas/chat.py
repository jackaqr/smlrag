from typing import Optional

from pydantic import BaseModel


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

