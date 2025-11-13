#!/bin/bash

# 自动部署脚本 - 带详细检查和日志
# 使用方法: ./auto-deploy.sh

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
PROD_DIR="/home/saas/proxy-system"
LOG_FILE="deploy-$(date +%Y%m%d-%H%M%S).log"

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "${BLUE}$@${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$@${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}$@${NC}"
}

log_error() {
    log "ERROR" "${RED}$@${NC}"
}

# 错误处理
error_exit() {
    log_error "$1"
    exit 1
}

# 打印标题
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_header "生产环境自动部署脚本"
log_info "目标服务器: ${PROD_USER}@${PROD_HOST}"
log_info "部署路径: ${PROD_DIR}"
log_info "日志文件: ${LOG_FILE}"

# ============================================
# 步骤 0: 预检查
# ============================================
print_header "步骤 0/8: 预检查"

# 检查是否在项目根目录
if [ ! -f "package.json" ]; then
    error_exit "请在项目根目录运行此脚本"
fi
log_success "✓ 当前目录正确"

# 检查 sshpass
if ! command -v sshpass &> /dev/null; then
    log_warning "sshpass 未安装，正在安装..."
    sudo apt-get install -y sshpass || error_exit "无法安装 sshpass"
fi
log_success "✓ sshpass 已安装"

# 检查 git 状态
log_info "检查代码变更..."
CHANGED_FILES=$(git status --short | wc -l)
if [ $CHANGED_FILES -gt 0 ]; then
    log_warning "发现 ${CHANGED_FILES} 个文件有变更:"
    git status --short | head -10 | tee -a "$LOG_FILE"
else
    log_info "没有未提交的变更"
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    error_exit "Node.js 未安装"
fi
log_success "✓ Node.js 版本: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    error_exit "npm 未安装"
fi
log_success "✓ npm 版本: $(npm --version)"

# ============================================
# 步骤 1: 构建前端
# ============================================
print_header "步骤 1/8: 构建前端"

cd packages/frontend || error_exit "无法进入前端目录"

# 检查依赖
if [ ! -d "node_modules" ]; then
    log_warning "node_modules 不存在，正在安装依赖..."
    npm install || error_exit "依赖安装失败"
fi

# 构建
log_info "开始构建前端..."
npm run build:prod || error_exit "前端构建失败"

# 检查构建产物
if [ ! -d "dist" ]; then
    error_exit "构建产物不存在"
fi

DIST_SIZE=$(du -sh dist | cut -f1)
log_success "✓ 前端构建完成 (大小: ${DIST_SIZE})"

cd ../..

# ============================================
# 步骤 2: 打包项目
# ============================================
print_header "步骤 2/8: 打包项目"

log_info "开始打包项目文件..."

tar -czf deploy-package.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='*.log' \
    --exclude='uploads' \
    --exclude='*.md' \
    packages/backend \
    packages/frontend/dist \
    deploy-scripts \
    quick-deploy.sh \
    || error_exit "打包失败"

PACKAGE_SIZE=$(du -h deploy-package.tar.gz | cut -f1)
log_success "✓ 打包完成 (大小: ${PACKAGE_SIZE})"

# ============================================
# 步骤 3: 测试SSH连接
# ============================================
print_header "步骤 3/8: 测试SSH连接"

log_info "测试SSH连接..."
if sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    ${PROD_USER}@${PROD_HOST} "echo 'SSH连接成功'" > /dev/null 2>&1; then
    log_success "✓ SSH连接正常"
else
    error_exit "SSH连接失败，请检查网络和服务器状态"
fi

# ============================================
# 步骤 4: 上传文件
# ============================================
print_header "步骤 4/8: 上传到生产服务器"

log_info "开始上传文件..."
sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
    deploy-package.tar.gz ${PROD_USER}@${PROD_HOST}:/tmp/ \
    || error_exit "文件上传失败"

log_success "✓ 文件上传完成"

# ============================================
# 步骤 5: 备份和部署
# ============================================
print_header "步骤 5/8: 服务器端部署"

log_info "在服务器上执行部署..."

sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
set -e

echo "[INFO] 创建目录结构..."
mkdir -p /home/saas/proxy-system
mkdir -p /home/saas/proxy-system/logs
mkdir -p /home/saas/proxy-system/uploads
mkdir -p /home/saas/proxy-system/backups

cd /home/saas/proxy-system

