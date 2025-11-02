# Smlrag 聊天后端服务

轻量级的聊天历史管理后端，使用纯内存存储。

## 特性

✅ **内存存储** - 数据保存在进程内存中  
✅ **自动清除** - 重启容器/服务后数据自动清空  
✅ **省内存** - 每个对话最多保存100条消息  
✅ **RESTful API** - 标准的 HTTP 接口  
✅ **CORS 支持** - 前端可直接调用  

## 快速启动

### 方式 1: Docker Compose（推荐）

```bash
cd backend
docker-compose up -d
```

服务将在 `http://localhost:8000` 启动

### 方式 2: 本地运行

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## API 接口

### 基础接口

- `GET /` - 健康检查
- `GET /api/stats` - 获取统计信息

### 对话管理

- `GET /api/chats` - 获取所有对话列表
- `POST /api/chats?chat_id={id}` - 创建新对话
- `GET /api/chats/{chat_id}` - 获取对话元数据
- `DELETE /api/chats/{chat_id}` - 删除对话
- `PUT /api/chats/{chat_id}/title` - 更新对话标题

### 消息管理

- `GET /api/chats/{chat_id}/messages` - 获取对话消息
- `POST /api/chats/{chat_id}/messages` - 发送消息

### 管理接口

- `POST /api/admin/clear` - 清除所有数据

## API 文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 示例

### 创建对话

```bash
curl -X POST "http://localhost:8000/api/chats?chat_id=chat123" \
  -H "Content-Type: application/json" \
  -d '{"title": "我的第一个对话"}'
```

### 发送消息

```bash
curl -X POST "http://localhost:8000/api/chats/chat123/messages" \
  -H "Content-Type: application/json" \
  -d '{"content": "你好！"}'
```

### 获取消息历史

```bash
curl "http://localhost:8000/api/chats/chat123/messages"
```

## 配置

在 `chat_history.py` 中可以修改：

- `max_messages_per_chat` - 每个对话最多保存的消息数量（默认100）

## 数据存储说明

- 数据仅存储在进程内存中
- 重启服务或容器后，所有数据自动清除
- 不依赖任何数据库
- 适合开发和测试环境使用

## 生产环境建议

如果需要持久化存储，建议：

1. 使用 Redis 替代内存存储
2. 使用 PostgreSQL/MySQL 数据库
3. 添加身份验证和授权
4. 限制 CORS 允许的域名

