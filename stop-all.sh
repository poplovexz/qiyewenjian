#!/bin/bash

# 服务停止脚本 - 停止后端、前端和移动端

echo "=========================================="
echo "停止所有服务"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 停止占用端口的进程
kill_port() {
    local port=$1
    local service=$2
    local pid=$(lsof -ti:$port)
    
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}停止 $service (端口 $port, PID: $pid)...${NC}"
        kill -9 $pid
        sleep 1
        
        # 检查是否成功停止
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            echo -e "${RED}   ✗ 停止失败${NC}"
        else
            echo -e "${GREEN}   ✓ 停止成功${NC}"
        fi
    else
        echo -e "${YELLOW}$service (端口 $port) 未运行${NC}"
    fi
}

# 停止后端服务
echo ""
echo -e "${GREEN}1. 停止后端服务...${NC}"
kill_port 8000 "后端服务"

# 停止前端服务
echo ""
echo -e "${GREEN}2. 停止前端服务...${NC}"
kill_port 5174 "前端服务"

# 停止移动端服务
echo ""
echo -e "${GREEN}3. 停止移动端服务...${NC}"
kill_port 5175 "移动端服务"

# 清理日志文件（可选）
echo ""
read -p "是否清理日志文件? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /tmp/backend.log /tmp/frontend.log /tmp/mobile.log
    echo -e "${GREEN}日志文件已清理${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}所有服务已停止！${NC}"
echo "=========================================="

