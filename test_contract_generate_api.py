#!/usr/bin/env python3
"""
测试合同生成API
"""
import requests
import json

def test_contract_generate_api():
    """测试合同生成API"""
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
        return
    
    login_result = login_response.json()
    token = login_result["token"]["access_token"]
    print("登录成功，获取到token")
    
    # 获取合同模板列表
    headers = {"Authorization": f"Bearer {token}"}
    print("\n正在获取合同模板列表...")
    templates_response = requests.get(f"{base_url}/api/v1/contract-generate/templates", headers=headers)
    print(f"模板列表响应状态码: {templates_response.status_code}")
    
    if templates_response.status_code != 200:
        print(f"获取模板列表失败: {templates_response.text}")
        return
    
    templates_response_data = templates_response.json()
    print(f"模板响应数据: {json.dumps(templates_response_data, ensure_ascii=False, indent=2)}")
    
    if not templates_response_data.get("success") or not templates_response_data.get("data"):
        print("没有可用的模板")
        return
    
    templates_data = templates_response_data["data"]
    if len(templates_data) == 0:
        print("没有可用的模板")
        return
    
    template_id = templates_data[0]["id"]
    print(f"使用模板ID: {template_id}")
    
    # 测试合同生成API（这可能会失败，因为我们没有有效的报价ID）
    print("\n=== 测试合同生成API ===")
    generate_data = {
        "baojia_id": "2351612a-5b05-4f6d-992e-e51d6f20a257",  # 使用真实的已接受报价ID
        "contract_types": ["daili_jizhang"],  # 合同类型列表
        "daili_jizhang_config": {  # 代理记账合同配置
            "price": 10000.0,
            "count": 1,
            "party_id": None,
            "price_change_reason": "测试价格调整"
        }
    }
    
    generate_response = requests.post(
        f"{base_url}/api/v1/contract-generate/generate",
        headers=headers,
        json=generate_data
    )
    
    print(f"合同生成API状态码: {generate_response.status_code}")
    if generate_response.status_code == 200:
        print("合同生成成功!")
        print(f"响应内容: {generate_response.json()}")
    else:
        print(f"合同生成失败: {generate_response.text}")
        try:
            error_data = generate_response.json()
            print(f"错误详情: {error_data}")
        except:
            pass

if __name__ == "__main__":
    test_contract_generate_api()