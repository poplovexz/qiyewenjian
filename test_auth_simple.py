#!/usr/bin/env python3
"""
简单的认证测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_auth():
    """测试认证"""
    session = requests.Session()
    
    # 1. 测试登录
    print("🔐 测试登录...")
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = session.post(f"{API_BASE}/auth/login", json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ 登录成功，token: {token[:50]}...")
            
            # 2. 测试带token的请求
            print("\n🔑 测试带token的请求...")
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试获取用户信息
            response = session.get(f"{API_BASE}/auth/me", headers=headers)
            print(f"获取用户信息状态码: {response.status_code}")
            print(f"获取用户信息响应: {response.text}")
            
            # 测试客户列表
            response = session.get(f"{API_BASE}/customers/", headers=headers)
            print(f"获取客户列表状态码: {response.status_code}")
            print(f"获取客户列表响应: {response.text}")
            
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_auth()
