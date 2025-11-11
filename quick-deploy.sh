#!/bin/bash

# 快速部署脚本 - 一键部署到生产环境
# 使用方法: ./quick-deploy.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   生产环境一键部署脚本                ║${NC}"
echo -e "${BLUE}║   目标: ${PROD_USER}@${PROD_HOST}        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查 sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}安装 sshpass...${NC}"
    sudo apt-get install -y sshpass || {
        echo -e "${RED}无法安装 sshpass，请手动运行 deploy.sh${NC}"
        exit 1
    }
fi

# 1. 构建前端
echo -e "${YELLOW}[1/7] 构建前端...${NC}"
cd packages/frontend
npm run build:prod || {
    echo -e "${RED}前端构建失败${NC}"
    exit 1
}
cd ../..
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 2. 打包项目
echo -e "${YELLOW}[2/7] 打包项目...${NC}"
tar -czf deploy-package.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='*.log' \
    packages/backend \
    packages/frontend/dist \
    deploy-scripts

echo -e "${GREEN}✓ 打包完成 ($(du -h deploy-package.tar.gz | cut -f1))${NC}"

# 3. 上传文件
echo -e "${YELLOW}[3/7] 上传到生产服务器...${NC}"
sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
    deploy-package.tar.gz ${PROD_USER}@${PROD_HOST}:/tmp/ || {
    echo -e "${RED}上传失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ 上传完成${NC}"

# 4. 部署到服务器
echo -e "${YELLOW}[4/7] 在服务器上部署...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
set -e

# 创建目录
mkdir -p /home/saas/proxy-system
mkdir -p /home/saas/proxy-system/logs
mkdir -p /home/saas/proxy-system/uploads

cd /home/saas/proxy-system

# 备份
if [ -d "packages" ]; then
    BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    cp -r packages $BACKUP_DIR/ 2>/dev/null || true
    echo "✓ 已备份到: $BACKUP_DIR"
fi

# 解压
tar -xzf /tmp/deploy-package.tar.gz
rm /tmp/deploy-package.tar.gz

# 安装依赖
cd packages/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q

if [ -f "requirements-production.txt" ]; then
    pip install -r requirements-production.txt -q
else
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
        python-jose passlib bcrypt python-multipart redis pydantic-settings -q
fi

echo "✓ 服务器部署完成"
ENDSSH

echo -e "${GREEN}✓ 服务器部署完成${NC}"

# 5. 检查配置
echo -e "${YELLOW}[5/7] 检查配置...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
if [ ! -f "/home/saas/proxy-system/packages/backend/.env" ]; then
    echo "⚠ 警告: .env 文件不存在"
    echo "请创建配置文件: /home/saas/proxy-system/packages/backend/.env"
    exit 1
fi
echo "✓ 配置文件存在"
ENDSSH

# 6. 重启服务
echo -e "${YELLOW}[6/7] 重启服务...${NC}"
sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
# 停止旧进程
pkill -f "uvicorn.*main:app" || true
sleep 2

# 启动新进程
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

sleep 3
echo "✓ 服务已重启"
ENDSSH

echo -e "${GREEN}✓ 服务重启完成${NC}"

# 7. 验证部署
echo -e "${YELLOW}[7/7] 验证部署...${NC}"
sleep 2

# 检查健康状态
if sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "curl -s http://localhost:8000/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务可能未正常启动${NC}"
    echo -e "${YELLOW}请检查日志: ssh ${PROD_USER}@${PROD_HOST} 'tail -50 /home/saas/proxy-system/logs/backend.log'${NC}"
fi

# 清理
rm -f deploy-package.tar.gz

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          部署完成！                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}访问地址:${NC}"
echo -e "  前端: ${BLUE}http://${PROD_HOST}${NC}"
echo -e "  API:  ${BLUE}http://${PROD_HOST}:8000/docs${NC}"
echo ""
echo -e "${YELLOW}查看日志:${NC}"
echo -e "  ssh ${PROD_USER}@${PROD_HOST} 'tail -f /home/saas/proxy-system/logs/backend.log'"
echo ""
echo -e "${YELLOW}管理服务:${NC}"
echo -e "  重启: ssh ${PROD_USER}@${PROD_HOST} 'pkill -f uvicorn && cd /home/saas/proxy-system/packages/backend && source venv/bin/activate && nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 > /home/saas/proxy-system/logs/backend.log 2>&1 &'"
echo ""

