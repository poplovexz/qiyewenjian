#!/usr/bin/env python3
"""
启动脚本 - 设置正确的Python路径并启动应用
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# 设置环境变量
os.environ.setdefault("PYTHONPATH", str(src_dir))

if __name__ == "__main__":
    # 切换到src目录
    os.chdir(src_dir)

    # 导入uvicorn
    import uvicorn
    import os

    # 安全修复：从环境变量读取 host，默认 127.0.0.1
    host = os.getenv("UVICORN_HOST", "127.0.0.1")

    # 启动应用（使用导入字符串以支持reload）
    uvicorn.run(
        "main:app",
        host=host,
        port=8000,
        reload=True,
        reload_dirs=[str(src_dir)],
        log_level="info"
    )
