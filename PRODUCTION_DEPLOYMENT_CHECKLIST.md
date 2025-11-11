# 生产环境部署检查清单

## 部署前准备

### 1. 服务器信息确认
- [x] 服务器IP: 172.16.2.221
- [x] SSH用户: saas
- [x] SSH密码: Pop781216
- [x] 部署目录: /home/saas/proxy-system

### 2. 本地环境检查
- [ ] 确认所有代码已提交到Git
- [ ] 确认当前代码在开发环境运行正常
- [ ] 确认所有测试通过
- [ ] 安装了sshpass工具 (`sudo apt-get install sshpass`)
- [ ] 安装了pnpm (`npm install -g pnpm`)

### 3. 生产服务器环境检查
- [ ] PostgreSQL已安装并运行
- [ ] Redis已安装并运行
- [ ] Python 3.12已安装
- [ ] Node.js已安装
- [ ] 防火墙已开放端口: 8000, 5174, 5175

## 部署步骤

### 自动部署（推荐）

运行自动部署脚本：

```bash
./deploy-to-production.sh
```

脚本将自动完成以下步骤：
1. ✅ 备份生产数据库
2. ✅ 构建前端和移动端
3. ✅ 打包并上传代码
4. ✅ 安装依赖
5. ✅ 配置环境变量
6. ✅ 初始化数据库
7. ✅ 启动所有服务
8. ✅ 验证部署

### 手动部署（备选）

如果自动部署失败，可以按以下步骤手动部署：

#### 步骤1: 备份生产数据库

```bash
ssh saas@172.16.2.221
mkdir -p /home/saas/proxy-system/backups/database
pg_dump -h localhost -U postgres proxy_db > /home/saas/proxy-system/backups/database/db-backup-$(date +%Y%m%d-%H%M%S).sql
gzip /home/saas/proxy-system/backups/database/db-backup-*.sql
```

#### 步骤2: 构建前端和移动端

```bash
# 在本地开发环境
cd /var/www/packages/frontend
pnpm install
pnpm build:prod

cd /var/www/packages/mobile
pnpm install
pnpm build
```

#### 步骤3: 打包代码

```bash
cd /var/www
tar -czf deploy-production.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env.local' \
    --exclude='*.log' \
    packages/backend \
    packages/frontend/dist \
    packages/mobile/dist \
    deploy-scripts \
    create_admin_user.py \
    init_bank_payment_workflow.py
```

#### 步骤4: 上传到服务器

```bash
scp deploy-production.tar.gz saas@172.16.2.221:/tmp/
```

#### 步骤5: 在服务器上部署

```bash
ssh saas@172.16.2.221

# 创建目录
mkdir -p /home/saas/proxy-system/{logs,uploads,backups}
cd /home/saas/proxy-system

# 备份旧版本
if [ -d "packages" ]; then
    cp -r packages backups/code-backup-$(date +%Y%m%d-%H%M%S)/
fi

# 解压新版本
tar -xzf /tmp/deploy-production.tar.gz
rm /tmp/deploy-production.tar.gz
```

#### 步骤6: 安装依赖

```bash
cd /home/saas/proxy-system/packages/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
    python-jose passlib bcrypt python-multipart redis pydantic-settings \
    alembic python-dateutil
```

#### 步骤7: 配置环境变量

```bash
cd /home/saas/proxy-system/packages/backend

cat > .env << 'EOF'
# 应用配置
APP_NAME=代理记账营运内部系统
DEBUG=False
ENVIRONMENT=production

# JWT配置
SECRET_KEY=your-production-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=30

# 数据库配置
DATABASE_URL=postgresql://postgres:Pop781216@localhost:5432/proxy_db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# CORS配置
BACKEND_CORS_ORIGINS=http://172.16.2.221,http://172.16.2.221:5174,http://172.16.2.221:5175,http://172.16.2.221:8000

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=5174
MOBILE_PORT=5175
EOF
```

#### 步骤8: 初始化数据库

