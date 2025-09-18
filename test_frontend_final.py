#!/usr/bin/env python3
"""
最终前端测试
"""

import requests
import time

def test_frontend_final():
    """最终前端测试"""
    print("🎯 最终前端测试")
    print("=" * 50)
    
    # 1. 检查服务状态
    print("1️⃣ 检查服务状态...")
    
    # 检查后端
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {response.status_code}")
            return False
    except:
        print("   ❌ 后端服务未运行")
        return False
    
    # 检查前端
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("   ✅ 前端服务正常")
        else:
            print(f"   ❌ 前端服务异常: {response.status_code}")
            return False
    except:
        print("   ❌ 前端服务未运行")
        return False
    
    # 2. 测试API
    print("\n2️⃣ 测试API...")
    try:
        # 登录
        login_data = {"yonghu_ming": "admin", "mima": "admin123"}
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["token"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ 登录成功")
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            return False
        
        # 测试客户API
        response = requests.get("http://localhost:8000/api/v1/customers/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 客户API正常，共 {data['total']} 个客户")
        else:
            print(f"   ❌ 客户API失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API测试异常: {e}")
        return False
    
    # 3. 测试前端页面
    print("\n3️⃣ 测试前端页面...")
    
    pages_to_test = [
        ("登录页面", "http://localhost:5174/login"),
        ("工作台", "http://localhost:5174/dashboard"),
        ("客户列表", "http://localhost:5174/customers"),
        ("服务记录", "http://localhost:5174/customer-services")
    ]
    
    for name, url in pages_to_test:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html = response.text
                size_kb = len(html) / 1024
                print(f"   ✅ {name}: 可访问 ({size_kb:.1f}KB)")
                
                # 检查页面内容
                if size_kb < 1:
                    print(f"      ⚠️ 页面内容较少，可能有问题")
                elif "error" in html.lower() or "exception" in html.lower():
                    print(f"      ⚠️ 页面可能包含错误")
                else:
                    print(f"      ✅ 页面内容正常")
            else:
                print(f"   ❌ {name}: 访问失败 ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {name}: 连接异常 ({e})")
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    
    print("\n📋 访问指南:")
    print("1. 打开浏览器访问: http://localhost:5174/login")
    print("2. 使用以下信息登录:")
    print("   • 用户名: admin")
    print("   • 密码: admin123")
    print("3. 登录后访问客户管理:")
    print("   • 客户列表: http://localhost:5174/customers")
    print("   • 服务记录: http://localhost:5174/customer-services")
    
    print("\n🔧 如果仍有问题:")
    print("1. 确保已经登录系统")
    print("2. 按F12打开开发者工具查看Console错误")
    print("3. 检查Network标签页的API请求")
    print("4. 清除浏览器缓存后重试")
    print("5. 刷新页面重新加载")
    
    return True

if __name__ == "__main__":
    test_frontend_final()