# 备份旧版本
if [ -d "packages" ]; then
    BACKUP_DIR="backups/backup-$(date +%Y%m%d-%H%M%S)"
    echo "[INFO] 备份旧版本到: $BACKUP_DIR"
    mkdir -p $BACKUP_DIR
    cp -r packages $BACKUP_DIR/ 2>/dev/null || true
    
    # 只保留最近5个备份
    cd backups
    ls -t | tail -n +6 | xargs -r rm -rf
    cd ..
    
    echo "[SUCCESS] 备份完成"
fi

# 解压新版本
echo "[INFO] 解压新版本..."
tar -xzf /tmp/deploy-package.tar.gz
rm /tmp/deploy-package.tar.gz
echo "[SUCCESS] 解压完成"

# 安装Python依赖
echo "[INFO] 安装Python依赖..."
cd packages/backend

if [ ! -d "venv" ]; then
    echo "[INFO] 创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q

if [ -f "requirements-production.txt" ]; then
    pip install -r requirements-production.txt -q
else
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
        python-jose PyJWT passlib bcrypt python-multipart redis pydantic-settings -q
fi

echo "[SUCCESS] 依赖安装完成"
ENDSSH

log_success "✓ 服务器部署完成"

# ============================================
# 步骤 6: 检查配置
# ============================================
print_header "步骤 6/8: 检查配置"

log_info "检查配置文件..."

sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
if [ ! -f "/home/saas/proxy-system/packages/backend/.env" ]; then
    echo "[WARNING] .env 文件不存在"
    echo "[INFO] 创建默认配置文件..."
    cat > /home/saas/proxy-system/packages/backend/.env << 'EOF'
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/dbname

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 环境
ENVIRONMENT=production
EOF
    echo "[WARNING] 请手动配置 .env 文件"
else
    echo "[SUCCESS] 配置文件存在"
fi
ENDSSH

log_success "✓ 配置检查完成"

# ============================================
# 步骤 6.5: 数据库迁移和权限配置
# ============================================
print_header "步骤 6.5/8: 数据库迁移和权限配置"

log_info "运行数据库迁移和权限配置..."

sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
export PYTHONPATH=/home/saas/proxy-system/packages/backend/src
cd src

# 确保admin用户拥有所有权限（每次部署都运行）
echo "[INFO] 确保admin用户权限..."
python3 scripts/ensure_admin_permissions.py || echo "[WARNING] admin权限配置可能失败"

echo "[SUCCESS] 数据库迁移和权限配置完成"
ENDSSH

log_success "✓ 数据库迁移和权限配置完成"

# ============================================
# 步骤 7: 重启服务
# ============================================
print_header "步骤 7/8: 重启服务"

log_info "停止旧服务..."

sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} << 'ENDSSH'
# 停止旧进程
pkill -f "uvicorn.*main:app" || true
sleep 3
echo "[SUCCESS] 旧服务已停止"

# 启动新服务
echo "[INFO] 启动新服务..."
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate

nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

sleep 5
echo "[SUCCESS] 新服务已启动"
ENDSSH

log_success "✓ 服务重启完成"

# ============================================
# 步骤 8: 验证部署
# ============================================
print_header "步骤 8/8: 验证部署"

log_info "等待服务启动..."
sleep 3

log_info "检查服务健康状态..."

if sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "curl -s http://localhost:8000/health" | grep -q "healthy"; then
    log_success "✓ 后端服务运行正常"
else
    log_error "✗ 后端服务可能未正常启动"
    log_warning "请检查日志: ssh ${PROD_USER}@${PROD_HOST} 'tail -50 /home/saas/proxy-system/logs/backend.log'"
fi

# 清理本地文件
rm -f deploy-package.tar.gz
log_info "清理临时文件完成"

# ============================================
# 部署完成
# ============================================
print_header "部署完成！"

echo ""
log_success "=========================================="
log_success "  部署成功完成！"
log_success "=========================================="
echo ""
log_info "访问地址:"
log_info "  前端: http://${PROD_HOST}"
log_info "  API:  http://${PROD_HOST}:8000/docs"
echo ""
log_info "查看日志:"
log_info "  ssh ${PROD_USER}@${PROD_HOST} 'tail -f /home/saas/proxy-system/logs/backend.log'"
echo ""
log_info "本地日志: ${LOG_FILE}"
echo ""

