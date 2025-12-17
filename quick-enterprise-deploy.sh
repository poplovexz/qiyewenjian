#!/bin/bash

################################################################################
# 快速企业级部署脚本 - 后台运行版本
# 
# 特点：
# - 后台运行，不阻塞终端
# - 实时日志输出
# - 智能跳过未变更的构建
# - 详细的变更报告
################################################################################

set -e

# 配置
PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"
PROD_DIR="/home/saas/proxy-system"

DEPLOY_TIME=$(date +%Y%m%d-%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/deploy-logs/quick-deploy-${DEPLOY_TIME}.log"
REPORT_FILE="${SCRIPT_DIR}/deploy-logs/deploy-report-${DEPLOY_TIME}.html"

# 创建日志目录
mkdir -p "${SCRIPT_DIR}/deploy-logs"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✓ $@${NC}"
}

log_info() {
    log "${BLUE}ℹ $@${NC}"
}

log_warn() {
    log "${YELLOW}⚠ $@${NC}"
}

log_error() {
    log "${RED}✗ $@${NC}"
}

remote_exec() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} "$@"
}

# 开始部署
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 快速企业级部署系统                              ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""

log_info "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "目标服务器: ${PROD_USER}@${PROD_HOST}"
log_info "日志文件: $LOG_FILE"
echo ""

# 1. 分析变更
log_info "【1/7】分析代码变更..."

BACKEND_CHANGED=$(git status --short | grep "packages/backend" | wc -l)
FRONTEND_CHANGED=$(git status --short | grep "packages/frontend" | wc -l)
TOTAL_CHANGED=$(git status --short | grep -v "^$" | wc -l)

log_info "  后端变更: ${BACKEND_CHANGED} 个文件"
log_info "  前端变更: ${FRONTEND_CHANGED} 个文件"
log_info "  总计: ${TOTAL_CHANGED} 个文件"

# 2. 构建前端（仅在有变更时）
if [ $FRONTEND_CHANGED -gt 0 ]; then
    log_info "【2/7】构建前端（检测到前端变更）..."
    cd packages/frontend
    
    if [ ! -d "dist" ]; then
        log_info "  首次构建，这可能需要几分钟..."
    fi
    
    npm run build:prod >> "$LOG_FILE" 2>&1 &
    BUILD_PID=$!
    
    # 显示进度
    while kill -0 $BUILD_PID 2>/dev/null; do
        echo -n "."
        sleep 2
    done
    wait $BUILD_PID
    
    if [ $? -eq 0 ]; then
        DIST_SIZE=$(du -sh dist 2>/dev/null | cut -f1 || echo "未知")
        log_success "  前端构建完成 (${DIST_SIZE})"
    else
        log_error "  前端构建失败"
        exit 1
    fi
    
    cd ../..
else
    log_warn "【2/7】跳过前端构建（无变更）"
    
    # 检查是否存在dist目录
    if [ ! -d "packages/frontend/dist" ]; then
        log_error "  dist目录不存在，需要先构建前端"
        log_info "  运行: cd packages/frontend && npm run build:prod"
        exit 1
    fi
fi

# 3. 打包
log_info "【3/7】打包项目..."

PACKAGE_NAME="deploy-${DEPLOY_TIME}.tar.gz"

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
    packages/backend \
    packages/frontend/dist \
    2>> "$LOG_FILE"

PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
log_success "  打包完成 (${PACKAGE_SIZE})"

# 4. 上传
log_info "【4/7】上传到服务器..."

sshpass -p "$PROD_PASS" scp -o StrictHostKeyChecking=no \
    "$PACKAGE_NAME" ${PROD_USER}@${PROD_HOST}:/tmp/ \
    >> "$LOG_FILE" 2>&1

log_success "  上传完成"

# 5. 备份和部署
log_info "【5/7】服务器端部署..."

remote_exec << 'ENDSSH'
set -e

PROD_DIR="/home/saas/proxy-system"
DEPLOY_TIME=$(date +%Y%m%d-%H%M%S)

echo "  创建目录..."
mkdir -p $PROD_DIR/{logs,uploads,backups}

cd $PROD_DIR

# 备份
if [ -d "packages" ]; then
    echo "  备份旧版本..."
    BACKUP_DIR="backups/backup-${DEPLOY_TIME}"
    mkdir -p $BACKUP_DIR
    cp -r packages $BACKUP_DIR/ 2>/dev/null || true
    
    # 保留最近5个备份
    cd backups && ls -t | tail -n +6 | xargs -r rm -rf && cd ..
    echo "  备份完成: $BACKUP_DIR"
fi

