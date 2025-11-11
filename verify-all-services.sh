#!/bin/bash

# 验证所有服务是否正常运行

echo "=========================================="
echo "  验证所有服务状态"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS_COUNT=0
FAIL_COUNT=0

# 1. 检查后端服务
echo "1. 检查后端服务 (端口 8000)..."
if lsof -i :8000 | grep -q LISTEN; then
    echo -e "${GREEN}   ✓ 后端服务正在运行${NC}"
    
    # 测试健康检查
    HEALTH=$(curl -s http://localhost:8000/health --max-time 3 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✓ 健康检查通过${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${YELLOW}   ⚠ 健康检查失败${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo -e "${RED}   ✗ 后端服务未运行${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# 2. 检查前端服务
echo "2. 检查前端服务 (端口 5174)..."
if lsof -i :5174 | grep -q LISTEN; then
    echo -e "${GREEN}   ✓ 前端服务正在运行${NC}"
    
    # 测试访问
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174 --max-time 3 2>&1)
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}   ✓ 前端页面可访问${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${YELLOW}   ⚠ 前端页面访问异常 (HTTP $HTTP_CODE)${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo -e "${RED}   ✗ 前端服务未运行${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# 3. 检查移动端服务
echo "3. 检查移动端服务 (端口 5175)..."
if lsof -i :5175 | grep -q LISTEN; then
    echo -e "${GREEN}   ✓ 移动端服务正在运行${NC}"
    
    # 测试访问
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5175 --max-time 3 2>&1)
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}   ✓ 移动端页面可访问${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${YELLOW}   ⚠ 移动端页面访问异常 (HTTP $HTTP_CODE)${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo -e "${RED}   ✗ 移动端服务未运行${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# 4. 测试后端登录API
echo "4. 测试后端登录API..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}\n%{time_total}" \
    -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"yonghu_ming":"admin","mima":"admin123"}' \
    --max-time 10 2>&1)

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -2 | head -1)
TIME_TOTAL=$(echo "$LOGIN_RESPONSE" | tail -1)

echo "   HTTP状态码: $HTTP_CODE"
echo "   响应时间: ${TIME_TOTAL}秒"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}   ✓ 登录API正常响应${NC}"
    if (( $(echo "$TIME_TOTAL < 5" | bc -l) )); then
        echo -e "${GREEN}   ✓ 响应速度正常 (<5秒)${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${YELLOW}   ⚠ 响应速度较慢 (>5秒)${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
else
    echo -e "${RED}   ✗ 登录API异常${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# 总结
echo "=========================================="
echo "  验证结果"
echo "=========================================="
echo ""

TOTAL=$((SUCCESS_COUNT + FAIL_COUNT))
echo "总检查项: $TOTAL"
echo -e "${GREEN}成功: $SUCCESS_COUNT${NC}"
echo -e "${RED}失败: $FAIL_COUNT${NC}"

echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 所有服务运行正常！${NC}"
    echo ""
    echo "可以开始使用了："
    echo "  - 后端API文档: http://localhost:8000/docs"
    echo "  - 前端PC端:    http://localhost:5174"
    echo "  - 移动端H5:    http://localhost:5175"
    echo ""
    echo "移动端登录测试："
    echo "  1. 访问 http://localhost:5175"
    echo "  2. 用户名: admin"
    echo "  3. 密码: admin123"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  部分服务异常，请检查日志${NC}"
    echo ""
    echo "查看日志："
    echo "  后端:   tail -f /tmp/backend.log"
    echo "  前端:   tail -f /tmp/frontend.log"
    echo "  移动端: tail -f /tmp/mobile.log"
    echo ""
    exit 1
fi

