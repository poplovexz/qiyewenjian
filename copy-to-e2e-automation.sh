#!/bin/bash

# 复制 E2E 测试文件到 e2e-automation 文件夹

echo "开始复制文件到 e2e-automation 文件夹..."

# 创建目录结构
mkdir -p e2e-automation/tests
mkdir -p e2e-automation/screenshots
mkdir -p e2e-automation/docs

# 复制测试文件
echo "复制测试文件..."
cp tests/e2e/test_complete_workflow.spec.ts e2e-automation/tests/
cp tests/e2e/test_task_item_assignment.spec.ts e2e-automation/tests/

# 复制配置文件
echo "复制配置文件..."
cp playwright.config.ts e2e-automation/

# 复制运行脚本
echo "复制运行脚本..."
cp run-task-assignment-test.sh e2e-automation/
cp run-task-assignment-test.bat e2e-automation/
chmod +x e2e-automation/run-task-assignment-test.sh

# 复制文档
echo "复制文档..."
cp COMPLETE_WORKFLOW_TEST.md e2e-automation/docs/
cp WSL_PLAYWRIGHT_GUIDE.md e2e-automation/docs/
cp prepare-test-data.md e2e-automation/docs/

# 复制截图（如果存在）
if [ -d "screenshots" ]; then
  echo "复制截图..."
  cp screenshots/*.png e2e-automation/screenshots/ 2>/dev/null || true
fi

echo ""
echo "✅ 文件复制完成！"
echo ""
echo "e2e-automation 文件夹内容："
ls -la e2e-automation/
echo ""
echo "tests 目录："
ls -la e2e-automation/tests/
echo ""
echo "docs 目录："
ls -la e2e-automation/docs/

