#!/usr/bin/env python3
"""
简化的按钮显示逻辑测试
只检查现有线索的按钮显示状态
"""

import requests
import json

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

def check_button_display_logic(xiansuo, baojia_list):
    """检查按钮显示逻辑"""
    print(f"\n=== 线索: {xiansuo.get('gongsi_mingcheng', 'N/A')} (ID: {xiansuo['id']}) ===")
    print(f"线索状态: {xiansuo.get('xiansuo_zhuangtai', 'N/A')}")
    print(f"报价数量: {len(baojia_list)}")
    
    # 检查是否有有效报价
    has_valid_baojia = False
    accepted_baojia = None
    pending_baojia = None
    
    for baojia in baojia_list:
        print(f"  报价: {baojia.get('baojia_mingcheng', 'N/A')} - 状态: {baojia.get('baojia_zhuangtai', 'N/A')} - 过期: {baojia.get('is_expired', False)}")
        
        if not baojia.get('is_expired', False) and baojia.get('baojia_zhuangtai') != 'rejected':
            has_valid_baojia = True
            
        if baojia.get('baojia_zhuangtai') == 'accepted' and not baojia.get('is_expired', False):
            accepted_baojia = baojia
            
        if baojia.get('baojia_zhuangtai') == 'pending' and not baojia.get('is_expired', False):
            pending_baojia = baojia
    
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
    
    if accepted_baojia:
        print(f"  ✅ 发现已确认报价: {accepted_baojia.get('baojia_mingcheng', 'N/A')}")
        print(f"  ✅ 生成合同按钮应该显示")
    elif pending_baojia:
        print(f"  ⏳ 发现待确认报价: {pending_baojia.get('baojia_mingcheng', 'N/A')}")
        print(f"  ⏳ 生成合同按钮暂不显示，需要先确认报价")
    else:
        print(f"  ❌ 没有已确认的报价，生成合同按钮不显示")
    
    return show_generate_contract_button

def main():
    print("=== 检查线索按钮显示逻辑 ===")
    
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
    
    # 3. 检查每个线索的按钮显示状态
    print("\n3. 检查线索按钮显示状态...")
    
    contract_button_count = 0
    total_checked = 0
    
    for xiansuo in xiansuo_list[:10]:  # 只检查前10个线索
        baojia_list = fetch_baojia_by_xiansuo(token, xiansuo['id'])
        show_contract_button = check_button_display_logic(xiansuo, baojia_list)
        
        if show_contract_button:
            contract_button_count += 1
        total_checked += 1
    
    print(f"\n=== 检查结果汇总 ===")
    print(f"总共检查线索数: {total_checked}")
    print(f"显示生成合同按钮的线索数: {contract_button_count}")
    print(f"按钮显示逻辑: {'正常' if contract_button_count > 0 else '可能存在问题'}")
    
    if contract_button_count == 0:
        print("\n⚠️  没有线索显示生成合同按钮")
        print("   这可能是因为:")
        print("   1. 所有线索都没有已确认的报价")
        print("   2. getBaojiaStatus函数存在问题")
        print("   3. canGenerateContract函数逻辑有误")
    else:
        print(f"\n✅ 有 {contract_button_count} 个线索正确显示生成合同按钮")

if __name__ == "__main__":
    main()