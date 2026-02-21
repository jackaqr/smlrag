from typing import List, Optional

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


# ========== OpenAI 兼容格式 ==========

class OpenAIChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class OpenAIChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[OpenAIChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


class OpenAIChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str


class OpenAIChoice(BaseModel):
    index: int = 0
    message: OpenAIChoiceMessage
    finish_reason: str = "stop"


class OpenAIUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class OpenAIChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    choices: List[OpenAIChoice]
    usage: Optional[OpenAIUsage] = None

