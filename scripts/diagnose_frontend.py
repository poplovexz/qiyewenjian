#!/usr/bin/env python3
"""
前端问题诊断脚本
"""
import requests
import time
import json

def test_static_pages():
    """测试静态页面"""
    print("🔍 测试静态页面...")
    
    pages = [
        ("主页面", "http://localhost:5174"),
        ("简单测试页面", "http://localhost:5174/simple-test.html"),
        ("测试页面", "http://localhost:5174/test-page.html"),
        ("报价浏览页面", "http://localhost:5174/quote-view.html")
    ]
    
    all_passed = True
    
    for name, url in pages:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                size = len(response.content)
                print(f"  ✅ {name}: 可访问 ({size} 字节)")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {name}: 访问失败 - {e}")
            all_passed = False
    
    return all_passed

def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试API端点...")
    
    endpoints = [
        ("基础API", "http://localhost:8000/api/v1/"),
        ("登录API", "http://localhost:8000/api/v1/auth/login", "POST", {"yonghu_ming": "admin", "mima": "admin123"})
    ]
    
    all_passed = True
    token = None
    
    for endpoint_info in endpoints:
        name = endpoint_info[0]
        url = endpoint_info[1]
        method = endpoint_info[2] if len(endpoint_info) > 2 else "GET"
        data = endpoint_info[3] if len(endpoint_info) > 3 else None
        
        try:
            if method == "POST" and data:
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {name}: 正常")
                if name == "登录API":
                    token = response.json().get("token", {}).get("access_token")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {name}: 失败 - {e}")
            all_passed = False
    
    # 测试用户信息API
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                print(f"  ✅ 用户信息API: 正常 (用户: {user_data.get('xingming', 'Unknown')})")
            else:
                print(f"  ❌ 用户信息API: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ 用户信息API: 失败 - {e}")
            all_passed = False
    
    return all_passed

def test_frontend_javascript():
    """测试前端JavaScript是否正常加载"""
    print("\n🔍 测试前端JavaScript...")
    
    try:
        response = requests.get("http://localhost:5174", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # 检查关键的JavaScript文件引用
            if "/src/main.ts" in content:
                print("  ✅ main.ts 文件引用存在")
            else:
                print("  ❌ main.ts 文件引用缺失")
                return False
            
            if "/@vite/client" in content:
                print("  ✅ Vite 客户端脚本存在")
            else:
                print("  ❌ Vite 客户端脚本缺失")
                return False
            
            if '<div id="app"></div>' in content:
                print("  ✅ Vue 挂载点存在")
            else:
                print("  ❌ Vue 挂载点缺失")
                return False
            
            return True
        else:
            print(f"  ❌ 主页面访问失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 前端JavaScript测试失败: {e}")
        return False

def test_vite_hmr():
    """测试Vite热重载是否正常"""
    print("\n🔍 测试Vite热重载...")
    
    try:
        response = requests.get("http://localhost:5174/@vite/client", timeout=10)
        if response.status_code == 200:
            print("  ✅ Vite 客户端可访问")
            return True
        else:
            print(f"  ❌ Vite 客户端访问失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Vite 热重载测试失败: {e}")
        return False

def check_browser_console():
    """提供浏览器控制台检查建议"""
    print("\n🔍 浏览器控制台检查建议...")
    print("  📋 请在浏览器中打开以下页面并检查控制台:")
    print("     1. http://localhost:5174/simple-test.html")
    print("     2. http://localhost:5174")
    print("  🔍 查看是否有以下错误:")
    print("     - JavaScript 语法错误")
    print("     - 模块加载失败")
    print("     - 网络请求失败")
    print("     - Vue 组件错误")

def main():
    """主函数"""
    print("🚀 开始前端问题诊断...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 测试静态页面
    if not test_static_pages():
        all_tests_passed = False
    
    # 测试API端点
    if not test_api_endpoints():
        all_tests_passed = False
    
    # 测试前端JavaScript
    if not test_frontend_javascript():
        all_tests_passed = False
    
    # 测试Vite热重载
    if not test_vite_hmr():
        all_tests_passed = False
    
    # 浏览器控制台检查建议
    check_browser_console()
    
    print("\n" + "=" * 50)
    
    if all_tests_passed:
        print("🎉 所有自动化测试通过！")
        print("\n✅ 诊断结果:")
        print("  ✅ 静态页面可以正常访问")
        print("  ✅ API端点工作正常")
        print("  ✅ 前端JavaScript文件正常")
        print("  ✅ Vite热重载正常")
        print("\n🔧 建议:")
        print("  1. 在浏览器中打开: http://localhost:5174/simple-test.html")
        print("  2. 点击测试按钮验证功能")
        print("  3. 如果简单测试页面正常，再访问主应用")
        print("  4. 检查浏览器控制台是否有JavaScript错误")
        return True
    else:
        print("❌ 部分测试失败")
        print("\n⚠️ 问题可能在于:")
        print("  - 前端服务配置问题")
        print("  - JavaScript代码错误")
        print("  - Vue组件加载失败")
        print("  - 网络连接问题")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
