import os
from typing import List


OPENAI_API_KEY = "QC-6d1572adcf49ed77911d01be083e7fd8-db064c3d3b4fce728350b6874ea9b880"
OPENAI_BASE_URL = "https://aiping.cn/api/v1"

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

        self.openai_model = os.getenv("OPENAI_MODEL", "DeepSeek-V3.1")
        self.openai_timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))
        self.openai_system_prompt = os.getenv(
            "OPENAI_SYSTEM_PROMPT", "你是一名乐于助人的 AI 助手。"
        )


settings = Settings()

