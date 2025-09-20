#!/usr/bin/env python3
"""
新的服务器启动脚本 - 使用重构后的模块化结构
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 启动重构后的模块化后端服务...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )
