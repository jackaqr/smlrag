# 快速启动指南

## 🚀 启动服务

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 **http://localhost:5301** 启动

### 3. 验证服务

访问 http://localhost:5301 查看健康状态：

```json
{
  "status": "ok",
  "service": "Smlrag API",
  "modules": ["chat", "scan"]
}
```

## 📖 API 文档

启动后访问交互式 API 文档：
- **Swagger UI**: http://localhost:5301/docs
- **ReDoc**: http://localhost:5301/redoc

## 💬 聊天功能测试

```bash
# 1. 创建对话
curl -X POST "http://localhost:5301/api/chats?chat_id=test123" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试对话"}'

# 2. 发送消息
curl -X POST "http://localhost:5301/api/chats/test123/messages" \
  -H "Content-Type: application/json" \
  -d '{"content": "你好"}'

# 3. 获取消息历史
curl "http://localhost:5301/api/chats/test123/messages"

# 4. 获取所有对话
curl "http://localhost:5301/api/chats"
```

## 📁 文件扫描功能测试

### 配置环境变量

**Windows (PowerShell):**
```powershell
$env:DIFY_BASE_URL = "https://api.dify.ai/v1"
$env:DIFY_API_KEY = "your_api_key_here"
```

**Linux/Mac:**
```bash
export DIFY_BASE_URL=https://api.dify.ai/v1
export DIFY_API_KEY=your_api_key_here
```

### 使用扫描功能

```bash
# 1. 将文件放入 backend/data 目录
echo "测试内容" > data/test.txt

# 2. 触发扫描
curl -X POST "http://localhost:5301/api/scan"

# 响应示例：
# {
#   "status": "ok",
#   "message": "扫描完成",
#   "files_processed": 1
# }
```

## 🧪 运行测试

### 测试聊天功能
```bash
python test_api.py
```

### 测试扫描功能
```bash
python test_scan.py
```

## 🐳 Docker 部署

```bash
docker-compose up -d
```

## 📝 注意事项

- ⚠️ 聊天数据存储在内存中，重启服务后数据会清空
- ⚠️ 每个对话最多保存 100 条消息
- ⚠️ 文件扫描功能需要配置 Dify API 凭证
- ⚠️ 仅适用于开发和测试环境

## 🔗 相关链接

- [完整 README](README.md)
- [环境变量配置](ENV_CONFIG.md)
- [Dify API 文档](https://docs.dify.ai/)

