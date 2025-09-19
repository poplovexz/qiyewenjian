#!/usr/bin/env python3
"""
测试后端服务启动的简化脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI 导入成功")
    except Exception as e:
        print(f"❌ FastAPI 导入失败: {e}")
        return False
    
    try:
        from src.core.config import settings
        print("✅ Settings 导入成功")
        print(f"   - APP_NAME: {settings.APP_NAME}")
        print(f"   - DATABASE_URL: {str(settings.DATABASE_URL)}")
    except Exception as e:
        print(f"❌ Settings 导入失败: {e}")
        return False
    
    try:
        from src.api.api_v1.api import api_router
        print("✅ API Router 导入成功")
    except Exception as e:
        print(f"❌ API Router 导入失败: {e}")
        return False
    
    return True

def test_app_creation():
    """测试应用创建"""
    print("\n🔍 测试应用创建...")
    
    try:
        from fastapi import FastAPI
        from src.core.config import settings
        
        # 创建最简化的应用
        app = FastAPI(
            title=settings.APP_NAME,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
        )
        
        print("✅ FastAPI 应用创建成功")
        return app
    except Exception as e:
        print(f"❌ FastAPI 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_router_inclusion():
    """测试路由包含"""
    print("\n🔍 测试路由包含...")
    
    try:
        app = test_app_creation()
        if not app:
            return False
        
        from src.api.api_v1.api import api_router
        from src.core.config import settings
        
        app.include_router(api_router, prefix=settings.API_V1_STR)
        print("✅ API 路由包含成功")
        return True
    except Exception as e:
        print(f"❌ API 路由包含失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始测试后端服务启动...")
    
    # 测试基础导入
    if not test_imports():
        print("❌ 基础导入测试失败")
        return False
    
    # 测试应用创建
    if not test_app_creation():
        print("❌ 应用创建测试失败")
        return False
    
    # 测试路由包含
    if not test_router_inclusion():
        print("❌ 路由包含测试失败")
        return False
    
    print("\n🎉 所有测试通过！后端服务应该可以正常启动")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
