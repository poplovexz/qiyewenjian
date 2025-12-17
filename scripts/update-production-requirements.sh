#!/bin/bash

# 自动更新生产环境依赖文件
# 使用方法: ./scripts/update-production-requirements.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   自动更新生产环境依赖文件            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  未检测到虚拟环境${NC}"
    echo -e "${YELLOW}正在激活虚拟环境...${NC}"
    
    if [ -f "packages/backend/venv/bin/activate" ]; then
        source packages/backend/venv/bin/activate
    else
        echo -e "${RED}❌ 虚拟环境不存在，请先创建：${NC}"
        echo "cd packages/backend && python3 -m venv venv"
        exit 1
    fi
fi

echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 进入后端目录
cd packages/backend

# 备份旧的 requirements-production.txt
if [ -f "requirements-production.txt" ]; then
    cp requirements-production.txt requirements-production.txt.backup
    echo -e "${GREEN}✓ 已备份旧的依赖文件${NC}"
fi

# 生成新的依赖文件
echo -e "${YELLOW}正在生成依赖文件...${NC}"
pip freeze > requirements-production.txt.new

# 显示差异
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}依赖变更对比：${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if [ -f "requirements-production.txt.backup" ]; then
    diff -u requirements-production.txt.backup requirements-production.txt.new || true
else
    echo "首次生成依赖文件"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"

# 询问是否应用更改
echo ""
echo -e "${YELLOW}是否应用这些更改？ (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    mv requirements-production.txt.new requirements-production.txt
    echo -e "${GREEN}✓ 依赖文件已更新${NC}"
    
    # 显示新增的包
    echo ""
    echo -e "${BLUE}新增的包：${NC}"
    if [ -f "requirements-production.txt.backup" ]; then
        comm -13 <(sort requirements-production.txt.backup) <(sort requirements-production.txt) || true
    fi
    
    # 清理备份
    rm -f requirements-production.txt.backup
    
    echo ""
    echo -e "${GREEN}✓ 完成！${NC}"
    echo -e "${YELLOW}提示：请提交 requirements-production.txt 到版本控制${NC}"
else
    echo -e "${YELLOW}已取消更新${NC}"
    rm -f requirements-production.txt.new
    mv requirements-production.txt.backup requirements-production.txt 2>/dev/null || true
fi

