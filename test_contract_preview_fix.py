#!/usr/bin/env python3
"""
测试合同预览功能修复
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "yonghu_ming": "admin",
            "mima": "admin123"
        }
    )
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")

    if response.status_code == 200:
        data = response.json()
        # Token is nested in the response
        token_data = data.get("token", {})
        return token_data.get("access_token")
    else:
        print(f"登录失败: {response.status_code}")
        return None

def get_templates(token):
    """获取合同模板列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/contract-generate/templates",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    else:
        print(f"获取模板失败: {response.status_code}")
        print(response.text)
        return []

def get_customers(token):
    """获取客户列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/customers",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"获取客户失败: {response.status_code}")
        print(response.text)
        return []

def test_preview(token, template_id, customer_id):
    """测试合同预览"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    preview_data = {
        "hetong_moban_id": template_id,
        "kehu_id": customer_id,
        "bianliang_zhis": {
            "hetong_jine": 5000,
            "kehu_mingcheng": "测试公司"
        }
    }
    
    print(f"\n发送预览请求:")
    print(f"URL: {BASE_URL}/contract-generate/preview")
    print(f"数据: {json.dumps(preview_data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/contract-generate/preview",
        headers=headers,
        json=preview_data
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ 预览成功!")
        data = response.json()
        content = data.get("data", {}).get("content", "")
        print(f"合同内容长度: {len(content)} 字符")
        print(f"合同内容预览 (前500字符):\n{content[:500]}")
        return True
    else:
        print("❌ 预览失败!")
        print(f"错误响应: {response.text}")
        return False

def main():
    print("=" * 60)
    print("测试合同预览功能修复")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录系统...")
    token = login()
    if not token:
        print("无法获取token，测试终止")
        return
    print(f"✅ 登录成功，token: {token[:20]}...")
    
    # 2. 获取模板
    print("\n2. 获取合同模板...")
    templates = get_templates(token)
    if not templates:
        print("❌ 没有可用的合同模板")
        return
    
    print(f"✅ 找到 {len(templates)} 个模板:")
    for t in templates:
        print(f"  - {t.get('moban_mingcheng')} (ID: {t.get('id')})")
    
    template_id = templates[0].get('id')
    print(f"\n使用模板: {templates[0].get('moban_mingcheng')} (ID: {template_id})")
    
    # 3. 获取客户
    print("\n3. 获取客户列表...")
    customers = get_customers(token)
    if not customers:
        print("❌ 没有可用的客户")
        return
    
    print(f"✅ 找到 {len(customers)} 个客户:")
    for c in customers[:5]:  # 只显示前5个
        print(f"  - {c.get('gongsi_mingcheng')} (ID: {c.get('id')})")
    
    customer_id = customers[0].get('id')
    print(f"\n使用客户: {customers[0].get('gongsi_mingcheng')} (ID: {customer_id})")
    
    # 4. 测试预览
    print("\n4. 测试合同预览...")
    success = test_preview(token, template_id, customer_id)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过！合同预览功能正常工作")
    else:
        print("❌ 测试失败！请检查后端日志")
    print("=" * 60)

if __name__ == "__main__":
    main()

