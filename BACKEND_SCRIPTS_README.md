# 服务管理脚本使用指南

## 📋 概述

本项目提供了便捷的脚本来管理前端和后端服务：

### 全栈服务管理（推荐）

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start_all.sh` | 🚀 一键启动所有服务 | 启动 PostgreSQL、Redis、后端 API (8000) 和前端 (5174) |
| `stop_all.sh` | 🛑 一键停止所有服务 | 优雅地停止所有前端和后端进程 |

### 后端服务管理

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start_backend_all.sh` | 一键启动所有后端服务 | 自动检查并启动 PostgreSQL、Redis 和后端 API 服务 |
| `stop_backend_all.sh` | 一键停止所有后端服务 | 优雅地停止所有后端相关进程 |
| `status_backend.sh` | 查看服务状态 | 显示所有服务的运行状态和健康检查信息 |

## 🚀 快速开始

### 方式一：启动所有服务（推荐）

**一键启动前端 + 后端所有服务：**

```bash
./start_all.sh
```

这个脚本会自动：
- ✅ 启动 PostgreSQL 数据库
- ✅ 启动 Redis 缓存服务
- ✅ 启动后端 API 服务（端口 8000）
- ✅ 启动前端开发服务器（端口 5174）
- ✅ 执行健康检查
- ✅ 显示所有服务状态

**停止所有服务：**

```bash
./stop_all.sh
```

### 方式二：仅启动后端服务

```bash
./start_backend_all.sh
```

**功能说明：**
- ✅ 自动检查并启动 PostgreSQL 数据库
- ✅ 自动检查并启动 Redis 缓存服务
- ✅ 检查 Python 虚拟环境
- ✅ 检查环境变量配置文件
- ✅ 清理旧的后端进程
- ✅ 启动后端 API 服务（端口 8000）
- ✅ 执行健康检查
- ✅ 显示服务状态总览

**输出示例：**
```
=========================================
后端服务一键启动脚本
=========================================

步骤 1/5: 检查 PostgreSQL 服务
[SUCCESS] postgresql@16-main.service 正在运行

步骤 2/5: 检查 Redis 服务
[SUCCESS] redis-server.service 正在运行

步骤 3/5: 检查后端环境
[SUCCESS] 虚拟环境检查通过
[SUCCESS] 环境变量文件检查通过

步骤 4/5: 清理旧进程
[SUCCESS] 后端进程清理完成

步骤 5/5: 启动后端服务
[INFO] 后端进程 PID: 12345
[SUCCESS] 后端服务启动成功！
[INFO] 健康检查: http://localhost:8000/health
[INFO] API 文档: http://localhost:8000/docs
[INFO] 日志文件: /tmp/backend_8000.log

=========================================
服务状态总览
=========================================

系统服务:
  ✓ PostgreSQL: 运行中
  ✓ Redis: 运行中

应用服务:
  ✓ 后端服务 (8000): 运行中

访问地址:
  - API 服务: http://localhost:8000
  - API 文档: http://localhost:8000/docs
  - 健康检查: http://localhost:8000/health

日志文件:
  - 后端日志: /tmp/backend_8000.log

=========================================
[SUCCESS] 所有服务启动完成！
```

### 2. 查看服务状态

```bash
./status_backend.sh
```

**功能说明：**
- 📊 显示系统服务状态（PostgreSQL、Redis）
- 📊 显示应用服务状态（后端 API）
- 📊 检查数据库连接
- 📊 检查 Redis 连接
- 📊 显示最近的日志
- 📊 显示访问地址和常用命令

**输出示例：**
```
=========================================
后端服务状态总览
=========================================

系统服务
  ✓ PostgreSQL: 运行中
    状态: Active: active (running) since ...
  ✓ Redis: 运行中
    状态: Active: active (running) since ...

应用服务
  ✓ 后端 API 服务 (端口 8000): 运行中
    PID: 12345
    命令: /var/www/packages/backend/venv/bin/python3 -m uvicorn src.main:app...
    健康检查: 通过
    服务状态: healthy

数据库连接
  ✓ PostgreSQL 连接: 正常
    数据库大小: 15 MB

Redis 连接
  ✓ Redis 连接: 正常
    版本: 7.0.15
    键数量: 42

访问地址
  API 服务:     http://localhost:8000
  API 文档:     http://localhost:8000/docs
  健康检查:     http://localhost:8000/health
  OpenAPI:      http://localhost:8000/api/v1/openapi.json

最近日志 (最后 10 行)
后端日志:
  INFO:     Started server process [12345]
  INFO:     Waiting for application startup.
  🚀 启动代理记账营运内部系统...
  ✅ Redis连接成功
  ✅ 缓存预热完成
  ✅ 事件处理器加载完成
  ✅ 系统启动完成
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8000

常用命令
  启动服务:     ./start_backend_all.sh
  停止服务:     ./stop_backend_all.sh
  查看日志:     tail -f /tmp/backend_8000.log
  重启服务:     ./stop_backend_all.sh && ./start_backend_all.sh

=========================================
状态检查完成
=========================================
```

### 3. 停止所有后端服务

