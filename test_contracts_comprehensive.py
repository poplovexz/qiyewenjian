#!/usr/bin/env python3
"""
合同API综合测试脚本
"""
import requests
import json
import sys
from datetime import datetime, timedelta
import uuid

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

class ComprehensiveContractTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_info = None
        self.test_data = {}
        
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
    
    def get_customers_list(self):
        """获取客户列表"""
        print("\n👥 获取客户列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/customers/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取客户列表成功，总数: {result.get('total', 0)}")
            
            if result.get('items'):
                self.test_data['customers'] = result['items']
                print(f"📝 第一个客户: {result['items'][0]['gongsi_mingcheng']}")
                return result['items'][0]['id']  # 返回第一个客户ID
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取客户列表失败: {e}")
            return None
    
    def get_contract_templates_list(self):
        """获取合同模板列表"""
        print("\n📋 获取合同模板列表...")
        
        try:
            response = self.session.get(f"{BASE_URL}/contract-templates/")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取合同模板列表成功，总数: {result.get('total', 0)}")
            
            if result.get('items'):
                self.test_data['templates'] = result['items']
                print(f"📝 第一个模板: {result['items'][0]['moban_mingcheng']}")
                return result['items'][0]['id']  # 返回第一个模板ID
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取合同模板列表失败: {e}")
            return None
    
    def test_create_contract(self, kehu_id, template_id):
        """测试创建合同"""
        print("\n📄 测试创建合同...")
        
        # 生成唯一的合同编号
        contract_number = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        contract_data = {
            "kehu_id": kehu_id,
            "hetong_moban_id": template_id,
            "hetong_bianhao": contract_number,
            "hetong_mingcheng": f"测试合同-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "hetong_neirong": "这是一个测试合同的内容",
            "hetong_zhuangtai": "draft",
            "daoqi_riqi": (datetime.now() + timedelta(days=365)).isoformat(),
            "hetong_laiyuan": "manual"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/contracts/", json=contract_data)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 创建合同成功")
            print(f"📄 合同ID: {result['id']}")
            print(f"📄 合同编号: {result['hetong_bianhao']}")
            print(f"📄 合同名称: {result['hetong_mingcheng']}")
            
            self.test_data['created_contract'] = result
            return result['id']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 创建合同失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_get_contract_detail(self, contract_id):
        """测试获取合同详情"""
        print(f"\n📖 测试获取合同详情: {contract_id}")
        
        try:
            response = self.session.get(f"{BASE_URL}/contracts/{contract_id}")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 获取合同详情成功")
            print(f"📄 合同名称: {result['hetong_mingcheng']}")
            print(f"📄 合同状态: {result['hetong_zhuangtai']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取合同详情失败: {e}")
            return None
    
    def test_update_contract(self, contract_id):
        """测试更新合同"""
        print(f"\n✏️ 测试更新合同: {contract_id}")
        
        update_data = {
            "hetong_mingcheng": f"更新后的测试合同-{datetime.now().strftime('%H%M%S')}",
            "hetong_neirong": "这是更新后的合同内容",
            "hetong_zhuangtai": "pending"
        }
        
        try:
            response = self.session.put(f"{BASE_URL}/contracts/{contract_id}", json=update_data)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 更新合同成功")
            print(f"📄 新名称: {result['hetong_mingcheng']}")
            print(f"📄 新状态: {result['hetong_zhuangtai']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 更新合同失败: {e}")
            return None
    
    def test_contract_preview(self, template_id, kehu_id):
        """测试合同预览"""
        print(f"\n👁️ 测试合同预览...")
        
        preview_data = {
            "hetong_moban_id": template_id,
            "kehu_id": kehu_id,
            "bianliang_zhis": {
                "fuwu_feiyong": "2000",
                "zhifu_fangshi": "月付",
                "kaishi_riqi": datetime.now().strftime('%Y-%m-%d'),
                "jieshu_riqi": (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            }
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/contracts/preview", json=preview_data)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 合同预览成功")
            print(f"📄 预览内容长度: {len(result.get('hetong_neirong', ''))}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 合同预览失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None
    
    def test_delete_contract(self, contract_id):
        """测试删除合同"""
        print(f"\n🗑️ 测试删除合同: {contract_id}")
        
        try:
            response = self.session.delete(f"{BASE_URL}/contracts/{contract_id}")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ 删除合同成功: {result.get('message', '删除成功')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 删除合同失败: {e}")
            return False
    
    def save_test_results(self):
        """保存测试结果"""
        try:
            with open('/tmp/contracts_comprehensive_test.json', 'w', encoding='utf-8') as f:
                json.dump(self.test_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 测试结果已保存到: /tmp/contracts_comprehensive_test.json")
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")
    
    def run_comprehensive_tests(self):
        """运行综合测试"""
        print("🚀 开始合同API综合测试...")
        print("=" * 60)
        
        # 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 获取测试数据
        kehu_id = self.get_customers_list()
        template_id = self.get_contract_templates_list()
        
        if not kehu_id or not template_id:
            print("❌ 无法获取必要的测试数据")
            return False
        
        # 测试合同预览
        self.test_contract_preview(template_id, kehu_id)
        
        # 测试创建合同
        contract_id = self.test_create_contract(kehu_id, template_id)
        if not contract_id:
            print("❌ 创建合同失败，跳过后续测试")
            return False
        
        # 测试获取合同详情
        self.test_get_contract_detail(contract_id)
        
        # 测试更新合同
        self.test_update_contract(contract_id)
        
        # 再次获取详情确认更新
        self.test_get_contract_detail(contract_id)
        
        # 测试删除合同
        self.test_delete_contract(contract_id)
        
        # 保存测试结果
        self.save_test_results()
        
        print("\n" + "=" * 60)
        print("✅ 合同API综合测试完成!")
        
        return True

def main():
    """主函数"""
    tester = ComprehensiveContractTester()
    
    # 运行测试
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 所有测试完成!")
        sys.exit(0)
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
