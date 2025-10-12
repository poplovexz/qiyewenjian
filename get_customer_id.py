#!/usr/bin/env python3
"""
获取有效的客户ID用于测试
"""
import requests
import json

def get_customer_id():
    """获取一个有效的客户ID"""
    base_url = "http://localhost:8000"
    
    # 登录获取token
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    print("正在登录...")
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    print(f"登录响应状态码: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.text}")
        return None
    
    login_result = login_response.json()
    token = login_result["token"]["access_token"]
    print("登录成功，获取到token")
    
    # 获取客户列表
    headers = {"Authorization": f"Bearer {token}"}
    print("\n正在获取客户列表...")
    customers_response = requests.get(f"{base_url}/api/v1/customers/", headers=headers)
    print(f"客户列表响应状态码: {customers_response.status_code}")
    
    if customers_response.status_code != 200:
        print(f"获取客户列表失败: {customers_response.text}")
        return None
    
    customers_data = customers_response.json()
    print(f"客户列表响应内容: {json.dumps(customers_data, ensure_ascii=False, indent=2)}")
    
    if customers_data.get("items") and len(customers_data["items"]) > 0:
        customer_id = customers_data["items"][0]["id"]
        customer_name = customers_data["items"][0]["gongsi_mingcheng"]
        print(f"\n找到客户: {customer_name} (ID: {customer_id})")
        return customer_id
    else:
        print("没有找到任何客户")
        return None

if __name__ == "__main__":
    customer_id = get_customer_id()
    if customer_id:
        print(f"\n可用的客户ID: {customer_id}")
    else:
        print("\n未找到可用的客户ID")