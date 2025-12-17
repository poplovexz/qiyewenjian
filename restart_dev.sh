#!/bin/bash

echo "========================================="
echo "重启本地开发环境"
echo "========================================="
echo ""

# 1. 清理所有进程
echo "1. 清理旧进程..."
pkill -9 node 2>/dev/null || true
pkill -9 uvicorn 2>/dev/null || true
pkill -9 python3 2>/dev/null || true
sleep 3
echo "   ✅ 进程已清理"
echo ""

# 2. 清理日志文件
echo "2. 清理日志文件..."
rm -f /tmp/backend_dev.log /tmp/frontend_dev.log
echo "   ✅ 日志已清理"
echo ""

# 3. 启动后端
echo "3. 启动后端服务 (端口 8000)..."
cd /var/www/packages/backend
nohup bash -c 'source venv/bin/activate && export PYTHONPATH=/var/www/packages/backend/src && python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload' > /tmp/backend_dev.log 2>&1 &
BACKEND_PID=$!
echo "   后端进程 PID: $BACKEND_PID"
sleep 8

# 检查后端
echo "   检查后端健康状态..."
HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>&1)
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "   ✅ 后端启动成功"
    echo "   后端地址: http://localhost:8000"
else
    echo "   ❌ 后端启动失败"
    echo "   查看日志: tail -f /tmp/backend_dev.log"
    exit 1
fi
echo ""

# 4. 启动前端
echo "4. 启动前端服务..."
cd /var/www/packages/frontend
nohup npm run dev > /tmp/frontend_dev.log 2>&1 &
FRONTEND_PID=$!
echo "   前端进程 PID: $FRONTEND_PID"
sleep 10

# 检查前端日志
echo "   检查前端启动状态..."
if grep -q "ready in" /tmp/frontend_dev.log; then
    FRONTEND_URL=$(grep -oP "Local:\s+\Khttp://[^\s]+" /tmp/frontend_dev.log | head -1)
    echo "   ✅ 前端启动成功"
    echo "   前端地址: $FRONTEND_URL"
elif grep -q "Port.*already in use" /tmp/frontend_dev.log; then
    echo "   ❌ 前端启动失败: 端口被占用"
    echo "   查看日志: tail -f /tmp/frontend_dev.log"
    exit 1
else
    echo "   ⚠️  前端可能还在启动中..."
    echo "   查看日志: tail -f /tmp/frontend_dev.log"
fi
echo ""

echo "========================================="
echo "✅ 开发环境启动完成"
echo "========================================="
echo ""
echo "📊 服务状态:"
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:5174 (或查看上面的实际端口)"
echo ""
echo "📝 日志文件:"
echo "   后端: tail -f /tmp/backend_dev.log"
echo "   前端: tail -f /tmp/frontend_dev.log"
echo ""
echo "🔍 进程信息:"
echo "   后端 PID: $BACKEND_PID"
echo "   前端 PID: $FRONTEND_PID"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   或: pkill -9 node; pkill -9 uvicorn"
echo ""

