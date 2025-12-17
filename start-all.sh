#!/bin/bash

# 服务启动脚本 - 启动后端、前端和移动端

echo "=========================================="
echo "启动所有服务"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# 停止占用端口的进程
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}端口 $port 被占用，正在停止进程 $pid...${NC}"
        kill -9 $pid
        sleep 1
    fi
}

# 清理之前的进程
echo -e "${YELLOW}清理之前的进程...${NC}"
kill_port 8000
kill_port 5174
kill_port 5175

# 启动后端服务
echo ""
echo -e "${GREEN}1. 启动后端服务 (端口 8000)...${NC}"
cd /var/www/packages/backend
# 激活虚拟环境并启动
nohup bash -c "source venv/bin/activate && cd src && python main.py" > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}   日志文件: /tmp/backend.log${NC}"
echo -e "${GREEN}   访问地址: http://localhost:8000${NC}"
echo -e "${GREEN}   API文档: http://localhost:8000/docs${NC}"

# 等待后端启动（后端需要连接Redis，可能需要较长时间）
echo -e "${YELLOW}   等待后端服务启动（可能需要10-15秒）...${NC}"
for i in {1..15}; do
    if check_port 8000; then
        echo -e "${GREEN}   ✓ 后端服务启动成功（用时 ${i} 秒）${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo -e "${RED}   ✗ 后端服务启动超时，请检查日志: tail -f /tmp/backend.log${NC}"
    fi
done

# 启动前端服务
echo ""
echo -e "${GREEN}2. 启动前端服务 (端口 5174)...${NC}"
cd /var/www/packages/frontend
nohup pnpm dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}   前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}   日志文件: /tmp/frontend.log${NC}"
echo -e "${GREEN}   访问地址: http://localhost:5174${NC}"

# 等待前端启动
echo -e "${YELLOW}   等待前端服务启动...${NC}"
sleep 5

# 检查前端是否启动成功
if check_port 5174; then
    echo -e "${GREEN}   ✓ 前端服务启动成功${NC}"
else
    echo -e "${RED}   ✗ 前端服务启动失败，请检查日志: tail -f /tmp/frontend.log${NC}"
fi

# 启动移动端服务
echo ""
echo -e "${GREEN}3. 启动移动端服务 (端口 5175)...${NC}"
cd /var/www/packages/mobile
nohup pnpm dev > /tmp/mobile.log 2>&1 &
MOBILE_PID=$!
echo -e "${GREEN}   移动端服务已启动 (PID: $MOBILE_PID)${NC}"
echo -e "${GREEN}   日志文件: /tmp/mobile.log${NC}"
echo -e "${GREEN}   访问地址: http://localhost:5175${NC}"

# 等待移动端启动
echo -e "${YELLOW}   等待移动端服务启动...${NC}"
sleep 5

# 检查移动端是否启动成功
if check_port 5175; then
    echo -e "${GREEN}   ✓ 移动端服务启动成功${NC}"
else
    echo -e "${RED}   ✗ 移动端服务启动失败，请检查日志: tail -f /tmp/mobile.log${NC}"
fi

# 显示总结
echo ""
echo "=========================================="
echo -e "${GREEN}所有服务启动完成！${NC}"
echo "=========================================="
echo ""
echo "服务列表："
echo "  1. 后端服务:   http://localhost:8000 (PID: $BACKEND_PID)"
echo "  2. 前端服务:   http://localhost:5174 (PID: $FRONTEND_PID)"
echo "  3. 移动端服务: http://localhost:5175 (PID: $MOBILE_PID)"
echo ""
echo "API文档: http://localhost:8000/docs"
echo ""
echo "查看日志："
echo "  后端:   tail -f /tmp/backend.log"
echo "  前端:   tail -f /tmp/frontend.log"
echo "  移动端: tail -f /tmp/mobile.log"
echo ""
echo "停止所有服务："
echo "  ./stop-all.sh"
echo ""
echo "=========================================="

