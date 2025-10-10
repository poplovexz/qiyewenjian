#!/usr/bin/env python3
"""
合同API最终综合测试脚本
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

class FinalContractTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_info = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
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
    
    def test_api_endpoint(self, name, method, url, data=None, expected_status=200):
        """通用API测试方法"""
        print(f"\n🧪 测试 {name}...")
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 检查状态码
            if response.status_code == expected_status:
                result = response.json() if response.content else {}
                print(f"✅ {name} 成功")
                
                # 记录测试结果
                self.test_results["tests"][name] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "response": result
                }
                
                return result
            else:
                print(f"❌ {name} 失败: 状态码 {response.status_code}")
                self.test_results["tests"][name] = {
                    "status": "failed",
                    "status_code": response.status_code,
                    "error": response.text
                }
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} 失败: {e}")
            self.test_results["tests"][name] = {
                "status": "error",
                "error": str(e)
            }
            return None
    
    def run_all_contract_tests(self):
        """运行所有合同相关测试"""
        print("🚀 开始合同API最终综合测试...")
        print("=" * 70)
        
        # 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 1. 测试合同模板相关API
        print("\n📋 测试合同模板相关API...")
        self.test_api_endpoint("获取合同模板列表", "GET", f"{BASE_URL}/contract-templates/")
        
        # 2. 测试合同乙方主体相关API
        print("\n🏢 测试合同乙方主体相关API...")
        self.test_api_endpoint("获取乙方主体列表", "GET", f"{BASE_URL}/contract-parties/")
        
        # 3. 测试合同支付方式相关API
        print("\n💳 测试合同支付方式相关API...")
        self.test_api_endpoint("获取支付方式列表", "GET", f"{BASE_URL}/contract-payment-methods/")
        
        # 4. 测试合同相关API
        print("\n📄 测试合同相关API...")
        contracts_result = self.test_api_endpoint("获取合同列表", "GET", f"{BASE_URL}/contracts/")
        
        # 如果有合同，测试获取详情
        if contracts_result and contracts_result.get('items'):
            first_contract = contracts_result['items'][0]
            contract_id = first_contract['id']
            
            self.test_api_endpoint(
                "获取合同详情", 
                "GET", 
                f"{BASE_URL}/contracts/{contract_id}"
            )
        
        # 5. 测试线索报价相关API
        print("\n💰 测试线索报价相关API...")
        quotes_result = self.test_api_endpoint("获取报价列表", "GET", f"{BASE_URL}/lead-quotes/")
        
        # 如果有报价，测试报价详情和从报价获取合同
        if quotes_result and quotes_result.get('items'):
            first_quote = quotes_result['items'][0]
            quote_id = first_quote['id']
            
            self.test_api_endpoint(
                "获取报价详情", 
                "GET", 
                f"{BASE_URL}/lead-quotes/{quote_id}"
            )
            
            # 测试根据报价获取合同
            self.test_api_endpoint(
                "根据报价获取合同", 
                "GET", 
                f"{BASE_URL}/contracts/by-quote/{quote_id}"
            )
        
        # 6. 测试客户相关API
        print("\n👥 测试客户相关API...")
        customers_result = self.test_api_endpoint("获取客户列表", "GET", f"{BASE_URL}/customers/")
        
        # 7. 测试线索相关API
        print("\n🎯 测试线索相关API...")
        leads_result = self.test_api_endpoint("获取线索列表", "GET", f"{BASE_URL}/leads/")
        
        # 8. 测试产品相关API
        print("\n🛍️ 测试产品相关API...")
        self.test_api_endpoint("获取产品分类列表", "GET", f"{BASE_URL}/product-categories/")
        self.test_api_endpoint("获取产品项目列表", "GET", f"{BASE_URL}/product-items/")
        
        # 9. 测试报价产品数据API
        print("\n📊 测试报价产品数据API...")
        self.test_api_endpoint("获取报价产品数据", "GET", f"{BASE_URL}/lead-quotes/product-data")
        
        # 10. 测试健康检查
        print("\n🏥 测试系统健康检查...")
        self.test_api_endpoint("系统健康检查", "GET", f"{BASE_URL.replace('/api/v1', '')}/health")
        
        # 保存测试结果
        self.save_test_results()
        
        print("\n" + "=" * 70)
        print("✅ 合同API最终综合测试完成!")
        
        # 统计测试结果
        total_tests = len(self.test_results["tests"])
        success_tests = len([t for t in self.test_results["tests"].values() if t["status"] == "success"])
        failed_tests = total_tests - success_tests
        
        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功: {success_tests}")
        print(f"   失败: {failed_tests}")
        print(f"   成功率: {(success_tests/total_tests*100):.1f}%")
        
        return failed_tests == 0
    
    def save_test_results(self):
        """保存测试结果"""
        try:
            with open('/tmp/contracts_final_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 测试结果已保存到: /tmp/contracts_final_test_results.json")
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")

def main():
    """主函数"""
    tester = FinalContractTester()
    
    # 运行测试
    success = tester.run_all_contract_tests()
    
    if success:
        print("\n🎉 所有测试完成且全部通过!")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
