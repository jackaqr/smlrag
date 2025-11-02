# PowerShell 启动脚本（Windows）

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  启动 SMLRAG Scan 服务" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# 检查根目录的 .env 文件
if (-not (Test-Path ../.env)) {
    Write-Host "❌ 错误: 未找到项目根目录的 .env 文件" -ForegroundColor Red
    Write-Host ""
    Write-Host "请在项目根目录（不是 scan 目录）创建 .env 文件并配置以下变量：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "DIFY_BASE_URL=https://api.dify.ai/v1"
    Write-Host "DIFY_API_KEY=your_api_key_here"
    Write-Host ""
    exit 1
}

# 检查 Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ 错误: 未安装 Docker" -ForegroundColor Red
    Write-Host "请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# 检查 docker-compose
try {
    docker-compose --version | Out-Null
    $useCompose = $true
} catch {
    Write-Host "⚠️  警告: 未安装 docker-compose，将使用 docker 命令" -ForegroundColor Yellow
    $useCompose = $false
}

if ($useCompose) {
    # 使用 docker-compose
    Write-Host "🚀 使用 docker-compose 启动..." -ForegroundColor Green
    docker-compose up -d --build
} else {
    # 使用 docker 命令
    Write-Host "📦 构建 Docker 镜像..." -ForegroundColor Green
    docker build -t smlrag-scan .
    
    # 停止并删除旧容器
    docker stop smlrag-scan 2>$null
    docker rm smlrag-scan 2>$null
    
    # 运行容器
    Write-Host "🚀 启动容器..." -ForegroundColor Green
    docker run -d `
        --name smlrag-scan `
        --env-file ../.env `
        -v "${PWD}/data:/app/data" `
        --restart unless-stopped `
        smlrag-scan
}

Write-Host ""
Write-Host "✅ 服务启动成功！" -ForegroundColor Green
Write-Host ""
Write-Host "查看日志:" -ForegroundColor Cyan
if ($useCompose) {
    Write-Host "  docker-compose logs -f"
} else {
    Write-Host "  docker logs -f smlrag-scan"
}
Write-Host ""
Write-Host "停止服务:" -ForegroundColor Cyan
if ($useCompose) {
    Write-Host "  docker-compose down"
} else {
    Write-Host "  docker stop smlrag-scan"
}
Write-Host ""

