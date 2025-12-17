#!/bin/bash

# 部署前检查脚本
# 使用方法: ./scripts/pre-deploy-check.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   部署前检查                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 1. 检查 requirements-production.txt 是否存在
echo -e "${YELLOW}[1/6] 检查依赖文件...${NC}"
if [ -f "packages/backend/requirements-production.txt" ]; then
    echo -e "${GREEN}✓ requirements-production.txt 存在${NC}"
else
    echo -e "${RED}✗ requirements-production.txt 不存在${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. 检查是否有未提交的迁移文件
echo -e "${YELLOW}[2/6] 检查数据库迁移文件...${NC}"
MIGRATION_FILES=$(find packages/backend/migrations -name "*.sql" 2>/dev/null | wc -l)
echo -e "${GREEN}✓ 找到 $MIGRATION_FILES 个迁移文件${NC}"

# 3. 检查 .env.example 是否存在
echo -e "${YELLOW}[3/6] 检查环境变量模板...${NC}"
if [ -f "packages/backend/.env.example" ]; then
    echo -e "${GREEN}✓ .env.example 存在${NC}"
else
    echo -e "${YELLOW}⚠ .env.example 不存在${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 4. 检查前端构建
echo -e "${YELLOW}[4/6] 检查前端构建...${NC}"
cd packages/frontend
if npm run build:prod > /tmp/frontend-build.log 2>&1; then
    echo -e "${GREEN}✓ 前端构建成功${NC}"
else
    echo -e "${RED}✗ 前端构建失败，查看日志: /tmp/frontend-build.log${NC}"
    ERRORS=$((ERRORS + 1))
fi
cd ../..

# 5. 测试依赖安装
echo -e "${YELLOW}[5/6] 测试依赖安装...${NC}"
cd packages/backend

# 创建临时虚拟环境
TEMP_VENV="/tmp/test-venv-$$"
python3 -m venv "$TEMP_VENV" > /dev/null 2>&1

# 激活并测试安装
source "$TEMP_VENV/bin/activate"
if pip install -r requirements-production.txt -q > /tmp/pip-install.log 2>&1; then
    echo -e "${GREEN}✓ 所有依赖可以正常安装${NC}"
else
    echo -e "${RED}✗ 依赖安装失败，查看日志: /tmp/pip-install.log${NC}"
    tail -20 /tmp/pip-install.log
    ERRORS=$((ERRORS + 1))
fi
deactivate

# 清理临时环境
rm -rf "$TEMP_VENV"
cd ../..

# 6. 检查后端启动
echo -e "${YELLOW}[6/6] 检查后端代码...${NC}"
cd packages/backend
source venv/bin/activate
if python3 -c "from src.main import app; print('OK')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端代码可以正常导入${NC}"
else
    echo -e "${RED}✗ 后端代码导入失败${NC}"
    ERRORS=$((ERRORS + 1))
fi
deactivate
cd ../..

# 总结
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}检查结果总结${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！可以安全部署${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ 有 $WARNINGS 个警告，但可以部署${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $ERRORS 个错误，请修复后再部署${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ 另有 $WARNINGS 个警告${NC}"
    fi
    exit 1
fi

