#!/bin/bash

echo "========================================="
echo "启动生产服务器前端开发环境"
echo "========================================="

cd /home/saas/proxy-system/packages/frontend

# 清理旧进程
pkill -9 -f 'vite' 2>/dev/null || true
sleep 2

# 启动前端
npm run dev

