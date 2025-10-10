#!/usr/bin/env python3
"""
测试报价数据加载和按钮显示逻辑
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

class BaojiaLoadingTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None

    def login(self):
        """登录获取token"""
        print("🔐 正在登录...")
        login_data = {
            "yonghu_ming": "admin",
            "mima": "admin123"
        }
        
        response = self.session.post(f"{API_BASE}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"登录响应: {data}")
            # 尝试不同的字段名
            if "access_token" in data:
                self.access_token = data["access_token"]
            elif "token" in data and isinstance(data["token"], dict) and "access_token" in data["token"]:
                self.access_token = data["token"]["access_token"]
            elif "token" in data and isinstance(data["token"], str):
                self.access_token = data["token"]
            elif "data" in data and "access_token" in data["data"]:
                self.access_token = data["data"]["access_token"]
            else:
                print(f"❌ 无法找到访问令牌，响应数据: {data}")
                return False
            
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False

    def get_xiansuo_list(self):
        """获取线索列表"""
        print("\n📋 获取线索列表...")
        response = self.session.get(f"{API_BASE}/api/v1/leads/")

        if response.status_code == 200:
            data = response.json()
            xiansuo_list = data.get("items", [])
            print(f"✅ 获取到 {len(xiansuo_list)} 个线索")
            
            for xiansuo in xiansuo_list:
                # 打印完整的线索数据以便调试
                print(f"线索数据: {xiansuo}")
                bianhao = xiansuo.get('xiansuo_bianhao', xiansuo.get('id', 'N/A'))
                mingcheng = xiansuo.get('xiansuo_mingcheng', xiansuo.get('gongsi_mingcheng', 'N/A'))
                zhuangtai = xiansuo.get('xiansuo_zhuangtai', xiansuo.get('dangqian_zhuangtai', 'N/A'))
                print(f"   - {bianhao}: {mingcheng} (状态: {zhuangtai})")
            
            return xiansuo_list
        else:
            print(f"❌ 获取线索列表失败: {response.status_code}")
            return []

    def get_baojia_by_xiansuo(self, xiansuo_id):
        """获取指定线索的报价列表"""
        print(f"\n💰 获取线索 {xiansuo_id} 的报价列表...")
        response = self.session.get(f"{API_BASE}/api/v1/lead-quotes/xiansuo/{xiansuo_id}")

        if response.status_code == 200:
            baojia_list = response.json()
            print(f"✅ 获取到 {len(baojia_list)} 个报价")
            
            for baojia in baojia_list:
                print(f"   - {baojia['baojia_bianma']}: {baojia['baojia_mingcheng']}")
                print(f"     状态: {baojia['baojia_zhuangtai']}, 过期: {baojia['is_expired']}")
                print(f"     总金额: ¥{baojia['zongji_jine']}")
            
            return baojia_list
        else:
            print(f"❌ 获取报价列表失败: {response.status_code}")
            return []

    def test_button_logic(self, xiansuo_list):
        """测试按钮显示逻辑"""
        print("\n🔍 测试按钮显示逻辑...")
        
        for xiansuo in xiansuo_list:
            xiansuo_id = xiansuo['id']
            xiansuo_status = xiansuo.get('xiansuo_zhuangtai', xiansuo.get('dangqian_zhuangtai', 'N/A'))
            bianhao = xiansuo.get('xiansuo_bianhao', xiansuo.get('id', 'N/A'))
            mingcheng = xiansuo.get('xiansuo_mingcheng', xiansuo.get('gongsi_mingcheng', 'N/A'))
            
            print(f"\n线索: {bianhao} - {mingcheng}")
            print(f"状态: {xiansuo_status}")
            
            # 获取报价列表
            baojia_list = self.get_baojia_by_xiansuo(xiansuo_id)
            
            # 模拟前端逻辑
            has_valid_baojia = any(
                not baojia['is_expired'] and baojia['baojia_zhuangtai'] != 'rejected'
                for baojia in baojia_list
            ) or xiansuo_status in ['quoted', 'won']
            
            # 获取最新的非过期、非拒绝报价状态
            latest_baojia_status = None
            for baojia in baojia_list:
                if not baojia['is_expired'] and baojia['baojia_zhuangtai'] != 'rejected':
                    latest_baojia_status = baojia['baojia_zhuangtai']
                    break
            
            can_generate_contract = (
                has_valid_baojia and 
                latest_baojia_status == 'accepted'
            )
            
            print(f"   - 有有效报价: {has_valid_baojia}")
            print(f"   - 最新报价状态: {latest_baojia_status}")
            print(f"   - 可生成合同: {can_generate_contract}")
            
            # 按钮显示逻辑
            if not has_valid_baojia:
                print("   → 显示 '报价' 按钮")
            else:
                print("   → 显示 '查看报价' 按钮")
                if can_generate_contract:
                    print("   → 显示 '生成合同' 按钮 ✅")
                else:
                    print("   → 不显示 '生成合同' 按钮 ❌")

    def create_test_baojia(self, xiansuo_id):
        """创建测试报价"""
        print(f"\n📝 为线索 {xiansuo_id} 创建测试报价...")
        
        baojia_data = {
            "xiansuo_id": xiansuo_id,
            "baojia_mingcheng": "测试报价",
            "baojia_leixing": "zengzhi",
            "youxiao_tianshu": 30,
            "beizhu": "测试用报价",
            "xiangmu_list": [
                {
                    "chanpin_xiangmu_id": "test-item-1",
                    "shuliang": 1,
                    "danjia": 1000.00,
                    "danwei": "项",
                    "beizhu": "测试项目"
                }
            ]
        }
        
        response = self.session.post(f"{API_BASE}/api/v1/lead-quotes/", json=baojia_data)
        
        if response.status_code == 200:
            baojia = response.json()
            print(f"✅ 报价创建成功: {baojia['baojia_bianma']}")
            return baojia
        else:
            print(f"❌ 报价创建失败: {response.status_code} - {response.text}")
            return None

    def update_baojia_status(self, baojia_id, status):
        """更新报价状态"""
        print(f"\n🔄 更新报价 {baojia_id} 状态为 {status}...")
        
        response = self.session.put(f"{API_BASE}/api/v1/lead-quotes/{baojia_id}/status", 
                                  json={"baojia_zhuangtai": status})
        
        if response.status_code == 200:
            print(f"✅ 状态更新成功")
            return True
        else:
            print(f"❌ 状态更新失败: {response.status_code} - {response.text}")
            return False

    def run_test(self):
        """运行测试"""
        if not self.login():
            return False
        
        # 获取线索列表
        xiansuo_list = self.get_xiansuo_list()
        if not xiansuo_list:
            print("❌ 没有找到线索数据")
            return False
        
        # 测试按钮逻辑
        self.test_button_logic(xiansuo_list)
        
        print("\n" + "=" * 60)
        print("🎯 测试建议:")
        print("1. 确保线索有 'accepted' 状态的报价才能显示 '生成合同' 按钮")
        print("2. 检查前端 prefetchBaojiaForLeads 方法是否正确调用")
        print("3. 验证前端 store 中的报价数据是否正确缓存")
        
        return True

if __name__ == "__main__":
    test = BaojiaLoadingTest()
    test.run_test()