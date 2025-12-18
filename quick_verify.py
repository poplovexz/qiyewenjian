#!/usr/bin/env python3
"""
快速验证客户管理系统
"""

import requests
import json

def quick_verify():
    """快速验证系统状态"""
    print("🚀 快速验证客户管理系统")
    print("=" * 50)
    
    # 1. 检查后端服务
    print("1️⃣ 检查后端服务...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务正常运行")
        else:
            print(f"   ❌ 后端服务异常 (状态码: {response.status_code})")
            return False
    except (requests.RequestException, OSError):
        print("   ❌ 后端服务未运行")
        return False

    # 2. 检查前端服务
    print("2️⃣ 检查前端服务...")
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("   ✅ 前端服务正常运行")
        else:
            print(f"   ❌ 前端服务异常 (状态码: {response.status_code})")
            return False
    except (requests.RequestException, OSError):
        print("   ❌ 前端服务未运行")
        return False
    
    # 3. 测试登录
    print("3️⃣ 测试登录...")
    try:
        login_data = {"yonghu_ming": "admin", "mima": "admin123"}
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data["token"]["access_token"]
            print("   ✅ 登录成功")
        else:
            print(f"   ❌ 登录失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return False
    
    # 4. 测试客户API
    print("4️⃣ 测试客户API...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/api/v1/customers/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            customer_count = data["total"]
            print(f"   ✅ 客户API正常，共有 {customer_count} 个客户")
            
            if customer_count > 0:
                print("   📋 客户列表:")
                for i, customer in enumerate(data["items"][:3], 1):
                    status_map = {"active": "活跃", "renewing": "续约中", "terminated": "已终止"}
                    status = status_map.get(customer["kehu_zhuangtai"], customer["kehu_zhuangtai"])
                    print(f"      {i}. {customer['gongsi_mingcheng']} ({status})")
                if len(data["items"]) > 3:
                    print(f"      ... 还有 {len(data['items']) - 3} 个客户")
            else:
                print("   ⚠️ 客户列表为空，需要创建测试数据")
                return False
        else:
            print(f"   ❌ 客户API失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ 客户API异常: {e}")
        return False
    
    # 5. 测试前端页面
    print("5️⃣ 测试前端页面...")
    pages = [
        ("登录页面", "http://localhost:5174/login"),
        ("客户列表", "http://localhost:5174/customers"),
        ("服务记录", "http://localhost:5174/customer-services")
    ]
    
    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}可访问")
            else:
                print(f"   ❌ {name}访问失败 (状态码: {response.status_code})")
        except (requests.RequestException, OSError):
            print(f"   ❌ {name}连接失败")
    
    print("\n" + "=" * 50)
    print("🎉 系统验证完成！")
    print("\n📋 访问指南:")
    print("1. 打开浏览器访问: http://localhost:5174/login")
    print("2. 使用 admin/admin123 登录")
    print("3. 访问客户管理页面:")
    print("   • 客户列表: http://localhost:5174/customers")
    print("   • 服务记录: http://localhost:5174/customer-services")
    
    print("\n💡 如果客户列表显示为空:")
    print("1. 确保已经登录系统")
    print("2. 检查浏览器控制台是否有错误")
    print("3. 刷新页面重试")
    print("4. 清除浏览器缓存")
    
    return True

if __name__ == "__main__":
    quick_verify()