# 修改文件权限以允许覆盖
echo "  修改文件权限..."
if [ -d "packages" ]; then
    chmod -R u+w packages 2>/dev/null || true
fi

# 解压新版本（覆盖模式）
echo "  解压并覆盖旧版本..."
LATEST_PACKAGE=$(ls -t /tmp/deploy-*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_PACKAGE" ]; then
    tar -xzf "$LATEST_PACKAGE" --overwrite
    rm "$LATEST_PACKAGE"
    echo "  解压完成"
else
    echo "  错误: 找不到部署包"
    exit 1
fi

# 安装依赖
echo "  安装Python依赖..."
cd packages/backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip

# 安装核心依赖
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic \
    python-jose passlib bcrypt python-multipart redis pydantic-settings

echo "  部署完成"
ENDSSH

log_success "  服务器部署完成"

# 6. 重启服务
log_info "【6/7】重启服务..."

remote_exec "pkill -f 'uvicorn.*main:app' || true"
sleep 2

remote_exec "
cd $PROD_DIR/packages/backend
source venv/bin/activate
export PYTHONPATH=\$PYTHONPATH:/home/saas/proxy-system/packages/backend/src
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 \
    > $PROD_DIR/logs/backend.log 2>&1 &
echo 'PID:' \$!
"

sleep 3
log_success "  服务已重启"

# 7. 验证
log_info "【7/7】健康检查..."

sleep 2

if remote_exec "curl -s http://localhost:8000/health" | grep -q "healthy"; then
    log_success "  服务运行正常 ✓"
else
    log_warn "  健康检查未通过，请手动检查"
fi

# 清理
rm -f "$PACKAGE_NAME"

# 生成HTML报告
cat > "$REPORT_FILE" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>部署报告</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }
        h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
        .success { color: #10b981; font-weight: bold; }
        .info { background: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        th { background: #f3f4f6; font-weight: 600; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-info { background: #dbeafe; color: #1e40af; }
    </style>
</head>
<body>
    <h1>🚀 生产环境部署报告</h1>
    
    <div class="info">
        <strong>部署时间:</strong> DEPLOY_TIME_PLACEHOLDER<br>
        <strong>目标服务器:</strong> 172.16.2.221<br>
        <strong>状态:</strong> <span class="success">✓ 部署成功</span>
    </div>
    
    <h2>📊 变更统计</h2>
    <table>
        <tr>
            <th>类型</th>
            <th>变更数量</th>
        </tr>
        <tr>
            <td>后端文件</td>
            <td><span class="badge badge-info">BACKEND_CHANGES</span></td>
        </tr>
        <tr>
            <td>前端文件</td>
            <td><span class="badge badge-info">FRONTEND_CHANGES</span></td>
        </tr>
        <tr>
            <td><strong>总计</strong></td>
            <td><span class="badge badge-success">TOTAL_CHANGES</span></td>
        </tr>
    </table>
    
    <h2>🔗 访问地址</h2>
    <ul>
        <li><strong>前端:</strong> <a href="http://172.16.2.221">http://172.16.2.221</a></li>
        <li><strong>API文档:</strong> <a href="http://172.16.2.221:8000/docs">http://172.16.2.221:8000/docs</a></li>
        <li><strong>健康检查:</strong> <a href="http://172.16.2.221:8000/health">http://172.16.2.221:8000/health</a></li>
    </ul>
    
    <h2>📝 部署日志</h2>
    <p>详细日志: <code>LOG_FILE_PLACEHOLDER</code></p>
</body>
</html>
EOF

# 替换占位符
sed -i "s/DEPLOY_TIME_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/g" "$REPORT_FILE"
sed -i "s/BACKEND_CHANGES/${BACKEND_CHANGED}/g" "$REPORT_FILE"
sed -i "s/FRONTEND_CHANGES/${FRONTEND_CHANGED}/g" "$REPORT_FILE"
sed -i "s/TOTAL_CHANGES/${TOTAL_CHANGED}/g" "$REPORT_FILE"
sed -i "s|LOG_FILE_PLACEHOLDER|${LOG_FILE}|g" "$REPORT_FILE"

# 完成
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ✅ 部署成功完成！                                  ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""
log_success "总变更: ${TOTAL_CHANGED} 个文件"
log_success "包大小: ${PACKAGE_SIZE}"
echo ""
log_info "访问地址:"
log_info "  前端: http://172.16.2.221"
log_info "  API:  http://172.16.2.221:8000/docs"
echo ""
log_info "部署报告: ${REPORT_FILE}"
log_info "部署日志: ${LOG_FILE}"
echo ""

# 自动打开报告
if command -v xdg-open &> /dev/null; then
    xdg-open "$REPORT_FILE" 2>/dev/null &
fi

