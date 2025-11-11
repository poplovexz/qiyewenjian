#!/bin/bash

# 完成生产环境部署的脚本
# 用于手动完成部署的最后几个步骤

PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"

echo "========================================="
echo "完成生产环境部署"
echo "========================================="

# 远程执行命令
remote_exec() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} "$@"
}

# 远程执行脚本
remote_script() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} 'bash -s'
}

echo "步骤1: 停止旧服务..."
remote_exec "pkill -f 'uvicorn.*main:app' || true"
remote_exec "pkill -f 'serve.*5174' || true"
remote_exec "pkill -f 'serve.*5175' || true"
sleep 3
echo "✓ 旧服务已停止"

echo ""
echo "步骤2: 启动后端服务..."
remote_script << 'ENDSSH'
cd /home/saas/proxy-system/packages/backend
source venv/bin/activate
cd src

# 启动后端服务
nohup uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

echo "后端服务已启动"
ENDSSH

sleep 5
echo "✓ 后端服务已启动"

echo ""
echo "步骤3: 启动前端服务..."
remote_script << 'ENDSSH'
cd /home/saas/proxy-system/packages/frontend/dist

# 使用Python的http.server启动前端服务
nohup python3 -m http.server 5174 \
    > /home/saas/proxy-system/logs/frontend.log 2>&1 &

echo "前端服务已启动"
ENDSSH

sleep 3
echo "✓ 前端服务已启动"

echo ""
echo "步骤4: 启动移动端服务..."
remote_script << 'ENDSSH'
cd /home/saas/proxy-system/packages/mobile/dist

# 使用Python的http.server启动移动端服务
nohup python3 -m http.server 5175 \
    > /home/saas/proxy-system/logs/mobile.log 2>&1 &

echo "移动端服务已启动"
ENDSSH

sleep 3
echo "✓ 移动端服务已启动"

echo ""
echo "步骤5: 验证服务..."
sleep 10

# 检查后端
echo -n "检查后端服务... "
if remote_exec "curl -s http://localhost:8000/health | grep -q 'healthy'" 2>/dev/null; then
    echo "✓ 正常"
else
    echo "⚠ 可能未正常启动"
fi

# 检查前端
echo -n "检查前端服务... "
if remote_exec "curl -s -o /dev/null -w '%{http_code}' http://localhost:5174" | grep -q "200" 2>/dev/null; then
    echo "✓ 正常"
else
    echo "⚠ 可能未正常启动"
fi

# 检查移动端
echo -n "检查移动端服务... "
if remote_exec "curl -s -o /dev/null -w '%{http_code}' http://localhost:5175" | grep -q "200" 2>/dev/null; then
    echo "✓ 正常"
else
    echo "⚠ 可能未正常启动"
fi

echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "访问地址:"
echo "  - 后端 API: http://${PROD_HOST}:8000"
echo "  - API 文档: http://${PROD_HOST}:8000/docs"
echo "  - 前端应用: http://${PROD_HOST}:5174"
echo "  - 移动端应用: http://${PROD_HOST}:5175"
echo ""
echo "默认管理员账号:"
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo "查看日志:"
echo "  ssh ${PROD_USER}@${PROD_HOST}"
echo "  tail -f /home/saas/proxy-system/logs/backend.log"
echo "  tail -f /home/saas/proxy-system/logs/frontend.log"
echo "  tail -f /home/saas/proxy-system/logs/mobile.log"
echo ""

