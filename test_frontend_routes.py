#!/usr/bin/env python3
"""
前端路由测试
验证客户管理相关页面是否可以正常访问
"""

import requests
import time
import sys

# 配置
FRONTEND_URL = "http://localhost:5174"

def test_frontend_routes():
    """测试前端路由"""
    print("🌐 测试前端路由访问...")
    print("=" * 50)
    
    # 测试的路由列表
    routes_to_test = [
        {
            "path": "/",
            "name": "首页",
            "should_redirect": True
        },
        {
            "path": "/login",
            "name": "登录页面",
            "should_redirect": False
        },
        {
            "path": "/dashboard",
            "name": "工作台",
            "should_redirect": False
        },
        {
            "path": "/customers",
            "name": "客户列表",
            "should_redirect": False
        },
        {
            "path": "/customer-services",
            "name": "服务记录",
            "should_redirect": False
        }
    ]
    
    success_count = 0
    total_count = len(routes_to_test)
    
    for route in routes_to_test:
        path = route["path"]
        name = route["name"]
        should_redirect = route["should_redirect"]
        
        print(f"📍 测试路由: {path} ({name})")
        
        try:
            # 发送请求
            response = requests.get(f"{FRONTEND_URL}{path}", 
                                  allow_redirects=False, 
                                  timeout=10)
            
            # 检查响应
            if should_redirect:
                # 期望重定向
                if response.status_code in [301, 302, 307, 308]:
                    print(f"  ✅ 正确重定向 (状态码: {response.status_code})")
                    success_count += 1
                elif response.status_code == 200:
                    print(f"  ✅ 页面正常加载 (状态码: {response.status_code})")
                    success_count += 1
                else:
                    print(f"  ❌ 意外状态码: {response.status_code}")
            else:
                # 期望正常响应
                if response.status_code == 200:
                    print(f"  ✅ 页面正常加载 (状态码: {response.status_code})")
                    success_count += 1
                elif response.status_code in [301, 302, 307, 308]:
                    print(f"  ⚠️ 页面重定向 (状态码: {response.status_code})")
                    # 对于需要认证的页面，重定向到登录页是正常的
                    if path in ["/dashboard", "/customers", "/customer-services"]:
                        print(f"    ℹ️ 认证页面重定向到登录页是正常的")
                        success_count += 1
                    else:
                        print(f"    ❌ 意外的重定向")
                else:
                    print(f"  ❌ 页面加载失败 (状态码: {response.status_code})")
                    
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败 - 前端服务可能未启动")
        except requests.exceptions.Timeout:
            print(f"  ❌ 请求超时")
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
        
        # 短暂延迟
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 个路由测试通过")
    
    if success_count == total_count:
        print("🎉 所有路由测试通过！")
        return True
    else:
        print("⚠️ 部分路由测试失败")
        return False

def test_frontend_service():
    """测试前端服务是否运行"""
    print("🔍 检查前端服务状态...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ 前端服务正常运行 ({FRONTEND_URL})")
            return True
        else:
            print(f"❌ 前端服务响应异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到前端服务 ({FRONTEND_URL})")
        print("   请确保前端服务已启动: cd packages/frontend && pnpm run dev")
        return False
    except Exception as e:
        print(f"❌ 检查前端服务时发生异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始前端路由测试")
    print("=" * 50)
    
    # 1. 检查前端服务
    if not test_frontend_service():
        print("\n❌ 前端服务未正常运行，无法进行路由测试")
        return False
    
    print()
    
    # 2. 测试路由
    success = test_frontend_routes()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 前端路由测试完成！")
        print("\n📋 可用的客户管理页面:")
        print("  • 客户列表: http://localhost:5174/customers")
        print("  • 服务记录: http://localhost:5174/customer-services")
        print("  • 登录页面: http://localhost:5174/login")
        print("  • 工作台: http://localhost:5174/dashboard")
    else:
        print("❌ 前端路由测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
