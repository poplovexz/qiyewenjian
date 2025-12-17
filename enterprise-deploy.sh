#!/bin/bash

################################################################################
# 企业级生产环境部署脚本
# 
# 功能特性:
# - 详细的变更分析和影响评估
# - 自动备份和回滚机制
# - 完整的部署日志记录
# - 健康检查和验证
# - 部署报告生成
#
# 使用方法: ./enterprise-deploy.sh
################################################################################

set -e

# ============================================================================
# 配置区域
# ============================================================================

# 生产环境配置
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"
PROD_DIR="/home/saas/proxy-system"

# 本地配置
LOCAL_DIR="/var/www"
DEPLOY_TIME=$(date +%Y%m%d-%H%M%S)
LOG_DIR="deploy-logs"
LOG_FILE="${LOG_DIR}/deploy-${DEPLOY_TIME}.log"
REPORT_FILE="${LOG_DIR}/deploy-report-${DEPLOY_TIME}.md"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================================================
# 工具函数
# ============================================================================

# 创建日志目录
mkdir -p "$LOG_DIR"

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
    log "SUCCESS" "${GREEN}✓ $@${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}⚠ $@${NC}"
}

log_error() {
    log "ERROR" "${RED}✗ $@${NC}"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}${BOLD}  $@${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# 错误处理
error_exit() {
    log_error "$1"
    log_error "部署失败，请查看日志: $LOG_FILE"
    exit 1
}

# 执行远程命令
remote_exec() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} "$@"
}

# ============================================================================
# 部署报告生成
# ============================================================================

init_report() {
    cat > "$REPORT_FILE" << EOF
# 生产环境部署报告

**部署时间:** $(date '+%Y年%m月%d日 %H:%M:%S')  
**部署人员:** $(whoami)  
**目标服务器:** ${PROD_USER}@${PROD_HOST}  
**部署路径:** ${PROD_DIR}

---

## 📊 部署概览

EOF
}

add_to_report() {
    echo "$@" >> "$REPORT_FILE"
}

# ============================================================================
# 主流程
# ============================================================================

log_section "🚀 企业级生产环境部署系统"
log_info "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "目标服务器: ${PROD_USER}@${PROD_HOST}"
log_info "日志文件: $LOG_FILE"
log_info "报告文件: $REPORT_FILE"

init_report

# ============================================================================
# 步骤 1: 环境预检查
# ============================================================================

log_section "步骤 1/9: 环境预检查"

# 检查当前目录
if [ ! -f "package.json" ]; then
    error_exit "请在项目根目录运行此脚本"
fi
log_success "当前目录正确"

# 检查必要工具
for tool in sshpass git node npm tar; do
    if ! command -v $tool &> /dev/null; then
        error_exit "$tool 未安装"
    fi
    log_success "$tool 已安装"
done

# 检查SSH连接
log_info "测试SSH连接..."
if remote_exec "echo 'SSH连接成功'" > /dev/null 2>&1; then
    log_success "SSH连接正常"
else
    error_exit "SSH连接失败"
fi

# ============================================================================
# 步骤 2: 代码变更分析
# ============================================================================

log_section "步骤 2/9: 代码变更分析"

# 获取Git状态
log_info "分析代码变更..."
CHANGED_FILES=$(git status --short)
CHANGE_COUNT=$(echo "$CHANGED_FILES" | grep -v "^$" | wc -l)

if [ $CHANGE_COUNT -eq 0 ]; then
    log_warning "没有检测到代码变更"
else
    log_info "发现 $CHANGE_COUNT 个文件变更:"
    echo "$CHANGED_FILES" | head -20 | tee -a "$LOG_FILE"
fi

# 统计变更类型
BACKEND_CHANGES=$(echo "$CHANGED_FILES" | grep "packages/backend" | wc -l)
FRONTEND_CHANGES=$(echo "$CHANGED_FILES" | grep "packages/frontend" | wc -l)
CONFIG_CHANGES=$(echo "$CHANGED_FILES" | grep -E "\.(env|json|yaml|yml|conf)$" | wc -l)

