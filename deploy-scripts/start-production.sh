#!/bin/bash

# 生产环境启动脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  启动生产环境服务${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否在正确的目录
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}错误: 请在 packages/backend 目录运行此脚本${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 虚拟环境不存在，请先运行部署脚本${NC}"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: .env 文件不存在，将使用默认配置${NC}"
    echo -e "${YELLOW}建议创建 .env 文件并配置以下变量:${NC}"
    echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/proxy_db"
    echo "SECRET_KEY=your-secret-key-here"
    echo "REDIS_HOST=localhost"
    echo "REDIS_PORT=6379"
fi

# 停止旧进程
echo -e "${YELLOW}停止旧进程...${NC}"
pkill -f "uvicorn.*main:app" || true
sleep 2

# 启动后端服务
echo -e "${YELLOW}启动后端服务...${NC}"
nohup uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > /home/saas/proxy-system/logs/backend.log 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 5

# 检查服务状态
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务启动失败，请检查日志${NC}"
    echo -e "${YELLOW}日志位置: /home/saas/proxy-system/logs/backend.log${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  服务启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "后端服务: http://172.16.2.221:8000"
echo -e "API文档: http://172.16.2.221:8000/docs"
echo -e "健康检查: http://172.16.2.221:8000/health"
echo -e ""
echo -e "查看日志: tail -f /home/saas/proxy-system/logs/backend.log"
echo -e "停止服务: pkill -f 'uvicorn.*main:app'"

