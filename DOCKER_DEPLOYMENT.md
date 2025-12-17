# Docker 部署指南

## 📦 快速开始

### 前提条件

- Docker 20.10+
- Docker Compose 2.0+

### 一键启动

```bash
# 开发环境 (热重载)
./docker-start.sh dev

# 生产环境
./docker-start.sh prod

# 停止服务
./docker-start.sh stop

# 查看日志
./docker-start.sh logs
./docker-start.sh logs backend
```

---

## 🛠️ 手动操作

### 开发环境

```bash
# 启动
docker compose -f docker-compose.dev.yml up -d --build

# 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 停止
docker compose -f docker-compose.dev.yml down
```

**开发环境特性:**
- 前端热重载 (Vite HMR) - http://localhost:5173
- 后端热重载 (uvicorn --reload) - http://localhost:8000
- 源代码挂载，修改即生效

### 生产环境

```bash
# 1. 创建环境配置
cp .env.example .env
# 编辑 .env 修改密码和密钥

# 2. 构建并启动
docker compose up -d --build

# 3. 查看状态
docker compose ps

# 4. 查看日志
docker compose logs -f
```

---

## 📁 文件结构

```
/var/www/
├── docker-compose.yml          # 生产环境编排
├── docker-compose.dev.yml      # 开发环境编排
├── docker-start.sh             # 一键启动脚本
├── .env.example                # 环境变量模板
├── .dockerignore               # Docker 构建忽略
│
├── packages/backend/
│   ├── Dockerfile              # 后端生产镜像
│   ├── Dockerfile.dev          # 后端开发镜像
│   ├── .dockerignore
│   └── requirements.txt
│
└── packages/frontend/
    ├── Dockerfile              # 前端生产镜像
    ├── Dockerfile.dev          # 前端开发镜像
    ├── nginx.conf              # Nginx 配置
    └── .dockerignore
```

---

## 🌐 服务端口

| 服务 | 开发环境 | 生产环境 |
|------|----------|----------|
| 前端 | 5173 | 80 |
| 后端 API | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |

---

## 🔧 常用命令

```bash
# 重建单个服务
docker compose build backend
docker compose up -d backend

# 进入容器
docker compose exec backend bash
docker compose exec postgres psql -U proxy_user -d proxy_db

# 查看资源使用
docker stats

# 清理未使用资源
docker system prune -a
```

---

## ⚠️ 生产部署注意事项

1. **修改密码**: 编辑 `.env` 中的数据库密码和 SECRET_KEY
2. **HTTPS**: 建议在前端 Nginx 配置 SSL 或使用反向代理
3. **备份**: 定期备份 postgres_data 和 uploads_data 卷
4. **监控**: 配置健康检查告警

---

## 🔗 Windows Docker Desktop + WSL

如果在 WSL 中开发，Windows 上安装 Docker Desktop：

1. 安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 启用 WSL 2 集成 (Settings → Resources → WSL Integration)
3. 在 WSL 中直接使用 `docker` 命令

