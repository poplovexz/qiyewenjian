#!/usr/bin/env python3
"""
测试前端认证状态和API访问
"""

import requests
import sys

def test_frontend_auth():
    """测试前端认证状态"""
    print("🔐 测试前端认证状态")
    print("=" * 60)
    
    # 1. 测试登录获取token
    print("1. 获取认证token...")
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["token"]["access_token"]
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_api_with_token(token):
    """使用token测试API访问"""
    print("\n🌐 测试API访问")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试产品分类API
    print("1. 测试产品分类列表API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/categories/", headers=headers)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 产品分类API正常，共 {len(categories)} 个分类")
        else:
            print(f"❌ 产品分类API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 产品分类API异常: {e}")
    
    # 测试产品分类选项API
    print("2. 测试产品分类选项API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/categories/options", headers=headers)
        if response.status_code == 200:
            options = response.json()
            print(f"✅ 分类选项API正常，共 {len(options)} 个选项")
        else:
            print(f"❌ 分类选项API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 分类选项API异常: {e}")
    
    # 测试产品项目API
    print("3. 测试产品项目列表API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/products/", headers=headers)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ 产品项目API正常，共 {len(products)} 个产品")
        else:
            print(f"❌ 产品项目API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 产品项目API异常: {e}")

def test_frontend_page():
    """测试前端页面访问"""
    print("\n📱 测试前端页面访问")
    print("=" * 60)
    
    pages = [
        ("代理记账套餐管理", "http://localhost:5174/bookkeeping-packages"),
        ("产品管理", "http://localhost:5174/product-management"),
        ("增值服务", "http://localhost:5174/product-management?type=zengzhi"),
        ("代理记账服务", "http://localhost:5174/product-management?type=daili_jizhang")
    ]
    
    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}页面可访问: {url}")
            else:
                print(f"❌ {name}页面访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}页面访问异常: {e}")

def provide_solution():
    """提供解决方案"""
    print("\n💡 解决401未授权错误的方案")
    print("=" * 60)
    
    print("🔧 可能的原因和解决方案:")
    print()
    print("1. **用户未登录**:")
    print("   - 访问前端页面: http://localhost:5174")
    print("   - 使用管理员账号登录: admin / admin123")
    print("   - 登录后再访问产品管理页面")
    print()
    print("2. **Token过期**:")
    print("   - 刷新页面重新登录")
    print("   - 或者清除浏览器缓存后重新登录")
    print()
    print("3. **前端认证状态丢失**:")
    print("   - 检查浏览器localStorage中的token")
    print("   - 重新登录获取新的token")
    print()
    print("4. **API权限问题**:")
    print("   - 确认用户有product_management权限")
    print("   - 检查后端权限配置")
    print()
    print("🚀 推荐操作步骤:")
    print("1. 打开浏览器访问: http://localhost:5174")
    print("2. 使用admin/admin123登录")
    print("3. 登录成功后访问: http://localhost:5174/bookkeeping-packages")
    print("4. 如果仍有问题，清除浏览器缓存后重试")

def main():
    """主函数"""
    print("🚀 前端认证状态和API访问测试")
    print("=" * 70)
    
    # 1. 测试认证
    token = test_frontend_auth()
    if not token:
        print("\n❌ 无法获取认证token，请检查后端服务")
        sys.exit(1)
    
    # 2. 测试API访问
    test_api_with_token(token)
    
    # 3. 测试前端页面
    test_frontend_page()
    
    # 4. 提供解决方案
    provide_solution()
    
    print("\n🎉 测试完成！")
    print("=" * 70)
    print("如果前端仍然显示401错误，请按照上述解决方案操作。")
    print("最简单的解决方法是重新登录前端系统。")

if __name__ == "__main__":
    main()
