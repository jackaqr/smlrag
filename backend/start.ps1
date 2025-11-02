# Windows PowerShell 启动脚本

Write-Host "启动 Smlrag 聊天后端服务..." -ForegroundColor Green

# 检查是否安装了依赖
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    .\venv\Scripts\Activate.ps1
}

# 启动服务
Write-Host "服务启动在 http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

