#!/usr/bin/env python3
"""
合同预览API调试脚本
"""
import requests
import json

def test_contract_preview_api():
    base_url = "http://localhost:8000"
    
    # 登录获取token
    print("=== 登录获取token ===")
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    print(f"登录状态码: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.text}")
        return
    
    token = login_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("登录成功!")
    
    # 获取合同模板列表
    print("\n=== 获取合同模板列表 ===")
    templates_response = requests.get(f"{base_url}/api/v1/contract-generate/templates", headers=headers)
    print(f"模板列表状态码: {templates_response.status_code}")
    
    if templates_response.status_code != 200:
        print(f"获取模板列表失败: {templates_response.text}")
        return
    
    templates_data = templates_response.json()
    print(f"模板API响应: {json.dumps(templates_data, indent=2, ensure_ascii=False)}")
    
    # 检查响应结构
    if isinstance(templates_data, dict) and "data" in templates_data:
        templates_list = templates_data["data"]
    elif isinstance(templates_data, list):
        templates_list = templates_data
    else:
        print(f"未知的模板API响应格式: {type(templates_data)}")
        return
    
    print(f"可用模板数量: {len(templates_list)}")
    
    if len(templates_list) == 0:
        print("没有可用的模板")
        return
    
    # 使用第一个模板进行测试
    template = templates_list[0]
    template_id = template["id"]
    print(f"使用模板: {template['moban_mingcheng']} (ID: {template_id})")
    
    # 获取客户列表（用于测试）
    print("\n=== 获取客户列表 ===")
    customers_response = requests.get(f"{base_url}/api/v1/customers?page=1&size=5", headers=headers)
    print(f"客户列表状态码: {customers_response.status_code}")
    
    if customers_response.status_code != 200:
        print(f"获取客户列表失败: {customers_response.text}")
        return
    
    customers_data = customers_response.json()
    if customers_data["total"] == 0:
        print("没有可用的客户")
        return
    
    customer = customers_data["items"][0]
    customer_id = customer["id"]
    print(f"使用客户: {customer['gongsi_mingcheng']} (ID: {customer_id})")
    
    # 测试合同预览API
    print("\n=== 测试合同预览API ===")
    preview_data = {
        "hetong_moban_id": template_id,
        "kehu_id": customer_id,
        "bianliang_zhis": {
            "hetong_jine": 10000.0,
            "kehu_mingcheng": customer["gongsi_mingcheng"],
            "fuwu_neirong": "代理记账服务",
            "fuwu_qixian": "12个月"
        }
    }
    
    print(f"预览请求数据: {json.dumps(preview_data, indent=2, ensure_ascii=False)}")
    
    preview_response = requests.post(
        f"{base_url}/api/v1/contract-generate/preview",
        headers=headers,
        json=preview_data
    )
    
    print(f"预览API状态码: {preview_response.status_code}")
    if preview_response.status_code == 200:
        print("预览成功!")
        result = preview_response.json()
        print(f"预览内容长度: {len(result.get('data', {}).get('content', ''))}")
    else:
        print(f"预览失败: {preview_response.text}")
        try:
            error_data = preview_response.json()
            print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            pass

if __name__ == "__main__":
    test_contract_preview_api()