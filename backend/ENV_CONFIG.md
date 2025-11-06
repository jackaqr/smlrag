# 环境变量配置

## 文件扫描功能（可选）

如需使用文件扫描功能，请配置以下环境变量：

### Windows (PowerShell)

```powershell
$env:DIFY_BASE_URL = "https://api.dify.ai/v1"
$env:DIFY_API_KEY = "your_api_key_here"
```

### Linux/Mac (Bash)

```bash
export DIFY_BASE_URL=https://api.dify.ai/v1
export DIFY_API_KEY=your_api_key_here
```

### Docker Compose

在 `docker-compose.yml` 中添加：

```yaml
environment:
  - DIFY_BASE_URL=https://api.dify.ai/v1
  - DIFY_API_KEY=your_api_key_here
```

## 使用说明

1. 将待扫描的文件放入 `backend/data` 目录
2. 配置上述环境变量
3. 调用 `POST /api/scan` 接口触发扫描
4. 系统会自动上传所有文件到 Dify