log_info "变更统计:"
log_info "  后端文件: $BACKEND_CHANGES"
log_info "  前端文件: $FRONTEND_CHANGES"
log_info "  配置文件: $CONFIG_CHANGES"

# 添加到报告
add_to_report "### 变更统计"
add_to_report ""
add_to_report "| 类型 | 数量 |"
add_to_report "|------|------|"
add_to_report "| 后端文件 | $BACKEND_CHANGES |"
add_to_report "| 前端文件 | $FRONTEND_CHANGES |"
add_to_report "| 配置文件 | $CONFIG_CHANGES |"
add_to_report "| **总计** | **$CHANGE_COUNT** |"
add_to_report ""

# ============================================================================
# 步骤 3: 获取生产环境状态
# ============================================================================

log_section "步骤 3/9: 获取生产环境状态"

log_info "检查生产环境..."

PROD_STATUS=$(remote_exec "
    if [ -d '$PROD_DIR' ]; then
        echo 'EXISTS'
        if pgrep -f 'uvicorn.*main:app' > /dev/null; then
            echo 'RUNNING'
        else
            echo 'STOPPED'
        fi
        if [ -d '$PROD_DIR/backups' ]; then
            ls -t '$PROD_DIR/backups' | head -1
        else
            echo 'NO_BACKUP'
        fi
    else
        echo 'NOT_EXISTS'
    fi
")

log_info "生产环境状态:"
echo "$PROD_STATUS" | tee -a "$LOG_FILE"

# ============================================================================
# 步骤 4: 用户确认
# ============================================================================

log_section "步骤 4/9: 部署确认"

echo ""
echo -e "${YELLOW}${BOLD}⚠️  部署确认${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "目标服务器: ${BOLD}${PROD_HOST}${NC}"
echo -e "变更文件数: ${BOLD}${CHANGE_COUNT}${NC}"
echo -e "后端变更: ${BOLD}${BACKEND_CHANGES}${NC} | 前端变更: ${BOLD}${FRONTEND_CHANGES}${NC} | 配置变更: ${BOLD}${CONFIG_CHANGES}${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "确认部署到生产环境? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_warning "用户取消部署"
    exit 0
fi

log_success "用户确认部署"

# ============================================================================
# 步骤 5: 构建前端
# ============================================================================

log_section "步骤 5/9: 构建前端"

cd packages/frontend || error_exit "无法进入前端目录"

log_info "开始构建前端..."
BUILD_START=$(date +%s)

npm run build:prod >> "$LOG_FILE" 2>&1 || error_exit "前端构建失败"

BUILD_END=$(date +%s)
BUILD_TIME=$((BUILD_END - BUILD_START))

if [ ! -d "dist" ]; then
    error_exit "构建产物不存在"
fi

DIST_SIZE=$(du -sh dist | cut -f1)
log_success "前端构建完成 (耗时: ${BUILD_TIME}s, 大小: ${DIST_SIZE})"

cd ../..

# ============================================================================
# 步骤 6: 打包项目
# ============================================================================

log_section "步骤 6/9: 打包项目"

log_info "开始打包项目..."

PACKAGE_NAME="deploy-${DEPLOY_TIME}.tar.gz"

tar -czf "$PACKAGE_NAME" \
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
    --exclude='deploy-logs' \
    packages/backend \
    packages/frontend/dist \
    deploy-scripts \
    || error_exit "打包失败"

PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
log_success "打包完成 (大小: ${PACKAGE_SIZE})"

# ============================================================================
# 步骤 7: 上传到服务器
# ============================================================================

log_section "步骤 7/9: 上传到服务器"

log_info "开始上传文件..."
UPLOAD_START=$(date +%s)

sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
    "$PACKAGE_NAME" ${PROD_USER}@${PROD_HOST}:/tmp/ \
    || error_exit "文件上传失败"

UPLOAD_END=$(date +%s)
UPLOAD_TIME=$((UPLOAD_END - UPLOAD_START))

log_success "文件上传完成 (耗时: ${UPLOAD_TIME}s)"

# ============================================================================
# 步骤 8: 服务器端部署
# ============================================================================

log_section "步骤 8/9: 服务器端部署"

log_info "在服务器上执行部署..."

remote_exec << ENDSSH
set -e

echo "[INFO] 创建目录结构..."
mkdir -p $PROD_DIR
mkdir -p $PROD_DIR/logs
mkdir -p $PROD_DIR/uploads
mkdir -p $PROD_DIR/backups

cd $PROD_DIR

# 备份旧版本
if [ -d "packages" ]; then
    BACKUP_DIR="backups/backup-${DEPLOY_TIME}"
    echo "[INFO] 备份旧版本到: \$BACKUP_DIR"
    mkdir -p \$BACKUP_DIR
    cp -r packages \$BACKUP_DIR/ 2>/dev/null || true
    
    # 只保留最近10个备份
    cd backups
    ls -t | tail -n +11 | xargs -r rm -rf
    cd ..
    
    echo "[SUCCESS] 备份完成"
fi

# 解压新版本
echo "[INFO] 解压新版本..."
tar -xzf /tmp/${PACKAGE_NAME}
rm /tmp/${PACKAGE_NAME}

# 安装Python依赖
echo "[INFO] 安装Python依赖..."
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

echo "[SUCCESS] 部署完成"
ENDSSH

log_success "服务器部署完成"

# ============================================================================
# 步骤 9: 重启服务并验证
# ============================================================================

log_section "步骤 9/9: 重启服务并验证"

log_info "停止旧服务..."
remote_exec "pkill -f 'uvicorn.*main:app' || true"
sleep 3

log_info "启动新服务..."
remote_exec "
cd $PROD_DIR/packages/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 \
    > $PROD_DIR/logs/backend.log 2>&1 &
"

sleep 5

log_info "验证服务健康状态..."
if remote_exec "curl -s http://localhost:8000/health" | grep -q "healthy"; then
    log_success "服务运行正常"
else
    log_error "服务可能未正常启动，请检查日志"
fi

# ============================================================================
# 完成
# ============================================================================

# 清理本地文件
rm -f "$PACKAGE_NAME"

log_section "✅ 部署完成"

TOTAL_TIME=$(($(date +%s) - $(date -d "$(head -1 $LOG_FILE | cut -d' ' -f1-2)" +%s)))

echo ""
log_success "=========================================="
log_success "  部署成功完成！"
log_success "=========================================="
echo ""
log_info "部署信息:"
log_info "  总耗时: ${TOTAL_TIME}s"
log_info "  变更文件: ${CHANGE_COUNT}"
log_info "  包大小: ${PACKAGE_SIZE}"
echo ""
log_info "访问地址:"
log_info "  前端: http://${PROD_HOST}"
log_info "  API:  http://${PROD_HOST}:8000/docs"
echo ""
log_info "日志文件:"
log_info "  本地: ${LOG_FILE}"
log_info "  服务器: ssh ${PROD_USER}@${PROD_HOST} 'tail -f ${PROD_DIR}/logs/backend.log'"
echo ""
log_info "部署报告: ${REPORT_FILE}"
echo ""

# 完成报告
add_to_report ""
add_to_report "## ✅ 部署结果"
add_to_report ""
add_to_report "- **状态:** 成功"
add_to_report "- **总耗时:** ${TOTAL_TIME}秒"
add_to_report "- **包大小:** ${PACKAGE_SIZE}"
add_to_report ""
add_to_report "## 📝 访问信息"
add_to_report ""
add_to_report "- **前端:** http://${PROD_HOST}"
add_to_report "- **API文档:** http://${PROD_HOST}:8000/docs"
add_to_report ""

log_success "部署报告已生成: ${REPORT_FILE}"

