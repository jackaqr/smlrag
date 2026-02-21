"""配置 API 的请求/响应 schema"""
from typing import Any

from pydantic import BaseModel, Field


class ConfigResponse(BaseModel):
    """GET /api/config 返回：模型配置 + 界面设置"""
    model: dict[str, Any] = Field(default_factory=dict, description="模型配置（各模态默认模型、参数等）")
    ui: dict[str, Any] = Field(default_factory=dict, description="界面设置")


class ConfigUpdateRequest(BaseModel):
    """PUT /api/config 请求体：只传需要更新的部分，与现有配置合并"""
    model: dict[str, Any] | None = Field(default=None, description="模型配置，不传则不更新")
    ui: dict[str, Any] | None = Field(default=None, description="界面设置，不传则不更新")
