#!/bin/bash

echo "========================================="
echo "启动后端服务 (端口 8000)"
echo "========================================="

# 清理旧进程
echo "清理旧进程..."
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
sleep 2

# 进入后端目录
cd /var/www/packages/backend

# 激活虚拟环境
source venv/bin/activate

# 设置PYTHONPATH
export PYTHONPATH=/var/www/packages/backend/src

# 启动服务
echo "启动后端服务..."
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

