#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 设置Python路径
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 启动应用
cd src && python main.py
