#!/usr/bin/env python3
"""
测试合同预览API
"""
import requests
import json

def test_contract_preview():
    """测试合同预览API"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 首先登录获取token
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        # 登录
        print("正在登录...")
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.text}")
            return
        
        login_result = login_response.json()
        print(f"登录响应内容: {login_result}")
        
        # 检查响应结构
        if "data" in login_result:
            token = login_result["data"]["access_token"]
        elif "token" in login_result and "access_token" in login_result["token"]:
            token = login_result["token"]["access_token"]
        elif "access_token" in login_result:
            token = login_result["access_token"]
        else:
            print(f"无法从登录响应中获取token: {login_result}")
            return
            
        print("登录成功，获取到token")
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 获取合同模板列表
        print("\n正在获取合同模板列表...")
        templates_response = requests.get(f"{base_url}/api/v1/contract-generate/templates", headers=headers)
        print(f"模板列表响应状态码: {templates_response.status_code}")
        
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"找到 {len(templates.get('data', []))} 个模板")
            if templates.get('data'):
                template_id = templates['data'][0]['id']
                print(f"使用模板ID: {template_id}")
            else:
                print("没有找到可用的模板")
                return
        else:
            print(f"获取模板失败: {templates_response.text}")
            # 使用一个假的模板ID进行测试
            template_id = "test-template-id"
        
        # 测试合同预览
        print("\n正在测试合同预览...")
        preview_data = {
            "hetong_moban_id": template_id,
            "kehu_id": "d8fb1f90-4126-43f6-8284-71a568e17035",
            "bianliang_zhis": {
                "kehu_mingcheng": "测试公司",
                "hetong_jine": 5000,
                "fuwu_neirong": "代理记账服务"
            }
        }
        
        preview_response = requests.post(
            f"{base_url}/api/v1/contract-generate/preview", 
            json=preview_data, 
            headers=headers
        )
        
        print(f"预览响应状态码: {preview_response.status_code}")
        print(f"预览响应内容: {preview_response.text}")
        
        if preview_response.status_code == 500:
            print("发现500错误，这是我们需要修复的问题")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_contract_preview()