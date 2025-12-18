#!/usr/bin/env python3
"""
检查线索XS005的合同生成情况
"""
import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def login():
    """用户登录"""
    print("🔐 正在登录...")
    
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()
        
        result = response.json()
        token = result.get('access_token') or result.get('token', {}).get('access_token')
        
        if not token:
            print("❌ 无法获取访问令牌")
            return None
            
        print("✅ 登录成功")
        return token
        
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return None

def find_xiansuo_xs005(headers):
    """查找线索XS005"""
    print("\n🔍 查找线索XS005...")
    
    try:
        response = requests.get(f"{BASE_URL}/leads/", headers=headers)
        response.raise_for_status()
        
        leads = response.json()
        
        for lead in leads.get('items', []):
            if lead.get('xiansuo_bianhao') == 'XS005':
                print("✅ 找到线索XS005:")
                print(f"   线索ID: {lead['id']}")
                print(f"   线索名称: {lead['xiansuo_mingcheng']}")
                print(f"   线索状态: {lead['xiansuo_zhuangtai']}")
                print(f"   客户ID: {lead.get('kehu_id', 'N/A')}")
                return lead
        
        print("❌ 未找到线索XS005")
        return None
        
    except Exception as e:
        print(f"❌ 查找线索失败: {e}")
        return None

def get_xiansuo_quotes(xiansuo_id, headers):
    """获取线索的报价"""
    print("\n💰 查找线索的报价...")
    
    try:
        response = requests.get(f"{BASE_URL}/lead-quotes/xiansuo/{xiansuo_id}", headers=headers)
        response.raise_for_status()
        
        quotes = response.json()
        
        if quotes:
            print(f"✅ 找到 {len(quotes)} 个报价:")
            for i, quote in enumerate(quotes, 1):
                print(f"\n📋 报价 {i}:")
                print(f"   报价ID: {quote['id']}")
                print(f"   报价编码: {quote['baojia_bianma']}")
                print(f"   报价名称: {quote['baojia_mingcheng']}")
                print(f"   报价状态: {quote['baojia_zhuangtai']}")
                print(f"   总金额: {quote['zongji_jine']}")
                print(f"   有效期: {quote['youxiao_qi']}")
        else:
            print("❌ 该线索没有报价")
            
        return quotes
        
    except Exception as e:
        print(f"❌ 获取报价失败: {e}")
        return []

def check_quote_contracts(quotes, headers):
    """检查报价关联的合同"""
    print("\n📄 检查报价关联的合同...")
    
    contracts = []
    
    for quote in quotes:
        quote_id = quote['id']
        print(f"\n🔍 检查报价 {quote['baojia_bianma']} 的关联合同...")
        
        try:
            response = requests.get(f"{BASE_URL}/contracts/by-quote/{quote_id}", headers=headers)
            
            if response.status_code == 200:
                contract = response.json()
                print("   ✅ 找到关联合同:")
                print(f"      合同ID: {contract['id']}")
                print(f"      合同编号: {contract['hetong_bianhao']}")
                print(f"      合同名称: {contract['hetong_mingcheng']}")
                print(f"      合同状态: {contract['hetong_zhuangtai']}")
                print(f"      创建时间: {contract['created_at']}")
                contracts.append(contract)
            elif response.status_code == 404:
                print("   ❌ 该报价没有关联的合同")
            else:
                print(f"   ❌ 检查失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ 检查关联合同失败: {e}")
    
    return contracts

def get_all_contracts(headers):
    """获取所有合同列表"""
    print("\n📋 获取所有合同列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/contracts/", headers=headers)
        response.raise_for_status()
        
        result = response.json()
        contracts = result.get('items', [])
        
        print(f"✅ 系统中共有 {len(contracts)} 个合同:")
        for i, contract in enumerate(contracts, 1):
            print(f"   {i}. {contract['hetong_bianhao']} - {contract['hetong_mingcheng']} ({contract['hetong_zhuangtai']})")
            if contract.get('baojia_id'):
                print(f"      关联报价ID: {contract['baojia_id']}")
        
        return contracts
        
    except Exception as e:
        print(f"❌ 获取合同列表失败: {e}")
        return []

def main():
    """主函数"""
    print("🚀 开始检查线索XS005的合同生成情况...")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        sys.exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 查找线索XS005
    xiansuo = find_xiansuo_xs005(headers)
    if not xiansuo:
        sys.exit(1)
    
    xiansuo_id = xiansuo['id']
    
    # 获取线索的报价
    quotes = get_xiansuo_quotes(xiansuo_id, headers)
    
    # 检查报价关联的合同
    quote_contracts = check_quote_contracts(quotes, headers)
    
    # 获取所有合同列表
    all_contracts = get_all_contracts(headers)
    
    # 分析结果
    print("\n" + "=" * 60)
    print("📊 分析结果:")
    
    if quotes:
        print(f"✅ 线索XS005有 {len(quotes)} 个报价")
        
        if quote_contracts:
            print(f"✅ 找到 {len(quote_contracts)} 个关联合同")
            print("🎯 问题可能原因:")
            print("   1. 合同可能在合同列表的其他页面")
            print("   2. 前端筛选条件可能过滤了该合同")
            print("   3. 合同状态可能不在显示范围内")
        else:
            print("❌ 没有找到关联合同")
            print("🎯 可能的原因:")
            print("   1. 报价状态不是'accepted'，无法生成合同")
            print("   2. 系统在生成合同时出现了错误")
            print("   3. 合同生成后被删除了")
    else:
        print("❌ 线索XS005没有报价，无法生成合同")
    
    print("\n🔧 建议操作:")
    print("   1. 检查报价状态是否为'accepted'")
    print("   2. 检查合同列表的筛选条件")
    print("   3. 检查合同是否在其他页面")
    print("   4. 如果确实没有合同，可以重新从报价生成")

if __name__ == "__main__":
    main()
