#!/bin/bash

echo "========================================="
echo "启动开发环境服务器"
echo "========================================="
echo ""

# 清理旧进程
echo "1. 清理旧进程..."
killall -9 node uvicorn python3 2>/dev/null || true
sleep 2
echo "✅ 进程已清理"
echo ""

# 启动后端
echo "2. 启动后端服务 (端口 8001)..."
cd /var/www/packages/backend
source venv/bin/activate
export PYTHONPATH=/var/www/packages/backend/src
nohup python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端进程 PID: $BACKEND_PID"
sleep 5

# 检查后端
echo "   检查后端健康状态..."
HEALTH=$(curl -s http://localhost:8001/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ 后端启动成功"
else
    echo "   ❌ 后端启动失败，查看日志: tail -f /tmp/backend.log"
    exit 1
fi
echo ""

# 启动前端
echo "3. 启动前端服务 (端口 5174)..."
cd /var/www/packages/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端进程 PID: $FRONTEND_PID"
sleep 10

# 检查前端
echo "   检查前端服务..."
FRONTEND_CHECK=$(curl -s http://localhost:5174 2>&1)
if [ -n "$FRONTEND_CHECK" ]; then
    echo "   ✅ 前端启动成功"
else
    echo "   ⚠️  前端可能还在启动中，请稍等..."
fi
echo ""

echo "========================================="
echo "服务启动完成"
echo "========================================="
echo ""
echo "后端地址: http://localhost:8001"
echo "前端地址: http://localhost:5174"
echo ""
echo "后端日志: tail -f /tmp/backend.log"
echo "前端日志: tail -f /tmp/frontend.log"
echo ""
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo ""

