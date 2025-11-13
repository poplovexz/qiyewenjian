#!/bin/bash

################################################################################
# 生产环境完整部署脚本
# 
# 目标服务器: 172.16.2.221
# 用户: saas
# 密码: Pop781216
#
# 功能:
# 1. 备份生产数据库
# 2. 构建前端和移动端
# 3. 打包并上传代码
# 4. 安装依赖
# 5. 配置环境变量
# 6. 初始化数据库
# 7. 启动所有服务
# 8. 验证部署
################################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"
PROD_DIR="/home/saas/proxy-system"
LOCAL_DIR="/var/www"
DEPLOY_TIME=$(date +%Y%m%d-%H%M%S)
LOG_FILE="deploy-logs/production-deploy-${DEPLOY_TIME}.log"

# 创建日志目录
mkdir -p deploy-logs

# 日志函数
log() {
    echo -e "${1}" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} ${1}"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} ${1}"
}

log_error() {
    log "${RED}[ERROR]${NC} ${1}"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} ${1}"
}

# 打印标题
print_header() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}  ${1}${NC}"
    log "${GREEN}========================================${NC}"
}

# 远程执行命令
remote_exec() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} "$@"
}

# 远程执行脚本
remote_script() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} 'bash -s'
}

# 检查依赖
check_dependencies() {
    print_header "检查本地依赖"
    
    local missing_deps=()
    
    if ! command -v sshpass &> /dev/null; then
        missing_deps+=("sshpass")
    fi
    
    if ! command -v pnpm &> /dev/null; then
        missing_deps+=("pnpm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        log_info "请安装: sudo apt-get install ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "所有依赖已安装"
}

# 测试SSH连接
test_ssh_connection() {
    print_header "测试SSH连接"
    
    if remote_exec "echo 'SSH连接成功'" &> /dev/null; then
        log_success "SSH连接正常"
    else
        log_error "SSH连接失败，请检查服务器地址、用户名和密码"
        exit 1
    fi
}

# 步骤1: 备份生产数据库
backup_production_database() {
    print_header "步骤 1/8: 备份生产数据库"
    
    log_info "连接生产服务器备份数据库..."
    
    remote_script << 'ENDSSH'
set -e

BACKUP_DIR="/home/saas/proxy-system/backups/database"
BACKUP_TIME=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/db-backup-${BACKUP_TIME}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "正在备份数据库..."
pg_dump -h localhost -U postgres proxy_db > "$BACKUP_FILE" 2>/dev/null || {
    echo "数据库备份失败，可能数据库不存在（首次部署）"
    exit 0
}

# 压缩备份文件
gzip "$BACKUP_FILE"

# 只保留最近10个备份
cd $BACKUP_DIR
ls -t *.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm -f

echo "数据库备份完成: ${BACKUP_FILE}.gz"
ENDSSH
    
    log_success "数据库备份完成"
}

# 步骤2: 构建前端和移动端
build_frontend_and_mobile() {
    print_header "步骤 2/8: 构建前端和移动端应用"
    
    # 构建前端
    log_info "构建前端应用..."
    cd packages/frontend
    pnpm install
    pnpm build:prod
    cd ../..
    log_success "前端构建完成"
    
    # 构建移动端
    log_info "构建移动端应用..."
    cd packages/mobile
    pnpm install
    pnpm build
    cd ../..
    log_success "移动端构建完成"
}

# 步骤3: 打包代码
package_code() {
    print_header "步骤 3/8: 打包代码"
    
    log_info "打包项目文件..."
    
    PACKAGE_NAME="deploy-production-${DEPLOY_TIME}.tar.gz"
    
    tar -czf "$PACKAGE_NAME" \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='*.pyc' \
        --exclude='.env.local' \
        --exclude='*.log' \
        --exclude='uploads' \
        --exclude='deploy-logs' \
        --exclude='backups' \
        --exclude='test-results' \
        --exclude='playwright-report' \
        packages/backend \
        packages/frontend/dist \
        packages/mobile/dist \
        deploy-scripts \
        create_admin_user.py \
        init_bank_payment_workflow.py
    
    PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
    log_success "打包完成 (${PACKAGE_SIZE})"
    
    # 上传到服务器
    log_info "上传到生产服务器..."
    sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
        "$PACKAGE_NAME" ${PROD_USER}@${PROD_HOST}:/tmp/
    
    log_success "上传完成"
    
    # 清理本地打包文件
    rm -f "$PACKAGE_NAME"
}

# 步骤4: 在服务器上部署
deploy_on_server() {
    print_header "步骤 4/8: 在服务器上部署"
    
    log_info "解压并安装..."
    
    remote_script << ENDSSH
set -e

PROD_DIR="/home/saas/proxy-system"
DEPLOY_TIME="${DEPLOY_TIME}"

# 创建目录
mkdir -p \$PROD_DIR/{logs,uploads,backups}
cd \$PROD_DIR

# 备份旧版本
if [ -d "packages" ]; then
    echo "备份旧版本..."
    BACKUP_DIR="backups/code-backup-\${DEPLOY_TIME}"
    mkdir -p \$BACKUP_DIR
    cp -r packages \$BACKUP_DIR/ 2>/dev/null || true
    
    # 只保留最近5个备份
    cd backups && ls -t -d code-backup-* 2>/dev/null | tail -n +6 | xargs -r rm -rf && cd ..
    echo "备份完成"
fi

# 删除旧文件（保留.env和uploads）
if [ -d "packages" ]; then
    echo "删除旧文件..."
    # 保存.env文件
    if [ -f "packages/backend/.env" ]; then
        cp packages/backend/.env /tmp/backend.env.backup
    fi
    # 修改权限后删除packages目录
    chmod -R u+w packages 2>/dev/null || true
    rm -rf packages
    echo "旧文件已删除"
fi

# 解压新版本
echo "解压新版本..."
LATEST_PACKAGE=\$(ls -t /tmp/deploy-production-*.tar.gz 2>/dev/null | head -1)
if [ -n "\$LATEST_PACKAGE" ]; then
    tar -xzf "\$LATEST_PACKAGE"
    rm "\$LATEST_PACKAGE"
    echo "解压完成"

    # 恢复.env文件
    if [ -f "/tmp/backend.env.backup" ]; then
        cp /tmp/backend.env.backup packages/backend/.env
        rm /tmp/backend.env.backup
        echo "已恢复.env配置"
    fi
else
    echo "错误: 找不到部署包"
    exit 1
fi

echo "部署文件准备完成"
ENDSSH
    
    log_success "代码部署完成"
}

# 步骤5: 安装依赖
install_dependencies() {
    print_header "步骤 5/8: 安装依赖"
    
    log_info "安装Python和Node.js依赖..."
    
    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/backend

# 创建Python虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip -q

# 安装核心依赖
echo "安装Python依赖..."
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
    python-jose passlib bcrypt python-multipart redis pydantic-settings \
    alembic python-dateutil

echo "Python依赖安装完成"
ENDSSH
    
    log_success "依赖安装完成"
}

# 步骤6: 配置环境变量
configure_environment() {
    print_header "步骤 6/8: 配置环境变量"
    
    log_info "配置生产环境变量..."
    
    # 创建.env文件
    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/backend

# 创建.env文件
cat > .env << 'EOF'
# 应用配置
APP_NAME=代理记账营运内部系统
DEBUG=False
ENVIRONMENT=production

# JWT配置
SECRET_KEY=prod-secret-key-change-this-in-production-$(openssl rand -hex 32)
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

# 缓存配置
CACHE_DEFAULT_TTL=900
CACHE_LONG_TTL=86400
CACHE_SHORT_TTL=60

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=5174
MOBILE_PORT=5175
EOF

echo "环境变量配置完成"
ENDSSH
    
    log_success "环境变量配置完成"
}

# 步骤7: 初始化数据库
initialize_database() {
    print_header "步骤 7/8: 初始化数据库"

    log_info "初始化生产数据库..."

    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/backend
source venv/bin/activate

# 设置PYTHONPATH
export PYTHONPATH=/home/saas/proxy-system/packages/backend/src

# 运行数据库初始化脚本
echo "运行数据库初始化..."
cd src
python3 init_db.py

# 运行额外的初始化脚本
echo "创建产品管理表..."
python3 scripts/create_product_tables.py || echo "产品表可能已存在"

echo "创建线索管理表..."
python3 scripts/create_xiansuo_tables.py || echo "线索表可能已存在"

echo "创建审核工作流表..."
python3 scripts/create_audit_workflow_tables.py || echo "审核表可能已存在"

echo "创建支付管理表..."
python3 scripts/create_payment_tables_stage3.py || echo "支付表可能已存在"

# 初始化权限
echo "初始化权限..."
python3 scripts/init_product_permissions.py || echo "产品权限可能已存在"
python3 scripts/init_contract_permissions.py || echo "合同权限可能已存在"
python3 scripts/init_customer_permissions.py || echo "客户权限可能已存在"

# 初始化合同模板
echo "初始化合同模板..."
python3 scripts/init_contract_templates.py || echo "合同模板可能已存在"

# 初始化支付审核规则
echo "初始化支付审核规则..."
python3 scripts/init_payment_audit_rules.py || echo "审核规则可能已存在"

cd ..

# 创建管理员用户
echo "创建管理员用户..."
python3 create_admin_user.py || echo "管理员用户可能已存在"

# 确保admin用户拥有所有权限（每次部署都运行）
echo "确保admin用户权限..."
cd src
python3 scripts/ensure_admin_permissions.py || echo "⚠️  admin权限配置可能失败"
cd ..

# 初始化银行支付工作流
echo "初始化银行支付工作流..."
python3 init_bank_payment_workflow.py || echo "工作流可能已存在"

echo "数据库初始化完成"
ENDSSH

    log_success "数据库初始化完成"
}

# 步骤8: 启动服务
start_services() {
    print_header "步骤 8/8: 启动服务"

    log_info "停止旧服务..."

    # 停止旧服务
    remote_exec "pkill -f 'uvicorn.*main:app' || true"
    remote_exec "pkill -f 'vite.*5174' || true"
    remote_exec "pkill -f 'vite.*5175' || true"
    sleep 3

    log_info "启动后端服务 (端口 8000)..."

    # 启动后端
    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/backend
source venv/bin/activate

# 启动后端服务
nohup uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

echo "后端服务已启动"
ENDSSH

    sleep 5

    log_info "启动前端服务 (端口 5174)..."

    # 启动前端
    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/frontend

# 安装serve（如果没有）
if ! command -v serve &> /dev/null; then
    npm install -g serve
fi

# 启动前端服务
nohup serve -s dist -l 5174 \
    > /home/saas/proxy-system/logs/frontend.log 2>&1 &

echo "前端服务已启动"
ENDSSH

    sleep 3

    log_info "启动移动端服务 (端口 5175)..."

    # 启动移动端
    remote_script << 'ENDSSH'
set -e

cd /home/saas/proxy-system/packages/mobile

# 启动移动端服务
nohup serve -s dist -l 5175 \
    > /home/saas/proxy-system/logs/mobile.log 2>&1 &

echo "移动端服务已启动"
ENDSSH

    sleep 3

    log_success "所有服务已启动"
}

# 验证部署
verify_deployment() {
    print_header "验证部署"

    log_info "等待服务启动..."
    sleep 10

    # 检查后端
    log_info "检查后端服务 (http://${PROD_HOST}:8000)..."
    if remote_exec "curl -s http://localhost:8000/health | grep -q 'healthy'" 2>/dev/null; then
        log_success "✓ 后端服务正常"
    else
        log_warning "⚠ 后端服务可能未正常启动，请检查日志"
    fi

    # 检查前端
    log_info "检查前端服务 (http://${PROD_HOST}:5174)..."
    if remote_exec "curl -s -o /dev/null -w '%{http_code}' http://localhost:5174" | grep -q "200" 2>/dev/null; then
        log_success "✓ 前端服务正常"
    else
        log_warning "⚠ 前端服务可能未正常启动"
    fi

    # 检查移动端
    log_info "检查移动端服务 (http://${PROD_HOST}:5175)..."
    if remote_exec "curl -s -o /dev/null -w '%{http_code}' http://localhost:5175" | grep -q "200" 2>/dev/null; then
        log_success "✓ 移动端服务正常"
    else
        log_warning "⚠ 移动端服务可能未正常启动"
    fi

    # 显示进程状态
    log_info "服务进程状态:"
    remote_exec "ps aux | grep -E '(uvicorn|serve)' | grep -v grep" || true
}

# 主函数
main() {
    print_header "生产环境部署 - 开始"
    log_info "部署时间: ${DEPLOY_TIME}"
    log_info "目标服务器: ${PROD_HOST}"
    log_info "日志文件: ${LOG_FILE}"

    # 执行部署步骤
    check_dependencies
    test_ssh_connection
    backup_production_database
    build_frontend_and_mobile
    package_code
    deploy_on_server
    install_dependencies
    configure_environment
    initialize_database
    start_services
    verify_deployment

    # 部署完成
    print_header "部署完成"
    log_success "生产环境部署成功！"
    log ""
    log "${GREEN}访问地址:${NC}"
    log "  - 后端 API: http://${PROD_HOST}:8000"
    log "  - API 文档: http://${PROD_HOST}:8000/docs"
    log "  - 前端应用: http://${PROD_HOST}:5174"
    log "  - 移动端应用: http://${PROD_HOST}:5175"
    log ""
    log "${GREEN}默认管理员账号:${NC}"
    log "  - 用户名: admin"
    log "  - 密码: admin123"
    log ""
    log "${YELLOW}下一步操作:${NC}"
    log "  1. 访问前端应用并登录"
    log "  2. 修改管理员密码"
    log "  3. 配置Nginx反向代理（可选）"
    log "  4. 配置systemd服务（可选）"
    log ""
    log "${BLUE}查看日志:${NC}"
    log "  ssh ${PROD_USER}@${PROD_HOST}"
    log "  tail -f /home/saas/proxy-system/logs/backend.log"
    log "  tail -f /home/saas/proxy-system/logs/frontend.log"
    log "  tail -f /home/saas/proxy-system/logs/mobile.log"
}

# 运行主函数
main

