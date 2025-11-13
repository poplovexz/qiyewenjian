#!/bin/bash

# 部署验证脚本
# 用于验证生产环境部署是否成功

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROD_HOST="172.16.2.221"
PROD_USER="saas"
PROD_PASS="Pop781216"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           生产环境部署验证脚本                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 测试1: SSH连接
echo -e "${YELLOW}[1/6] 测试SSH连接...${NC}"
if sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    ${PROD_USER}@${PROD_HOST} "echo 'SSH连接成功'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ SSH连接正常${NC}"
else
    echo -e "${RED}✗ SSH连接失败${NC}"
    exit 1
fi

# 测试2: 后端服务状态
echo -e "${YELLOW}[2/6] 检查后端服务状态...${NC}"
SERVICE_STATUS=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "echo '$PROD_PASS' | sudo -S systemctl is-active proxy-system.service" 2>/dev/null || echo "inactive")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "${GREEN}✓ 后端服务运行中${NC}"
else
    echo -e "${RED}✗ 后端服务未运行 (状态: $SERVICE_STATUS)${NC}"
    exit 1
fi

# 测试3: 端口监听
echo -e "${YELLOW}[3/6] 检查端口监听...${NC}"
PORT_CHECK=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "echo '$PROD_PASS' | sudo -S netstat -tlnp | grep ':8000' | wc -l" 2>/dev/null)

if [ "$PORT_CHECK" -gt 0 ]; then
    echo -e "${GREEN}✓ 8000端口正在监听${NC}"
else
    echo -e "${RED}✗ 8000端口未监听${NC}"
    exit 1
fi

# 测试4: API健康检查
echo -e "${YELLOW}[4/6] 测试API健康检查...${NC}"
HEALTH_CHECK=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "curl -s http://localhost:8000/health | grep -o 'healthy' | head -1" 2>/dev/null)

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✓ API健康检查通过${NC}"
else
    echo -e "${RED}✗ API健康检查失败${NC}"
    exit 1
fi

# 测试5: PyJWT依赖
echo -e "${YELLOW}[5/6] 验证PyJWT依赖...${NC}"
PYJWT_CHECK=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "cd /home/saas/proxy-system/packages/backend && source venv/bin/activate && python3 -c 'import jwt; print(jwt.__version__)' 2>&1" || echo "failed")

if [[ "$PYJWT_CHECK" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${GREEN}✓ PyJWT已安装 (版本: $PYJWT_CHECK)${NC}"
else
    echo -e "${RED}✗ PyJWT未安装或导入失败${NC}"
    echo -e "${RED}  错误: $PYJWT_CHECK${NC}"
    exit 1
fi

# 测试6: 前端访问
echo -e "${YELLOW}[6/6] 测试前端访问...${NC}"
FRONTEND_CHECK=$(sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no ${PROD_USER}@${PROD_HOST} \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost/" 2>/dev/null)

if [ "$FRONTEND_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ 前端可以访问 (HTTP $FRONTEND_CHECK)${NC}"
else
    echo -e "${RED}✗ 前端访问失败 (HTTP $FRONTEND_CHECK)${NC}"
    exit 1
fi

# 总结
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✓ 所有验证测试通过！                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}生产环境信息：${NC}"
echo -e "  前端地址: http://${PROD_HOST}/"
echo -e "  移动端地址: http://${PROD_HOST}:81/"
echo -e "  API地址: http://${PROD_HOST}/api/v1/"
echo ""
echo -e "${BLUE}服务管理：${NC}"
echo -e "  查看状态: ssh ${PROD_USER}@${PROD_HOST} 'sudo systemctl status proxy-system.service'"
echo -e "  查看日志: ssh ${PROD_USER}@${PROD_HOST} 'sudo journalctl -u proxy-system.service -f'"
echo -e "  重启服务: ssh ${PROD_USER}@${PROD_HOST} 'sudo systemctl restart proxy-system.service'"
echo ""

