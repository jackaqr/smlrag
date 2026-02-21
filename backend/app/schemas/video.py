from typing import Optional

from pydantic import BaseModel, Field


class VideoCreateRequest(BaseModel):
    """提交视频生成任务的请求体。model 不传时使用 config 中的 VIDEO_MODEL。图生视频时传 image。"""

    model: Optional[str] = Field(default=None, description="视频生成模型，不传则用配置默认")
    prompt: str = Field(..., description="视频描述/提示词")
    aspect_ratio: str = Field(default="16:9", description="画面比例，如 16:9")
    seconds: int = Field(default=5, ge=1, le=60, description="视频时长（秒）")
    image: Optional[str] = Field(default=None, description="图生视频时传入，base64 或 URL，依即梦 API 要求")
