#!/usr/bin/env python3
"""
调试合同预览404错误
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
    if response.status_code == 200:
        data = response.json()
        return data.get("token", {}).get("access_token")
    return None

def get_quote_detail(token, quote_id):
    """获取报价详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/lead-quotes/{quote_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取报价失败: {response.status_code}")
        print(response.text)
        return None

def check_customer_exists(token, customer_id):
    """检查客户是否存在"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )
    print(f"\n检查客户 {customer_id}:")
    print(f"  状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 客户存在: {data.get('gongsi_mingcheng')}")
        return True
    else:
        print("  ❌ 客户不存在")
        print(f"  错误: {response.text}")
        return False

def get_lead_detail(token, lead_id):
    """获取线索详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/leads/{lead_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取线索失败: {response.status_code}")
        return None

def main():
    print("=" * 70)
    print("调试合同预览404错误 - 客户不存在问题")
    print("=" * 70)
    
    # 1. 登录
    print("\n1. 登录系统...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✅ 登录成功")
    
    # 2. 获取报价列表
    print("\n2. 获取报价列表...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/lead-quotes",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    
    if response.status_code != 200:
        print(f"❌ 获取报价列表失败: {response.status_code}")
        return
    
    quotes_data = response.json()
    quotes = quotes_data.get("items", [])
    
    if not quotes:
        print("❌ 没有找到报价记录")
        return
    
    print(f"✅ 找到 {len(quotes)} 个报价")
    
    # 3. 检查第一个报价的详细信息
    quote = quotes[0]
    quote_id = quote.get("id")
    print(f"\n3. 检查报价详情: {quote.get('baojia_mingcheng')}")
    print(f"   报价ID: {quote_id}")
    
    quote_detail = get_quote_detail(token, quote_id)
    if not quote_detail:
        print("❌ 无法获取报价详情")
        return
    
    print("\n报价详情结构:")
    print(json.dumps(quote_detail, indent=2, ensure_ascii=False, default=str)[:1000])
    
    # 4. 检查线索信息
    xiansuo_info = quote_detail.get("xiansuo_info", {})
    print("\n4. 线索信息:")
    print(f"   线索ID: {xiansuo_info.get('id')}")
    print(f"   公司名称: {xiansuo_info.get('gongsi_mingcheng')}")
    print(f"   客户ID (kehu_id): {xiansuo_info.get('kehu_id')}")
    
    kehu_id = xiansuo_info.get('kehu_id')
    
    if not kehu_id:
        print("\n⚠️  问题发现：线索没有关联的客户ID (kehu_id为None)")
        print("   这就是为什么合同预览会返回404 '客户不存在'")
        
        # 获取线索详情
        lead_id = xiansuo_info.get('id')
        if lead_id:
            print("\n5. 获取线索详细信息...")
            lead_detail = get_lead_detail(token, lead_id)
            if lead_detail:
                print("\n线索详细信息:")
                print(f"   公司名称: {lead_detail.get('gongsi_mingcheng')}")
                print(f"   联系人: {lead_detail.get('lianxi_ren')}")
                print(f"   联系电话: {lead_detail.get('lianxi_dianhua')}")
                print(f"   客户ID: {lead_detail.get('kehu_id')}")
                print(f"   是否转化: {lead_detail.get('shi_zhuanhua')}")
                
                if lead_detail.get('shi_zhuanhua') == 'N':
                    print("\n💡 解决方案：")
                    print("   线索尚未转化为客户，需要实现以下功能：")
                    print("   1. 在创建线索时自动创建对应的客户记录")
                    print("   2. 或者在生成合同前检查并自动创建客户")
    else:
        print("\n5. 检查客户是否真的存在...")
        exists = check_customer_exists(token, kehu_id)
        
        if not exists:
            print("\n⚠️  问题发现：线索有kehu_id，但数据库中不存在该客户")
            print("   可能的原因：")
            print("   1. 客户被删除了")
            print("   2. kehu_id是错误的值")
            print("   3. 数据不一致")
    
    print("\n" + "=" * 70)
    print("调试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()

