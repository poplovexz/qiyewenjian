#!/bin/bash

echo "========================================="
echo "启动前端服务 (端口 5174)"
echo "========================================="

# 清理旧进程
echo "清理旧进程..."
pkill -9 -f "vite.*5174" 2>/dev/null || true
sleep 2

# 进入前端目录
cd /var/www/packages/frontend

# 启动服务
echo "启动前端服务..."
npm run dev

