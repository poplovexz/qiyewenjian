#!/bin/bash

# 生产环境部署脚本
# 目标服务器: 172.16.2.221
# 用户: saas

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  生产环境部署脚本${NC}"
echo -e "${GREEN}  目标服务器: 172.16.2.221${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置变量
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_DIR="/home/saas/proxy-system"
LOCAL_DIR="/var/www"

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 构建前端
echo -e "${YELLOW}步骤 1/6: 构建前端...${NC}"
cd packages/frontend
npm run build:prod
if [ $? -ne 0 ]; then
    echo -e "${RED}前端构建失败${NC}"
    exit 1
fi
cd ../..
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 2. 打包项目
echo -e "${YELLOW}步骤 2/6: 打包项目文件...${NC}"
tar -czf deploy-package.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='uploads' \
    --exclude='*.log' \
    --exclude='dist' \
    packages/backend \
    packages/frontend/dist \
    deploy-scripts
echo -e "${GREEN}✓ 项目打包完成${NC}"

# 3. 上传到生产服务器
echo -e "${YELLOW}步骤 3/6: 上传到生产服务器...${NC}"
scp deploy-package.tar.gz ${PROD_USER}@${PROD_HOST}:/tmp/
if [ $? -ne 0 ]; then
    echo -e "${RED}文件上传失败，请检查SSH连接${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 文件上传完成${NC}"

# 4. 在生产服务器上执行部署
echo -e "${YELLOW}步骤 4/6: 在生产服务器上部署...${NC}"
ssh ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
set -e

# 创建部署目录
mkdir -p /home/saas/proxy-system
cd /home/saas/proxy-system

# 备份旧版本
if [ -d "packages" ]; then
    echo "备份旧版本..."
    BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    cp -r packages $BACKUP_DIR/
    echo "✓ 备份完成: $BACKUP_DIR"
fi

# 解压新版本
echo "解压新版本..."
tar -xzf /tmp/deploy-package.tar.gz
rm /tmp/deploy-package.tar.gz

# 设置Python虚拟环境
echo "设置Python虚拟环境..."
cd packages/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip

# 安装依赖
if [ -f "requirements-production.txt" ]; then
    pip install -r requirements-production.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose passlib bcrypt python-multipart redis pydantic-settings
fi

echo "✓ 部署完成"
ENDSSH

echo -e "${GREEN}✓ 服务器部署完成${NC}"

# 5. 配置环境变量
echo -e "${YELLOW}步骤 5/6: 配置环境变量...${NC}"
echo -e "${YELLOW}请手动在生产服务器上配置 .env 文件${NC}"
echo -e "${YELLOW}位置: /home/saas/proxy-system/packages/backend/.env${NC}"

# 6. 启动服务
echo -e "${YELLOW}步骤 6/6: 启动服务...${NC}"
echo -e "${YELLOW}请手动在生产服务器上执行以下命令:${NC}"
echo -e "${GREEN}cd /home/saas/proxy-system/packages/backend${NC}"
echo -e "${GREEN}source venv/bin/activate${NC}"
echo -e "${GREEN}./deploy-scripts/start-production.sh${NC}"

# 清理本地打包文件
rm -f deploy-package.tar.gz

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}下一步操作:${NC}"
echo -e "1. SSH登录到生产服务器: ssh saas@172.16.2.221"
echo -e "2. 配置环境变量: vi /home/saas/proxy-system/packages/backend/.env"
echo -e "3. 启动服务: cd /home/saas/proxy-system/packages/backend && ./deploy-scripts/start-production.sh"
echo -e "4. 配置Nginx反向代理"
echo -e "5. 访问: http://172.16.2.221"

