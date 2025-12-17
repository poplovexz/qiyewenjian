#!/bin/bash

# 工单任务项分配功能 - Playwright 测试运行脚本

echo "================================================================================"
echo "Playwright 端到端测试"
echo "================================================================================"
echo ""
echo "可用的测试："
echo "  1. 完整业务流程测试（推荐）- 从线索到工单任务项分配"
echo "  2. 任务项分配测试 - 仅测试任务项分配功能（需要已有工单）"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Playwright 是否已安装
echo "【检查1】检查 Playwright 是否已安装..."
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npx 未找到，请先安装 Node.js${NC}"
    exit 1
fi

# 检查 @playwright/test 是否已安装
if ! pnpm list @playwright/test &> /dev/null; then
    echo -e "${YELLOW}⚠️  @playwright/test 未安装，正在安装...${NC}"
    pnpm add -D @playwright/test -w
fi

# 检查 Chromium 浏览器是否已安装
CHROMIUM_DIR=$(find "$HOME/.cache/ms-playwright" -maxdepth 1 -name "chromium-*" -type d 2>/dev/null | head -1)
if [ -z "$CHROMIUM_DIR" ]; then
    echo -e "${YELLOW}⚠️  Playwright 浏览器未安装，正在安装...${NC}"
    npx playwright install chromium
fi

echo -e "${GREEN}✅ Playwright 已安装${NC}"
echo ""

# 检查后端服务
echo "【检查2】检查后端服务是否运行..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务正在运行 (http://localhost:8000)${NC}"
else
    echo -e "${RED}❌ 后端服务未运行${NC}"
    echo -e "${YELLOW}请先启动后端服务：${NC}"
    echo "  cd packages/backend"
    echo "  source venv/bin/activate"
    echo "  python src/main.py"
    exit 1
fi
echo ""

# 检查前端服务
echo "【检查3】检查前端服务是否运行..."
if curl -s http://localhost:5174 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务正在运行 (http://localhost:5174)${NC}"
else
    echo -e "${RED}❌ 前端服务未运行${NC}"
    echo -e "${YELLOW}请先启动前端服务：${NC}"
    echo "  cd packages/frontend"
    echo "  npm run dev"
    exit 1
fi
echo ""

# 创建截图目录
echo "【准备】创建截图目录..."
mkdir -p screenshots
echo -e "${GREEN}✅ 截图目录已创建${NC}"
echo ""

# 运行测试
echo "================================================================================"
echo "开始运行测试..."
echo "================================================================================"
echo ""

# 确定要运行的测试文件
TEST_FILE="tests/e2e/test_task_item_assignment.spec.ts"

# 检查是否指定了完整流程测试
if [ "$1" == "--complete" ] || [ "$2" == "--complete" ]; then
    TEST_FILE="tests/e2e/test_complete_workflow.spec.ts"
    echo "📋 运行完整业务流程测试（从线索到工单任务项分配）"
    echo ""
else
    echo "📋 运行任务项分配测试（需要已有工单数据）"
    echo "💡 提示：使用 --complete 参数运行完整流程测试"
    echo ""
fi

# 根据参数选择运行模式
if [ "$1" == "--debug" ] || [ "$2" == "--debug" ]; then
    echo "以调试模式运行..."
    npx playwright test "$TEST_FILE" --debug
elif [ "$1" == "--ui" ] || [ "$2" == "--ui" ]; then
    echo "以UI模式运行..."
    npx playwright test "$TEST_FILE" --ui
elif [ "$1" == "--headed" ] || [ "$2" == "--headed" ]; then
    echo "显示浏览器窗口运行..."
    npx playwright test "$TEST_FILE" --headed
else
    echo "以无头模式运行..."
    npx playwright test "$TEST_FILE"
fi

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}✅ 测试执行成功！${NC}"
    echo "================================================================================"
    echo ""
    echo "查看测试结果："
    echo "  - 截图目录: screenshots/"
    echo "  - HTML报告: npx playwright show-report"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo -e "${RED}❌ 测试执行失败${NC}"
    echo "================================================================================"
    echo ""
    echo "故障排查："
    echo "  1. 检查后端和前端服务是否正常运行"
    echo "  2. 检查数据库是否已迁移（添加 zhixing_ren_id 字段）"
    echo "  3. 检查是否有工单和用户数据"
    echo "  4. 查看截图目录了解失败原因"
    echo "  5. 以调试模式运行: ./run-task-assignment-test.sh --debug"
    echo ""
    exit 1
fi

