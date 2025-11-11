# 部署指南

本文档整合了系统部署的完整指南。

## 目录

- [快速开始](#快速开始)
- [开发环境](#开发环境)
- [生产环境](#生产环境)
- [部署检查清单](#部署检查清单)
- [常见问题](#常见问题)

---

## 快速开始

### 一键启动脚本

系统提供了一键启动脚本，可以快速启动所有服务。

```bash
# 启动所有服务（前端 + 后端）
./start_all.sh

# 只启动后端
./start_backend.sh

# 只启动前端
./start_frontend.sh

# 停止所有服务
./stop_all.sh
```

详细说明参考：`一键启动脚本说明.md`

---

## 开发环境

### 环境要求

- **Node.js**: >= 18.0.0
- **Python**: >= 3.11
- **PostgreSQL**: >= 14
- **Redis**: >= 6.0
- **pnpm**: >= 8.0.0

### 安装步骤

1. **克隆代码**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **安装依赖**
```bash
# 安装前端依赖
pnpm install

# 安装后端依赖
cd packages/backend
poetry install
```

3. **配置环境变量**
```bash
# 复制环境变量模板
cp packages/backend/.env.example packages/backend/.env
cp packages/frontend/.env.example packages/frontend/.env

# 编辑环境变量
vim packages/backend/.env
vim packages/frontend/.env
```

4. **初始化数据库**
```bash
cd packages/backend
poetry run alembic upgrade head
```

5. **启动服务**
```bash
# 开发模式启动所有服务
pnpm dev

# 或使用一键启动脚本
./start_all.sh
```

### 开发环境配置

**后端配置** (`packages/backend/.env`)：
```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务端口
PORT=8000
```

**前端配置** (`packages/frontend/.env.development`)：
```env
# API地址
VITE_API_BASE_URL=http://localhost:8000

# 前端端口
VITE_PORT=5174
```

### 端口配置

⚠️ **重要**：系统使用固定端口，不要修改

- **后端服务**: 8000
- **前端服务**: 5174

---

## 生产环境

### 部署方式

系统支持多种部署方式：

1. **快速部署**：使用 `quick-deploy.sh` 脚本
2. **企业部署**：使用 `enterprise-deploy.sh` 脚本
3. **手动部署**：按照下面的步骤手动部署

### 快速部署

```bash
# 执行快速部署脚本
./quick-deploy.sh
```

脚本会自动完成：
- ✅ 构建前端
- ✅ 构建后端
- ✅ 打包部署文件
- ✅ 生成部署报告

### 企业部署

```bash
# 执行企业部署脚本
./enterprise-deploy.sh
```

企业部署包含：
- ✅ 完整的健康检查
- ✅ 数据库迁移
- ✅ 服务重启
- ✅ 部署验证
- ✅ 回滚机制

### 手动部署步骤

#### 1. 构建前端

```bash
cd packages/frontend
pnpm build:prod
```

构建产物在 `packages/frontend/dist` 目录。

#### 2. 配置Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. 配置后端服务

使用systemd管理后端服务：

```ini
[Unit]
Description=Backend API Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/packages/backend
Environment="PATH=/var/www/packages/backend/.venv/bin"
ExecStart=/var/www/packages/backend/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable backend.service
sudo systemctl start backend.service
```

#### 4. 配置环境变量

生产环境配置 (`packages/backend/.env.production`)：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/production_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 日志级别
LOG_LEVEL=INFO

# CORS配置
ALLOWED_ORIGINS=https://your-domain.com
```

---

## 部署检查清单

部署前请确认以下事项：

### 环境检查
- [ ] 服务器环境满足要求
- [ ] 数据库已创建并配置
- [ ] Redis服务正常运行
- [ ] 域名DNS已配置
- [ ] SSL证书已配置（生产环境）

### 代码检查
- [ ] 代码已合并到主分支
- [ ] 所有测试通过
- [ ] 代码已经过审查
- [ ] 版本号已更新

### 配置检查
- [ ] 环境变量已正确配置
- [ ] 数据库连接正常
- [ ] Redis连接正常
- [ ] 文件上传路径已配置
- [ ] 日志路径已配置

### 安全检查
- [ ] 密钥已更换为生产密钥
- [ ] 调试模式已关闭
- [ ] CORS配置正确
- [ ] 敏感信息已移除
- [ ] 防火墙规则已配置

### 功能检查
- [ ] 用户登录功能正常
- [ ] 权限控制正常
- [ ] 核心业务功能正常
- [ ] 文件上传功能正常
- [ ] 通知功能正常

### 性能检查
- [ ] 数据库索引已优化
- [ ] 静态资源已压缩
- [ ] CDN已配置（如需要）
- [ ] 缓存策略已配置
- [ ] 数据库连接池已配置

### 监控检查
- [ ] 日志收集已配置
- [ ] 错误监控已配置
- [ ] 性能监控已配置
- [ ] 告警规则已配置

---

## 部署验证

部署完成后，执行以下验证：

### 1. 健康检查

```bash
# 检查后端健康状态
curl http://your-domain.com/api/health

# 检查前端访问
curl http://your-domain.com
```

### 2. 功能测试

- [ ] 访问首页
- [ ] 用户登录
- [ ] 创建线索
- [ ] 创建报价
- [ ] 生成合同
- [ ] 审核流程
- [ ] 文件上传

### 3. 性能测试

```bash
# 使用ab进行简单压测
ab -n 1000 -c 10 http://your-domain.com/api/health
```

---

## 常见问题

### 1. 前端无法访问后端API

**问题**：前端调用API返回CORS错误

**解决方案**：
- 检查后端CORS配置
- 确认前端API地址配置正确
- 检查Nginx代理配置

### 2. 数据库连接失败

**问题**：后端启动时数据库连接失败

**解决方案**：
- 检查数据库服务是否运行
- 确认数据库连接字符串正确
- 检查数据库用户权限
- 检查防火墙规则

### 3. Redis连接失败

**问题**：后端启动时Redis连接失败

**解决方案**：
- 检查Redis服务是否运行
- 确认Redis连接字符串正确
- 检查Redis密码配置
- 系统已实现Redis容错机制，连接失败不会影响启动

### 4. 静态文件404

**问题**：前端静态资源返回404

**解决方案**：
- 检查Nginx配置的root路径
- 确认前端构建产物存在
- 检查文件权限

### 5. 服务启动后立即退出

**问题**：systemd服务启动后立即退出

**解决方案**：
- 查看服务日志：`journalctl -u backend.service -n 50`
- 检查环境变量配置
- 检查Python虚拟环境路径
- 检查端口是否被占用

---

## 回滚方案

如果部署出现问题，可以快速回滚：

### 1. 使用Git回滚代码

```bash
# 回滚到上一个版本
git reset --hard HEAD~1

# 或回滚到指定版本
git reset --hard <commit-hash>
```

### 2. 恢复数据库

```bash
# 恢复数据库备份
psql -U user -d dbname < backup.sql
```

### 3. 重启服务

```bash
# 重启后端服务
sudo systemctl restart backend.service

# 重新部署前端
cd packages/frontend
pnpm build:prod
sudo cp -r dist/* /var/www/frontend/dist/
```

---

## 监控和维护

### 日志位置

- **后端日志**：`/var/log/backend/app.log`
- **Nginx日志**：`/var/log/nginx/access.log` 和 `/var/log/nginx/error.log`
- **系统日志**：`journalctl -u backend.service`

### 定期维护

- **每日**：检查日志，监控系统状态
- **每周**：数据库备份，清理临时文件
- **每月**：更新依赖，安全补丁
- **每季度**：性能优化，容量规划

---

## 相关文档

- `DEPLOYMENT_CHECKLIST.md` - 部署检查清单
- `DEPLOYMENT_VERIFICATION.md` - 部署验证
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - 生产部署指南
- `一键启动脚本说明.md` - 启动脚本说明

