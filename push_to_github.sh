#!/bin/bash
# 推送代码到 GitHub 备份仓库

cd /var/www

echo "=== Git 状态 ==="
git status --short | head -20

echo ""
echo "=== 添加所有文件 ==="
git add -A

echo ""
echo "=== 提交更改 ==="
git commit -m "备份: 开发环境完整代码 $(date '+%Y-%m-%d %H:%M:%S')" --allow-empty

echo ""
echo "=== 推送到 GitHub ==="
git push backup feature/contract-preview-improvements:main --force 2>&1

echo ""
echo "=== 完成 ==="

