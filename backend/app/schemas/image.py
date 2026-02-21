from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImageCreateRequest(BaseModel):
    """图片生成请求体。支持任意平铺参数，原样转发至上游 API（与 video 接口方式一致）。"""

    model_config = ConfigDict(extra="allow")

    model: Optional[str] = Field(default=None, description="图片生成模型，不传则用配置默认")
    prompt: str = Field(..., description="图片描述/提示词")
    negative_prompt: Optional[str] = Field(default=None, description="负向提示词")
    image: Optional[str] = Field(default=None, description="图生图时传入，URL 或 base64")
