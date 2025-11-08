"""
应用入口：仅负责创建并启动 FastAPI 应用
"""
from app import create_app

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5301)

