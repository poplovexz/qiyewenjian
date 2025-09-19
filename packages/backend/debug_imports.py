#!/usr/bin/env python3
"""
逐步测试导入，找出导致阻塞的模块
"""
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_with_timeout(module_name, timeout=10):
    """测试导入模块，带超时"""
    print(f"🔍 测试导入: {module_name}")
    start_time = time.time()
    
    try:
        if module_name == "fastapi":
            from fastapi import FastAPI
        elif module_name == "src.core.config":
            from src.core.config import settings
        elif module_name == "src.core.redis_client":
            from src.core.redis_client import redis_client
        elif module_name == "src.core.cache_decorator":
            from src.core.cache_decorator import warm_up_cache, cache_health_check
        elif module_name == "src.api.api_v1.api":
            from src.api.api_v1.api import api_router
        elif module_name == "src.services.xiansuo_guanli.baojia_event_handlers":
            from src.services.xiansuo_guanli.baojia_event_handlers import register_baojia_event_handlers
        else:
            exec(f"import {module_name}")
        
        elapsed = time.time() - start_time
        print(f"✅ {module_name} 导入成功 ({elapsed:.2f}s)")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {module_name} 导入失败 ({elapsed:.2f}s): {e}")
        return False

def test_basic_imports():
    """测试基础导入"""
    print("=" * 50)
    print("🔍 测试基础Python模块导入")
    print("=" * 50)
    
    basic_modules = [
        "fastapi",
        "pydantic", 
        "sqlalchemy",
        "redis",
        "uvicorn"
    ]
    
    for module in basic_modules:
        if not test_import_with_timeout(module):
            return False
    
    return True

def test_project_imports():
    """测试项目模块导入"""
    print("\n" + "=" * 50)
    print("🔍 测试项目模块导入")
    print("=" * 50)
    
    project_modules = [
        "src.core.config",
        "src.core.redis_client", 
        "src.core.cache_decorator",
    ]
    
    for module in project_modules:
        if not test_import_with_timeout(module):
            return False
    
    return True

def test_api_imports():
    """测试API模块导入"""
    print("\n" + "=" * 50)
    print("🔍 测试API模块导入")
    print("=" * 50)
    
    # 这个是最可能出问题的地方
    return test_import_with_timeout("src.api.api_v1.api")

def test_service_imports():
    """测试服务模块导入"""
    print("\n" + "=" * 50)
    print("🔍 测试服务模块导入")
    print("=" * 50)
    
    return test_import_with_timeout("src.services.xiansuo_guanli.baojia_event_handlers")

def main():
    """主函数"""
    print("🚀 开始逐步测试导入...")
    
    # 测试基础导入
    if not test_basic_imports():
        print("❌ 基础模块导入失败")
        return False
    
    # 测试项目核心模块
    if not test_project_imports():
        print("❌ 项目核心模块导入失败")
        return False
    
    # 测试API模块 - 这里最可能出问题
    if not test_api_imports():
        print("❌ API模块导入失败")
        return False
    
    # 测试服务模块
    if not test_service_imports():
        print("❌ 服务模块导入失败")
        return False
    
    print("\n🎉 所有导入测试通过！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
