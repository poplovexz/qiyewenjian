#!/usr/bin/env python3
"""
合同API测试脚本
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

class ContractAPITester:
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
            print(f"🔑 Token: {self.access_token[:20]}...")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 登录失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return False
    
    def test_contract_templates_list(self):
        """测试获取合同模板列表"""
        print("\n📋 测试获取合同模板列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/contract-templates/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取合同模板列表成功")
            print(f"📊 总数: {result.get('total', 0)}")
            
            if result.get('items'):
                print("📝 模板列表:")
                for template in result['items'][:3]:  # 只显示前3个
                    print(f"  - {template['moban_mingcheng']} ({template['hetong_leixing']})")
                    
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取合同模板列表失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_contracts_list(self):
        """测试获取合同列表"""
        print("\n📋 测试获取合同列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/contracts/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取合同列表成功")
            print(f"📊 总数: {result.get('total', 0)}")
            
            if result.get('items'):
                print("📄 合同列表:")
                for contract in result['items'][:3]:  # 只显示前3个
                    print(f"  - {contract['hetong_mingcheng']} ({contract['hetong_zhuangtai']})")
                    
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取合同列表失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_contract_parties_list(self):
        """测试获取合同乙方主体列表"""
        print("\n🏢 测试获取合同乙方主体列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/contract-parties/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取乙方主体列表成功")
            print(f"📊 总数: {result.get('total', 0)}")
            
            if result.get('items'):
                print("🏢 乙方主体列表:")
                for party in result['items'][:3]:  # 只显示前3个
                    print(f"  - {party['zhuti_mingcheng']} ({party['zhuti_leixing']})")
                    
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取乙方主体列表失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_contract_payment_methods_list(self):
        """测试获取合同支付方式列表"""
        print("\n💳 测试获取合同支付方式列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/contract-payment-methods/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取支付方式列表成功")
            print(f"📊 总数: {result.get('total', 0)}")
            
            if result.get('items'):
                print("💳 支付方式列表:")
                for method in result['items'][:3]:  # 只显示前3个
                    print(f"  - {method['zhanghu_mingcheng']} ({method['zhifu_fangshi']})")
                    
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取支付方式列表失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def save_response_to_file(self, data, filename):
        """保存响应数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 响应数据已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始合同API测试...")
        print("=" * 50)
        
        # 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 测试各个API
        templates_result = self.test_contract_templates_list()
        contracts_result = self.test_contracts_list()
        parties_result = self.test_contract_parties_list()
        payment_methods_result = self.test_contract_payment_methods_list()
        
        # 保存结果到文件
        if contracts_result:
            self.save_response_to_file(contracts_result, '/tmp/contracts_response.json')
        
        print("\n" + "=" * 50)
        print("✅ 合同API测试完成!")
        
        return True

def main():
    """主函数"""
    tester = ContractAPITester()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
        print(f"使用自定义用户: {username}")
    else:
        username = "admin"
        password = "admin123"
        print("使用默认用户: admin")
    
    # 运行测试
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试完成!")
        sys.exit(0)
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
