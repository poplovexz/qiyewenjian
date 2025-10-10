#!/usr/bin/env python3
"""
测试线索XS005的合同情况
"""
import requests
import json
import sys

def test_xs005_contract():
    """测试线索XS005的合同情况"""
    print("🔍 测试线索XS005的合同情况...")
    
    # 模拟登录
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {"yonghu_ming": "admin", "mima": "admin123"}
    
    try:
        # 登录
        print("🔐 正在登录...")
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            return False
            
        token_data = response.json()
        access_token = token_data.get('access_token') or token_data.get('token', {}).get('access_token')
        
        if not access_token:
            print("❌ 无法获取访问令牌")
            return False
            
        headers = {'Authorization': f'Bearer {access_token}'}
        print("✅ 登录成功")
        
        # 1. 查找线索XS005
        print("\n🔍 查找线索XS005...")
        leads_response = requests.get("http://localhost:8000/api/v1/leads/", headers=headers)
        if leads_response.status_code != 200:
            print(f"❌ 获取线索列表失败: {leads_response.status_code}")
            return False
            
        leads_data = leads_response.json()
        xs005_lead = None
        
        for lead in leads_data.get('items', []):
            if lead.get('xiansuo_bianhao') == 'XS005':
                xs005_lead = lead
                break
        
        if not xs005_lead:
            print("❌ 未找到线索XS005")
            print("📋 系统中的线索:")
            for lead in leads_data.get('items', [])[:5]:
                print(f"   - {lead.get('xiansuo_bianhao')}: {lead.get('xiansuo_mingcheng')}")
            return False
            
        print(f"✅ 找到线索XS005: {xs005_lead['xiansuo_mingcheng']}")
        print(f"   线索ID: {xs005_lead['id']}")
        print(f"   线索状态: {xs005_lead['xiansuo_zhuangtai']}")
        
        # 2. 查找该线索的报价
        print(f"\n💰 查找线索XS005的报价...")
        quotes_response = requests.get(f"http://localhost:8000/api/v1/lead-quotes/xiansuo/{xs005_lead['id']}", headers=headers)
        if quotes_response.status_code != 200:
            print(f"❌ 获取报价失败: {quotes_response.status_code}")
            return False
            
        quotes = quotes_response.json()
        
        if not quotes:
            print("❌ 该线索没有报价")
            return False
            
        print(f"✅ 找到 {len(quotes)} 个报价:")
        for i, quote in enumerate(quotes, 1):
            print(f"   报价 {i}: {quote['baojia_bianma']} - {quote['baojia_mingcheng']}")
            print(f"      状态: {quote['baojia_zhuangtai']}")
            print(f"      总金额: {quote['zongji_jine']}")
            
            # 3. 检查每个报价是否有关联的合同
            print(f"      🔍 检查关联合同...")
            contract_response = requests.get(f"http://localhost:8000/api/v1/contracts/by-quote/{quote['id']}", headers=headers)
            
            if contract_response.status_code == 200:
                contract = contract_response.json()
                print(f"      ✅ 找到关联合同:")
                print(f"         合同ID: {contract['id']}")
                print(f"         合同编号: {contract['hetong_bianhao']}")
                print(f"         合同名称: {contract['hetong_mingcheng']}")
                print(f"         合同状态: {contract['hetong_zhuangtai']}")
                print(f"         创建时间: {contract['created_at']}")
            elif contract_response.status_code == 404:
                print(f"      ❌ 该报价没有关联的合同")
            else:
                print(f"      ❌ 检查关联合同失败: {contract_response.status_code}")
            print()
        
        # 4. 获取所有合同列表
        print("📋 获取所有合同列表...")
        contracts_response = requests.get("http://localhost:8000/api/v1/contracts/", headers=headers)
        if contracts_response.status_code != 200:
            print(f"❌ 获取合同列表失败: {contracts_response.status_code}")
            return False
            
        contracts_data = contracts_response.json()
        contracts = contracts_data.get('items', [])
        
        print(f"✅ 系统中共有 {len(contracts)} 个合同:")
        for i, contract in enumerate(contracts, 1):
            print(f"   {i}. {contract['hetong_bianhao']} - {contract['hetong_mingcheng']}")
            print(f"      状态: {contract['hetong_zhuangtai']}")
            if contract.get('baojia_id'):
                print(f"      关联报价ID: {contract['baojia_id']}")
            print(f"      创建时间: {contract['created_at']}")
            print()
        
        # 5. 分析结果
        print("=" * 60)
        print("📊 分析结果:")
        
        # 检查是否有XS005相关的合同
        xs005_contracts = []
        for contract in contracts:
            if contract.get('baojia_id'):
                for quote in quotes:
                    if quote['id'] == contract['baojia_id']:
                        xs005_contracts.append(contract)
                        break
        
        if xs005_contracts:
            print(f"✅ 找到 {len(xs005_contracts)} 个与线索XS005相关的合同:")
            for contract in xs005_contracts:
                print(f"   - {contract['hetong_bianhao']}: {contract['hetong_mingcheng']} ({contract['hetong_zhuangtai']})")
            
            print("\n🎯 问题解决方案:")
            print("   1. 合同已经存在，请检查合同列表页面的筛选条件")
            print("   2. 可能需要刷新页面或清除浏览器缓存")
            print("   3. 检查合同状态筛选是否包含了这些合同的状态")
        else:
            print("❌ 没有找到与线索XS005相关的合同")
            print("\n🎯 可能的原因:")
            print("   1. 报价状态不是'accepted'，无法生成合同")
            print("   2. 合同生成过程中出现了错误")
            print("   3. 合同被删除了")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_xs005_contract()
    sys.exit(0 if success else 1)
