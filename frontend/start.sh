#!/bin/bash
# 无论从哪个目录执行，都切换到脚本所在目录（frontend）再运行
cd "$(dirname "$0")"

echo "启动 Smlrag 前端开发服务..."

if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

echo "开发服务器: http://localhost:5173"
npm run dev
