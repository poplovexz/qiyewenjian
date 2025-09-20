# 代理记账营运内部系统 - 后端

基于 FastAPI 的后端服务，提供代理记账系统的 API 接口。

## 🚀 快速开始（推荐）

**使用模块化结构**：
```bash
cd packages/backend
source venv/bin/activate
python3 run_server.py
```

详细说明请参考 [README_SIMPLE.md](README_SIMPLE.md)。

## 技术栈

- FastAPI (Python 3.11)
- PostgreSQL + SQLAlchemy ORM
- JWT 认证
- Alembic 数据库迁移
- Pytest 测试

## 安装与运行

```bash
# 安装依赖
poetry install

# 初始化数据库
poetry run python src/init_db.py

# 启动开发服务器
poetry run uvicorn src.main:app --reload --port 8000
```

## 环境变量

复制 `.env.example` 到 `.env` 并配置：

```
DATABASE_URL=postgresql://user:password@localhost/proxy_db
JWT_SECRET=your-secret-key
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## Redis 连接验证

项目在无法连接 Redis 时会自动降级为无缓存模式，并通过日志输出告警。建议在部署或开发环境下手动验证配置：

```bash
poetry run python -m src.scripts.verify_redis
```

该脚本会尝试建立连接并执行一次缓存预热，便于确认 Redis 服务和凭据是否正确。

## 测试

```bash
poetry run pytest
```
