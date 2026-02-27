# Windows PowerShell 启动脚本
# 无论从哪个目录执行，都切换到脚本所在目录（frontend）再运行
Set-Location $PSScriptRoot

Write-Host "启动 Smlrag 前端开发服务..." -ForegroundColor Green

if (-not (Test-Path "node_modules")) {
    Write-Host "安装依赖..." -ForegroundColor Yellow
    npm install
}

Write-Host "开发服务器: http://localhost:5173" -ForegroundColor Cyan
npm run dev
