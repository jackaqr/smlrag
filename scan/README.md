# Scan 服务

文件扫描和上传服务，用于自动扫描指定目录的文件并上传到 Dify。

## 快速开始

### 1. 配置环境变量

在**项目根目录**（不是 scan 目录）创建 `.env` 文件并填写配置：

```bash
cd ..  # 回到项目根目录
# 如果已有 .env.example，可以复制
cp .env.example .env
```

编辑根目录的 `.env` 文件，添加 Dify API 配置：
```env
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=your_actual_api_key
```

**注意**：所有服务的环境变量统一在根目录的 `.env` 文件中管理。

### 2. 使用 Docker Compose 启动（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 使用 Docker 命令启动

```bash
# 在 scan 目录下执行
cd scan

# 构建镜像
docker build -t smlrag-scan .

# 运行容器（注意 env-file 路径指向根目录）
docker run -d \
  --name smlrag-scan \
  --env-file ../.env \
  -v $(pwd)/data:/app/data \
  smlrag-scan

# 查看日志
docker logs -f smlrag-scan

# 停止容器
docker stop smlrag-scan
docker rm smlrag-scan
```

## 目录结构

```
项目根目录/
├── .env                # 环境变量配置（所有服务共用）
├── .env.example        # 环境变量示例
└── scan/
    ├── Dockerfile           # Docker 镜像定义
    ├── docker-compose.yml   # Docker Compose 配置
    ├── requirements.txt     # Python 依赖
    ├── scan.py             # 扫描服务主程序
    ├── upload.py           # 文件上传模块
    ├── data/               # 待扫描的文件目录（挂载）
    └── README.md           # 本文件
```

## 功能说明

- 自动扫描 `data` 目录下的所有文件
- 将文件上传到 Dify 数据集
- 支持容器化部署
- 支持自动重启

## 开发模式

如果需要在开发时热重载代码，可以在 `docker-compose.yml` 中取消注释代码挂载部分：

```yaml
volumes:
  - ./data:/app/data
  - ./scan.py:/app/scan.py      # 取消注释
  - ./upload.py:/app/upload.py  # 取消注释
```

## 注意事项

1. **环境变量**：所有服务统一使用项目根目录的 `.env` 文件，不要在 scan 目录下创建单独的 `.env`
2. **数据目录**：`data` 目录会被挂载到容器中，请将需要扫描的文件放入此目录
3. **自动重启**：服务会自动重启（除非手动停止）
4. **Git 安全**：确保 `.env` 文件不要提交到 Git（已在 .gitignore 中配置）

