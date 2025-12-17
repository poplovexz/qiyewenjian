#!/bin/bash

# 测试后端API脚本

echo "========================================="
echo "  后端API测试脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查后端服务是否运行
echo "1. 检查后端服务状态..."
if lsof -i :8000 | grep -q LISTEN; then
    echo -e "${GREEN}✅ 后端服务正在运行（端口8000）${NC}"
    PID=$(lsof -i :8000 | grep LISTEN | awk '{print $2}' | head -1)
    echo "   进程ID: $PID"
else
    echo -e "${RED}❌ 后端服务未运行${NC}"
    echo "   请先启动后端服务："
    echo "   cd /var/www/packages/backend/src && python3 main.py"
    exit 1
fi

echo ""

# 2. 测试健康检查端点
echo "2. 测试健康检查端点..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/health --max-time 5 2>&1)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 健康检查成功${NC}"
    echo "$HEALTH_RESPONSE" | head -n -1 | python3 -m json.tool 2>/dev/null | head -10
else
    echo -e "${YELLOW}⚠️  健康检查失败或超时${NC}"
    echo "   HTTP状态码: $HTTP_CODE"
fi

echo ""

# 3. 测试登录API（带超时）
echo "3. 测试登录API..."
echo "   请求: POST /api/v1/auth/login"
echo "   数据: {\"yonghu_ming\":\"admin\",\"mima\":\"admin123\"}"
echo "   超时: 30秒"
echo ""

START_TIME=$(date +%s)

LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}\n%{time_total}" \
    -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"yonghu_ming":"admin","mima":"admin123"}' \
    --max-time 30 2>&1)

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -2 | head -1)
TIME_TOTAL=$(echo "$LOGIN_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | head -n -2)

echo "   响应时间: ${TIME_TOTAL}秒 (实际: ${ELAPSED}秒)"
echo "   HTTP状态码: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 登录成功${NC}"
    echo ""
    echo "   响应数据:"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    
    # 提取token
    TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    
    if [ -n "$TOKEN" ]; then
        echo ""
        echo -e "${GREEN}✅ Token获取成功${NC}"
        echo "   Token: ${TOKEN:0:50}..."
        
        # 4. 测试需要认证的API
        echo ""
        echo "4. 测试任务统计API（需要认证）..."
        STATS_RESPONSE=$(curl -s -w "\n%{http_code}" \
            http://localhost:8000/api/v1/task-items/statistics \
            -H "Authorization: Bearer $TOKEN" \
            --max-time 10 2>&1)
        
        STATS_HTTP_CODE=$(echo "$STATS_RESPONSE" | tail -1)
        STATS_BODY=$(echo "$STATS_RESPONSE" | head -n -1)
        
        if [ "$STATS_HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✅ 任务统计API成功${NC}"
            echo ""
            echo "   统计数据:"
            echo "$STATS_BODY" | python3 -m json.tool 2>/dev/null | head -15
        else
            echo -e "${YELLOW}⚠️  任务统计API失败${NC}"
            echo "   HTTP状态码: $STATS_HTTP_CODE"
            echo "   响应: $STATS_BODY"
        fi
    fi
    
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}❌ 登录请求超时（30秒）${NC}"
    echo ""
    echo "   可能的原因:"
    echo "   1. 后端正在启动（Redis连接中）"
    echo "   2. Redis服务未运行或连接很慢"
    echo "   3. 数据库连接问题"
    echo ""
    echo "   建议操作:"
    echo "   1. 等待30-60秒后重试"
    echo "   2. 检查Redis服务: redis-cli ping"
    echo "   3. 重启后端服务"
else
    echo -e "${RED}❌ 登录失败${NC}"
    echo ""
    echo "   响应数据:"
    echo "$RESPONSE_BODY"
fi

echo ""
echo "========================================="
echo "  测试完成"
echo "========================================="
echo ""

# 5. 总结
echo "📊 测试总结:"
echo ""
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 后端API正常工作${NC}"
    echo ""
    echo "   移动端登录应该可以正常使用了！"
    echo "   访问: http://localhost:5175"
    echo "   用户名: admin"
    echo "   密码: admin123"
else
    echo -e "${YELLOW}⚠️  后端API响应异常${NC}"
    echo ""
    echo "   请检查:"
    echo "   1. 后端日志（如果使用脚本启动: tail -f /tmp/backend.log）"
    echo "   2. Redis服务状态（redis-cli ping）"
    echo "   3. 数据库连接状态"
    echo ""
    echo "   或者重启后端服务:"
    echo "   pkill -f 'python.*main.py'"
    echo "   cd /var/www/packages/backend/src && python3 main.py"
fi

echo ""

