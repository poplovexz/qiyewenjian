# 一键部署指南

## 📋 部署脚本说明

### 当前使用的脚本

一键部署功能（http://localhost:5174/settings/deploy）使用的脚本是：**`/var/www/quick-deploy.sh`**

### 部署范围

✅ **前端（PC端）** - 构建并部署到 `/home/saas/proxy-system/packages/frontend/dist/`
✅ **移动端** - 构建并部署到 `/home/saas/proxy-system/packages/mobile/dist/`
✅ **后端API** - 部署到 `/home/saas/proxy-system/packages/backend/`
✅ **数据库迁移** - 自动运行所有SQL迁移脚本

---

## 🚀 部署流程（9个步骤）

### 步骤1：构建前端
- 命令：`npm run build:prod`
- 产物：`packages/frontend/dist/`

### 步骤2：构建移动端
- 命令：`npm run build`
- 产物：`packages/mobile/dist/`

### 步骤3：打包项目
- 打包内容：
  - `packages/backend/`（后端源代码）
  - `packages/frontend/dist/`（前端构建产物）
  - `packages/mobile/dist/`（移动端构建产物）
  - `deploy-scripts/`（部署脚本）

### 步骤4：上传到生产服务器
- 目标：172.16.2.221
- 用户：saas
- 上传到：`/tmp/deploy-package.tar.gz`

### 步骤5：在服务器上部署
- 备份旧版本到 `backup-YYYYMMDD-HHMMSS/`
- 解压新版本
- 恢复 `.env` 配置文件
- 安装Python依赖（创建新的虚拟环境）

### 步骤6：检查配置
- 验证 `.env` 文件存在

### 步骤7：运行数据库迁移
- 执行所有SQL迁移脚本
- 创建缺失的数据库表
- 初始化权限数据
- 确保admin用户权限

### 步骤8：重启服务
- 停止旧的后端服务
- 启动新的后端服务（Uvicorn，4个worker）

### 步骤9：验证部署
- 检查后端健康状态
- 验证数据库表
- 验证前端和移动端文件

---

## 🌐 生产环境访问地址

部署完成后，可以通过以下地址访问：

- **前端PC端**: http://172.16.2.221
- **移动端**: http://172.16.2.221:81
- **API文档**: http://172.16.2.221:8000/docs
- **健康检查**: http://172.16.2.221:8000/health

---

## 📂 生产环境目录结构

```
/home/saas/proxy-system/
├── packages/
│   ├── backend/              # 后端代码
│   │   ├── src/
│   │   ├── venv/            # Python虚拟环境
│   │   └── .env             # 环境配置
│   ├── frontend/
│   │   └── dist/            # 前端构建产物（Nginx提供）
│   └── mobile/
│       └── dist/            # 移动端构建产物（Nginx提供）
├── logs/
│   └── backend.log          # 后端日志
├── uploads/                 # 上传文件
└── backup-*/                # 备份目录
```

---

## 🔧 Nginx配置

### 80端口（前端PC端）
- 静态文件：`/home/saas/proxy-system/packages/frontend/dist/`
- 移动端路径：`/mobile/` → `/home/saas/proxy-system/packages/mobile/dist/`
- API代理：`/api/v1/` → `http://127.0.0.1:8000/api/v1/`

### 81端口（移动端）
- 静态文件：`/home/saas/proxy-system/packages/mobile/dist/`
- API代理：`/api/v1/` → `http://127.0.0.1:8000/api/v1/`

---

## ⚙️ 服务管理

### 启动后端服务
```bash
ssh saas@172.16.2.221
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
nohup uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &
```

### 停止后端服务
```bash
pkill -f "uvicorn.*main:app"
```

### 查看后端日志
```bash
tail -f /home/saas/proxy-system/logs/backend.log
```

### 重启Nginx
```bash
echo 'Pop781216' | sudo -S systemctl restart nginx
```

---

## 📝 注意事项

1. **前端和移动端不需要单独启动服务**
   - Nginx直接提供静态文件服务
   - 不需要运行 `npm run dev` 或 `vite`

2. **只需要启动后端服务**
   - 后端API服务（Uvicorn，8000端口）
   - Nginx服务（通常已经在运行）

3. **部署前确保**
   - `.env` 文件配置正确
   - 数据库连接正常
   - Redis连接正常

4. **部署后验证**
   - 访问前端PC端：http://172.16.2.221
   - 访问移动端：http://172.16.2.221:81
   - 检查API健康：http://172.16.2.221:8000/health

