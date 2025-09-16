#!/bin/bash
set -e

echo "开始构建后端..."

# 检查 Python 语法
echo "检查 Python 语法..."
python -m py_compile src/main.py

# 检查导入
echo "检查模块导入..."
python -c "from src.main import app; print('✓ 应用导入成功')"

echo "✓ 后端构建验证完成！"
