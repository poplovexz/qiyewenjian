#!/usr/bin/env python3
"""
测试报价到合同的完整流程
验证生成合同按钮的显示逻辑
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# API配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
XIANSUO_URL = f"{BASE_URL}/api/v1/leads"
BAOJIA_URL = f"{BASE_URL}/api/v1/lead-quotes"

def login():
    """登录获取token"""
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        result = response.json()
        token_data = result.get("token", {})
        return token_data.get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def fetch_xiansuo_list(token):
    """获取线索列表"""
    headers = get_headers(token)
    response = requests.get(f"{XIANSUO_URL}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取线索列表失败: {response.status_code} - {response.text}")
        return None

def fetch_baojia_by_xiansuo(token, xiansuo_id):
    """获取线索的报价列表"""
    headers = get_headers(token)
    response = requests.get(f"{BAOJIA_URL}/xiansuo/{xiansuo_id}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取报价列表失败: {response.status_code} - {response.text}")
        return []

def create_baojia(token, xiansuo_id):
    """创建报价"""
    headers = get_headers(token)
    
    # 获取产品数据
    product_response = requests.get(f"{BAOJIA_URL}/product-data", headers=headers)
    if product_response.status_code != 200:
        print("获取产品数据失败")
        return None
    
    product_data = product_response.json()
    if not product_data.get('chanpin_xiangmu') or len(product_data['chanpin_xiangmu']) == 0:
        print("没有可用的产品项目")
        return None
    
    # 使用第一个产品项目
    first_product = product_data['chanpin_xiangmu'][0]
    
    baojia_data = {
        "xiansuo_id": xiansuo_id,
        "baojia_mingcheng": f"测试报价_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "youxiao_qi": (datetime.now() + timedelta(days=30)).isoformat(),
        "chanpin_xiangmu_id": first_product['id'],
        "xiangmu_mingcheng": first_product['xiangmu_mingcheng'],
        "xiangmu_jiage": first_product['jiage'],
        "xiangmu_shuliang": 1,
        "beizhu": "测试报价，用于验证生成合同按钮"
    }
    
    response = requests.post(BAOJIA_URL, json=baojia_data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"创建报价失败: {response.status_code} - {response.text}")
        return None

def confirm_baojia(token, baojia_id):
    """确认报价"""
    headers = get_headers(token)
    response = requests.post(f"{BAOJIA_URL}/{baojia_id}/confirm", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"确认报价失败: {response.status_code} - {response.text}")
        return None

def check_button_display_logic(xiansuo, baojia_list):
    """检查按钮显示逻辑"""
    print(f"\n=== 线索: {xiansuo.get('gongsi_mingcheng', 'N/A')} (ID: {xiansuo['id']}) ===")
    print(f"线索状态: {xiansuo.get('xiansuo_zhuangtai', 'N/A')}")
    print(f"报价数量: {len(baojia_list)}")
    
    # 检查是否有有效报价
    has_valid_baojia = False
    accepted_baojia = None
    
    for baojia in baojia_list:
        print(f"  报价: {baojia.get('baojia_mingcheng', 'N/A')} - 状态: {baojia.get('baojia_zhuangtai', 'N/A')} - 过期: {baojia.get('is_expired', False)}")
        
        if not baojia.get('is_expired', False) and baojia.get('baojia_zhuangtai') != 'rejected':
            has_valid_baojia = True
            
        if baojia.get('baojia_zhuangtai') == 'accepted' and not baojia.get('is_expired', False):
            accepted_baojia = baojia
    
    # 按钮显示逻辑
    show_quote_button = not has_valid_baojia
    show_view_quote_button = has_valid_baojia
    show_share_quote_button = has_valid_baojia
    show_generate_contract_button = accepted_baojia is not None
    
    print(f"按钮显示状态:")
    print(f"  报价按钮: {'显示' if show_quote_button else '隐藏'}")
    print(f"  查看报价按钮: {'显示' if show_view_quote_button else '隐藏'}")
    print(f"  分享报价按钮: {'显示' if show_share_quote_button else '隐藏'}")
    print(f"  生成合同按钮: {'显示' if show_generate_contract_button else '隐藏'}")
    
    return show_generate_contract_button

def main():
    print("=== 测试报价到合同的完整流程 ===")
    
    # 1. 登录
    print("\n1. 登录系统...")
    token = login()
    if not token:
        print("登录失败，退出测试")
        return
    print("✅ 登录成功")
    
    # 2. 获取线索列表
    print("\n2. 获取线索列表...")
    xiansuo_data = fetch_xiansuo_list(token)
    if not xiansuo_data or not xiansuo_data.get('items'):
        print("❌ 获取线索列表失败")
        return
    
    xiansuo_list = xiansuo_data['items']
    print(f"✅ 获取到 {len(xiansuo_list)} 个线索")
    
    # 3. 选择一个线索进行测试
    test_xiansuo = None
    for xiansuo in xiansuo_list[:5]:  # 只检查前5个线索
        baojia_list = fetch_baojia_by_xiansuo(token, xiansuo['id'])
        
        # 检查当前按钮显示状态
        show_contract_button = check_button_display_logic(xiansuo, baojia_list)
        
        # 如果没有已确认的报价，选择这个线索进行测试
        if not show_contract_button:
            test_xiansuo = xiansuo
            break
    
    if not test_xiansuo:
        print("\n❌ 没有找到合适的测试线索（所有线索都已有确认的报价）")
        return
    
    print(f"\n3. 选择线索进行测试: {test_xiansuo.get('gongsi_mingcheng', 'N/A')}")
    
    # 4. 创建报价
    print("\n4. 创建报价...")
    baojia = create_baojia(token, test_xiansuo['id'])
    if not baojia:
        print("❌ 创建报价失败")
        return
    print(f"✅ 报价创建成功: {baojia.get('baojia_mingcheng', 'N/A')}")
    
    # 5. 检查创建报价后的按钮状态
    print("\n5. 检查创建报价后的按钮状态...")
    baojia_list = fetch_baojia_by_xiansuo(token, test_xiansuo['id'])
    show_contract_button = check_button_display_logic(test_xiansuo, baojia_list)
    
    if show_contract_button:
        print("❌ 错误：报价未确认时不应显示生成合同按钮")
    else:
        print("✅ 正确：报价未确认时不显示生成合同按钮")
    
    # 6. 确认报价
    print("\n6. 确认报价...")
    confirmed_baojia = confirm_baojia(token, baojia['id'])
    if not confirmed_baojia:
        print("❌ 确认报价失败")
        return
    print(f"✅ 报价确认成功: {confirmed_baojia.get('baojia_zhuangtai', 'N/A')}")
    
    # 7. 检查确认报价后的按钮状态
    print("\n7. 检查确认报价后的按钮状态...")
    baojia_list = fetch_baojia_by_xiansuo(token, test_xiansuo['id'])
    show_contract_button = check_button_display_logic(test_xiansuo, baojia_list)
    
    if show_contract_button:
        print("✅ 正确：报价确认后显示生成合同按钮")
    else:
        print("❌ 错误：报价确认后应该显示生成合同按钮")
    
    print("\n=== 测试完成 ===")
    print(f"结论: 生成合同按钮 {'正常工作' if show_contract_button else '存在问题'}")

if __name__ == "__main__":
    main()