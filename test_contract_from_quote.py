#!/usr/bin/env python3
"""
测试从报价生成合同的API
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

class ContractFromQuoteTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_info = None
        
    def login(self, username="admin", password="admin123"):
        """用户登录"""
        print(f"🔐 正在登录用户: {username}")
        
        login_data = {
            "yonghu_ming": username,
            "mima": password
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 登录成功: {result['message']}")
            
            # 提取token信息
            if 'token' in result:
                self.access_token = result['token']['access_token']
            elif 'access_token' in result:
                self.access_token = result['access_token']
            else:
                raise Exception("响应中未找到access_token")
                
            self.user_info = result['user']
            
            # 设置认证头
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            print(f"👤 用户信息: {self.user_info['xingming']} ({self.user_info['yonghu_ming']})")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 登录失败: {e}")
            return False
    
    def get_quotes_list(self):
        """获取报价列表"""
        print("\n💰 获取报价列表...")

        try:
            response = self.session.get(f"{BASE_URL}/lead-quotes/")
            response.raise_for_status()

            result = response.json()
            print(f"✅ 获取报价列表成功，总数: {result.get('total', 0)}")

            if result.get('items'):
                print("📋 报价列表:")
                for quote in result['items'][:3]:  # 显示前3个
                    print(f"  - {quote['baojia_bianma']}: {quote['baojia_mingcheng']} ({quote['baojia_zhuangtai']})")

                # 返回第一个已确认的报价ID
                for quote in result['items']:
                    if quote['baojia_zhuangtai'] == 'accepted':
                        print(f"🎯 选择已接受的报价: {quote['baojia_bianma']}")
                        return quote['id']

                # 如果没有已确认的，返回第一个
                print(f"🎯 选择第一个报价: {result['items'][0]['baojia_bianma']}")
                return result['items'][0]['id']

            return None

        except requests.exceptions.RequestException as e:
            print(f"❌ 获取报价列表失败: {e}")
            return None
    
    def test_create_contract_from_quote(self, quote_id):
        """测试从报价生成合同"""
        print(f"\n📄 测试从报价生成合同: {quote_id}")
        
        try:
            response = self.session.post(f"{BASE_URL}/contracts/from-quote/{quote_id}")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 从报价生成合同成功")
            print(f"📄 合同ID: {result['id']}")
            print(f"📄 合同编号: {result['hetong_bianhao']}")
            print(f"📄 合同名称: {result['hetong_mingcheng']}")
            print(f"📄 合同状态: {result['hetong_zhuangtai']}")
            print(f"📄 合同来源: {result['hetong_laiyuan']}")
            print(f"📄 自动生成: {result['zidong_shengcheng']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 从报价生成合同失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_create_contract_from_quote_direct(self, quote_id):
        """测试直接从报价生成合同（支持金额修改）"""
        print(f"\n📄 测试直接从报价生成合同（支持金额修改）: {quote_id}")
        
        request_data = {
            "baojia_id": quote_id,
            "custom_amount": 3000.00,  # 自定义金额
            "change_reason": "客户要求调整服务内容"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/contracts/from-quote-direct", json=request_data)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 直接从报价生成合同成功")
            print(f"📄 合同ID: {result['id']}")
            print(f"📄 合同编号: {result['hetong_bianhao']}")
            print(f"📄 合同名称: {result['hetong_mingcheng']}")
            print(f"📄 合同状态: {result['hetong_zhuangtai']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 直接从报价生成合同失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_get_contract_by_quote(self, quote_id):
        """测试根据报价ID获取合同"""
        print(f"\n🔍 测试根据报价ID获取合同: {quote_id}")
        
        try:
            response = self.session.get(f"{BASE_URL}/contracts/by-quote/{quote_id}")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 根据报价ID获取合同成功")
            print(f"📄 合同ID: {result['id']}")
            print(f"📄 合同编号: {result['hetong_bianhao']}")
            print(f"📄 关联报价ID: {result['baojia_id']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 根据报价ID获取合同失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def save_test_results(self, data):
        """保存测试结果"""
        try:
            with open('/tmp/contract_from_quote_test.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 测试结果已保存到: /tmp/contract_from_quote_test.json")
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")
    
    def run_quote_to_contract_tests(self):
        """运行报价生成合同测试"""
        print("🚀 开始报价生成合同API测试...")
        print("=" * 60)
        
        # 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 获取报价列表
        quote_id = self.get_quotes_list()
        if not quote_id:
            print("❌ 无法获取报价数据")
            return False
        
        test_results = {
            "quote_id": quote_id,
            "tests": {}
        }
        
        # 测试1: 从报价生成合同
        contract1 = self.test_create_contract_from_quote(quote_id)
        if contract1:
            test_results["tests"]["create_from_quote"] = contract1
        
        # 测试2: 直接从报价生成合同（支持金额修改）
        contract2 = self.test_create_contract_from_quote_direct(quote_id)
        if contract2:
            test_results["tests"]["create_from_quote_direct"] = contract2
        
        # 测试3: 根据报价ID获取合同
        existing_contract = self.test_get_contract_by_quote(quote_id)
        if existing_contract:
            test_results["tests"]["get_by_quote"] = existing_contract
        
        # 保存测试结果
        self.save_test_results(test_results)
        
        print("\n" + "=" * 60)
        print("✅ 报价生成合同API测试完成!")
        
        return True

def main():
    """主函数"""
    tester = ContractFromQuoteTester()
    
    # 运行测试
    success = tester.run_quote_to_contract_tests()
    
    if success:
        print("\n🎉 所有测试完成!")
        sys.exit(0)
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
