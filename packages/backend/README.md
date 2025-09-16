# 代理记账营运内部系统 - 后端

基于 FastAPI 的后端服务，提供代理记账系统的 API 接口。

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
```

## 测试

```bash
poetry run pytest
```