```bash
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
export PYTHONPATH=/home/saas/proxy-system/packages/backend/src

# 初始化数据库
cd src
python3 init_db.py

# 创建额外的表
python3 scripts/create_product_tables.py
python3 scripts/create_xiansuo_tables.py
python3 scripts/create_audit_workflow_tables.py
python3 scripts/create_payment_tables_stage3.py

# 初始化权限和数据
python3 scripts/init_product_permissions.py
python3 scripts/init_contract_permissions.py
python3 scripts/init_customer_permissions.py
python3 scripts/init_contract_templates.py
python3 scripts/init_payment_audit_rules.py

cd ..
python3 create_admin_user.py
python3 init_bank_payment_workflow.py
```

#### 步骤9: 启动服务

```bash
# 停止旧服务
pkill -f 'uvicorn.*main:app' || true
pkill -f 'vite.*5174' || true
pkill -f 'vite.*5175' || true

# 启动后端
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

# 安装serve（如果没有）
npm install -g serve

# 启动前端
cd /home/saas/proxy-system/packages/frontend
nohup serve -s dist -l 5174 > /home/saas/proxy-system/logs/frontend.log 2>&1 &

# 启动移动端
cd /home/saas/proxy-system/packages/mobile
nohup serve -s dist -l 5175 > /home/saas/proxy-system/logs/mobile.log 2>&1 &
```

## 部署后验证

### 1. 检查服务状态

```bash
# 检查进程
ps aux | grep -E '(uvicorn|serve)' | grep -v grep

# 检查端口
netstat -tlnp | grep -E '(8000|5174|5175)'
```

### 2. 测试API

```bash
# 健康检查
curl http://172.16.2.221:8000/health

# API文档
curl http://172.16.2.221:8000/docs
```

### 3. 测试前端

在浏览器中访问：
- 前端: http://172.16.2.221:5174
- 移动端: http://172.16.2.221:5175
- API文档: http://172.16.2.221:8000/docs

### 4. 登录测试

使用默认管理员账号登录：
- 用户名: admin
- 密码: admin123

### 5. 功能测试

- [ ] 用户登录/登出
- [ ] 客户管理
- [ ] 线索管理
- [ ] 合同管理
- [ ] 服务工单
- [ ] 任务管理

## 故障排查

### 查看日志

```bash
# 后端日志
tail -f /home/saas/proxy-system/logs/backend.log

# 前端日志
tail -f /home/saas/proxy-system/logs/frontend.log

# 移动端日志
tail -f /home/saas/proxy-system/logs/mobile.log
```

### 常见问题

#### 1. 数据库连接失败

检查PostgreSQL是否运行：
```bash
sudo systemctl status postgresql
```

检查数据库是否存在：
```bash
psql -U postgres -l | grep proxy_db
```

#### 2. Redis连接失败

检查Redis是否运行：
```bash
sudo systemctl status redis
```

#### 3. 端口被占用

查找占用端口的进程：
```bash
lsof -i :8000
lsof -i :5174
lsof -i :5175
```

#### 4. 权限问题

确保saas用户有权限访问所有文件：
```bash
chown -R saas:saas /home/saas/proxy-system
chmod -R 755 /home/saas/proxy-system
```

## 回滚步骤

如果部署失败，可以回滚到之前的版本：

```bash
cd /home/saas/proxy-system

# 查看备份
ls -lt backups/

# 恢复代码
BACKUP_DIR=$(ls -t backups/code-backup-* | head -1)
rm -rf packages
cp -r $BACKUP_DIR/packages .

# 恢复数据库
BACKUP_DB=$(ls -t backups/database/*.sql.gz | head -1)
gunzip -c $BACKUP_DB | psql -U postgres proxy_db

# 重启服务
pkill -f 'uvicorn.*main:app'
pkill -f 'serve'
# 然后重新启动服务
```

## 后续优化

### 1. 配置Nginx反向代理

参考文件: `deploy-scripts/nginx.conf`

### 2. 配置systemd服务

参考文件: `deploy-scripts/systemd-service.conf`

### 3. 配置SSL证书

使用Let's Encrypt配置HTTPS

### 4. 配置自动备份

设置cron任务定期备份数据库

### 5. 配置监控

- 服务器监控
- 应用性能监控
- 日志监控

