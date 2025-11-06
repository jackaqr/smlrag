#!/bin/bash

echo "启动 Smlrag 聊天后端服务..."

# 检查是否安装了依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 启动服务
echo "服务启动在 http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

