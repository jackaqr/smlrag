#!/bin/bash

# 启动 scan 服务的快捷脚本

echo "==================================="
echo "  启动 SMLRAG Scan 服务"
echo "==================================="

# 检查根目录的 .env 文件
if [ ! -f ../.env ]; then
    echo "❌ 错误: 未找到项目根目录的 .env 文件"
    echo "请在项目根目录（不是 scan 目录）创建 .env 文件并配置以下变量："
    echo ""
    echo "DIFY_BASE_URL=https://api.dify.ai/v1"
    echo "DIFY_API_KEY=your_api_key_here"
    echo ""
    exit 1
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  警告: 未安装 docker-compose"
    echo "将使用 docker 命令启动..."
    
    # 构建镜像
    echo "📦 构建 Docker 镜像..."
    docker build -t smlrag-scan .
    
    # 停止并删除旧容器
    docker stop smlrag-scan 2>/dev/null || true
    docker rm smlrag-scan 2>/dev/null || true
    
    # 运行容器
    echo "🚀 启动容器..."
    docker run -d \
        --name smlrag-scan \
        --env-file ../.env \
        -v "$(pwd)/data:/app/data" \
        --restart unless-stopped \
        smlrag-scan
else
    # 使用 docker-compose
    echo "🚀 使用 docker-compose 启动..."
    docker-compose up -d --build
fi

echo ""
echo "✅ 服务启动成功！"
echo ""
echo "查看日志:"
if command -v docker-compose &> /dev/null; then
    echo "  docker-compose logs -f"
else
    echo "  docker logs -f smlrag-scan"
fi
echo ""
echo "停止服务:"
if command -v docker-compose &> /dev/null; then
    echo "  docker-compose down"
else
    echo "  docker stop smlrag-scan"
fi
echo ""