```bash
./stop_backend_all.sh
```

**功能说明：**
- 🛑 优雅地停止后端 API 服务
- 🛑 清理所有相关进程
- 🛑 释放端口 8000
- 🛑 显示停止状态

**输出示例：**
```
=========================================
后端服务一键停止脚本
=========================================

[INFO] 停止后端服务...
[INFO] 发现占用端口 8000 的进程: 12345
[SUCCESS] 已停止端口 8000 的服务
[SUCCESS] 后端服务已停止

[SUCCESS] 所有后端服务已停止！

[SUCCESS] 端口 8000 已释放
```

## 📝 常见使用场景

### 场景 1: 开发环境启动

```bash
# 启动所有服务
./start_backend_all.sh

# 查看日志
tail -f /tmp/backend_8000.log

# 访问 API 文档
# 浏览器打开: http://localhost:8000/docs
```

### 场景 2: 重启服务

```bash
# 方式 1: 分步执行
./stop_backend_all.sh
./start_backend_all.sh

# 方式 2: 一行命令
./stop_backend_all.sh && ./start_backend_all.sh
```

### 场景 3: 检查服务状态

```bash
# 查看详细状态
./status_backend.sh

# 或者快速检查健康状态
curl http://localhost:8000/health
```

### 场景 4: 调试问题

```bash
# 1. 查看服务状态
./status_backend.sh

# 2. 查看实时日志
tail -f /tmp/backend_8000.log

# 3. 如果有问题，重启服务
./stop_backend_all.sh && ./start_backend_all.sh
```

## ⚙️ 配置说明

### 环境变量文件

首次使用前，需要配置 `.env` 文件：

```bash
cd /var/www/packages/backend

# 如果 .env 不存在，复制示例文件
cp .env.example .env

# 编辑配置
vim .env
```

**重要配置项：**

```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/proxy_db

# JWT 配置
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### 端口配置

- **后端 API**: 8000（固定，不可更改）
- **PostgreSQL**: 5432（默认）
- **Redis**: 6379（默认）

## 🔧 故障排除

### 问题 1: PostgreSQL 启动失败

**症状：**
```
[ERROR] PostgreSQL 启动失败，无法继续
```

**解决方案：**
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql@16-main.service

# 查看日志
sudo journalctl -u postgresql@16-main.service -n 50

# 手动启动
sudo systemctl start postgresql@16-main.service
```

### 问题 2: Redis 启动失败

**症状：**
```
[WARNING] Redis 启动失败，系统将在无缓存模式下运行
```

**解决方案：**
```bash
# 检查 Redis 状态
sudo systemctl status redis-server.service

# 手动启动
sudo systemctl start redis-server.service

# 注意: Redis 失败不会阻止后端启动，系统会降级为无缓存模式
```

### 问题 3: 端口 8000 被占用

**症状：**
```
[WARNING] 端口 8000 已被占用
```

**解决方案：**
```bash
# 查看占用端口的进程
lsof -i:8000

# 停止旧服务
./stop_backend_all.sh

# 或手动杀死进程
kill -9 $(lsof -ti:8000)
```

### 问题 4: 虚拟环境不存在

**症状：**
```
[ERROR] 虚拟环境不存在: /var/www/packages/backend/venv
```

**解决方案：**
```bash
cd /var/www/packages/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 问题 5: 健康检查失败

**症状：**
```
[ERROR] 后端服务启动失败或超时
```

**解决方案：**
```bash
# 查看日志
tail -f /tmp/backend_8000.log

# 常见原因:
# 1. 数据库连接失败 - 检查 DATABASE_URL
# 2. 依赖缺失 - 重新安装依赖
# 3. 代码错误 - 查看日志中的错误信息
```

## 📚 日志文件位置

| 服务 | 日志文件 | 查看命令 |
|------|---------|---------|
| 后端 API | `/tmp/backend_8000.log` | `tail -f /tmp/backend_8000.log` |
| PostgreSQL | 系统日志 | `sudo journalctl -u postgresql@16-main.service -f` |
| Redis | 系统日志 | `sudo journalctl -u redis-server.service -f` |

## 🔗 相关链接

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **OpenAPI 规范**: http://localhost:8000/api/v1/openapi.json

## 💡 提示

1. **首次使用**: 确保已配置 `.env` 文件
2. **开发模式**: 后端服务启用了热重载（`--reload`），代码修改会自动重启
3. **日志查看**: 使用 `tail -f /tmp/backend_8000.log` 实时查看日志
4. **服务依赖**: PostgreSQL 是必需的，Redis 是可选的（失败时降级为无缓存模式）
5. **权限问题**: 如果遇到权限问题，可能需要使用 `sudo` 启动系统服务

## 🎯 最佳实践

1. **每天开始工作前**: 运行 `./start_backend_all.sh` 启动所有服务
2. **遇到问题时**: 先运行 `./status_backend.sh` 检查状态
3. **修改代码后**: 不需要重启，热重载会自动生效
4. **下班前**: 运行 `./stop_backend_all.sh` 停止服务（可选）
5. **定期检查**: 使用 `./status_backend.sh` 监控服务健康状态

