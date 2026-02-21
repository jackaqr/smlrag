import os
from typing import Dict, List


OPENAI_API_KEY = "QC-6d1572adcf49ed77911d01be083e7fd8-db064c3d3b4fce728350b6874ea9b880"
OPENAI_BASE_URL = "https://aiping.cn/api/v1"

# 各模态支持的模型列表（key: 文本生成 / 图片生成 / 视频生成）
DEFAULT_MODALITY_MODELS: Dict[str, List[str]] = {
    "text": ["GLM-5"],
    "image": [],
    "video": ["即梦视频生成 3.0 Pro"],
}


class Settings:
    """应用配置，集中管理环境变量读取逻辑"""

    def __init__(self) -> None:
        self.app_title = os.getenv("APP_TITLE", "Smlrag API")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")

        cors_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
        self.cors_allow_origins: List[str] = [
            origin.strip() for origin in cors_origins.split(",")
        ] if cors_origins else ["*"]

        self.openai_api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        base_url = os.getenv("OPENAI_BASE_URL", OPENAI_BASE_URL)
        self.openai_base_url = base_url.rstrip("/")

        self.openai_model = os.getenv("OPENAI_MODEL", "GLM-5")
        self.openai_timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))
        self.openai_system_prompt = os.getenv(
            "OPENAI_SYSTEM_PROMPT", "你是一名乐于助人的 AI 助手。"
        )

        # 视频生成 API（即梦等），配置完整 URL，不含尾部 /
        default_video_api_url = f"{OPENAI_BASE_URL.rstrip('/')}/videos"
        self.video_api_url = os.getenv("VIDEO_API_URL", default_video_api_url).rstrip("/")
        self.video_model = os.getenv("VIDEO_MODEL", "即梦视频生成 3.0 Pro")

        # 各模态支持的模型：文本生成 / 图片生成 / 视频生成
        self.modality_models: Dict[str, List[str]] = {
            "text": _parse_model_list(os.getenv("MODELS_TEXT", "GLM-5")),
            "image": _parse_model_list(os.getenv("MODELS_IMAGE", "")),
            "video": _parse_model_list(os.getenv("MODELS_VIDEO", "即梦视频生成 3.0 Pro")),
        }


def _parse_model_list(value: str) -> List[str]:
    """将逗号分隔的字符串解析为模型列表，空字符串返回 []"""
    if not value or not value.strip():
        return []
    return [m.strip() for m in value.split(",") if m.strip()]


settings = Settings()

