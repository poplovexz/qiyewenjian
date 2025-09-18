#!/usr/bin/env python3
"""
报价功能完整性测试脚本
测试报价创建、数量单价计算、总金额等功能
"""
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# 配置
API_BASE = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "yonghu_ming": "admin",
    "mima": "admin123"
}

class BaojiaTestClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
    
    def login(self):
        """登录获取token"""
        print("🔐 正在登录...")
        response = self.session.post(
            f"{API_BASE}/api/v1/auth/login",
            json=ADMIN_CREDENTIALS
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]["access_token"]
            self.user_info = data["user"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print(f"✅ 登录成功: {self.user_info['xingming']}")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False
    
    def get_xiansuo_list(self):
        """获取线索列表"""
        print("📋 获取线索列表...")
        response = self.session.get(f"{API_BASE}/api/v1/leads/")

        if response.status_code == 200:
            data = response.json()
            xiansuo_list = data.get("items", [])
            print(f"✅ 获取到 {len(xiansuo_list)} 个线索")
            return xiansuo_list
        else:
            print(f"❌ 获取线索列表失败: {response.status_code}")
            return []
    
    def get_chanpin_data(self):
        """获取产品数据"""
        print("🛍️ 获取产品数据...")
        response = self.session.get(f"{API_BASE}/api/v1/lead-quotes/product-data")

        if response.status_code == 200:
            data = response.json()
            print("✅ 获取产品数据成功")
            return data
        else:
            print(f"❌ 获取产品数据失败: {response.status_code}")
            return None
    
    def create_test_baojia(self, xiansuo_id, chanpin_data):
        """创建测试报价"""
        print("📝 创建测试报价...")
        
        # 选择一些产品项目
        xiangmu_list = []
        
        # 从代理记账分类中选择项目
        daili_jizhang_items = chanpin_data.get("daili_jizhang_xiangmu", [])
        if daili_jizhang_items:
            item = daili_jizhang_items[0]
            xiangmu_list.append({
                "chanpin_xiangmu_id": item["id"],
                "xiangmu_mingcheng": item["xiangmu_mingcheng"],
                "shuliang": 2,  # 测试数量
                "danjia": 1500.00,  # 测试单价
                "danwei": item.get("baojia_danwei", "yuan"),
                "paixu": 0,
                "beizhu": "测试项目1"
            })
        
        # 从增值服务分类中选择项目
        zengzhi_items = chanpin_data.get("zengzhi_xiangmu", [])
        if zengzhi_items:
            item = zengzhi_items[0]
            xiangmu_list.append({
                "chanpin_xiangmu_id": item["id"],
                "xiangmu_mingcheng": item["xiangmu_mingcheng"],
                "shuliang": 1,  # 测试数量
                "danjia": 800.00,  # 测试单价
                "danwei": item.get("baojia_danwei", "yuan"),
                "paixu": 1,
                "beizhu": "测试项目2"
            })
        
        if not xiangmu_list:
            print("❌ 没有可用的产品项目")
            return None
        
        # 创建报价数据
        youxiao_qi = datetime.now() + timedelta(days=15)
        baojia_data = {
            "xiansuo_id": xiansuo_id,
            "baojia_mingcheng": "测试报价单",
            "youxiao_qi": youxiao_qi.isoformat(),
            "beizhu": "这是一个测试报价单，用于验证数量和单价功能",
            "xiangmu_list": xiangmu_list
        }
        
        print(f"📊 报价数据: {json.dumps(baojia_data, indent=2, ensure_ascii=False)}")
        
        response = self.session.post(
            f"{API_BASE}/api/v1/lead-quotes/",
            json=baojia_data
        )
        
        if response.status_code == 200:
            baojia = response.json()
            print(f"✅ 报价创建成功: {baojia['baojia_bianma']}")
            print(f"💰 总金额: ¥{baojia['zongji_jine']}")
            
            # 验证计算
            expected_total = sum(item["shuliang"] * item["danjia"] for item in xiangmu_list)
            actual_total = float(baojia['zongji_jine'])
            
            print(f"🧮 计算验证:")
            print(f"   预期总金额: ¥{expected_total}")
            print(f"   实际总金额: ¥{actual_total}")
            
            if abs(expected_total - actual_total) < 0.01:
                print("✅ 金额计算正确")
            else:
                print("❌ 金额计算错误")
            
            # 验证项目详情
            print("📋 项目详情:")
            for item in baojia.get("xiangmu_list", []):
                xiaoji = float(item["shuliang"]) * float(item["danjia"])
                print(f"   - {item['xiangmu_mingcheng']}: {item['shuliang']} × ¥{item['danjia']} = ¥{item['xiaoji']} (预期: ¥{xiaoji})")
            
            return baojia
        else:
            print(f"❌ 报价创建失败: {response.status_code} - {response.text}")
            return None
    
    def get_baojia_detail(self, baojia_id):
        """获取报价详情"""
        print(f"🔍 获取报价详情: {baojia_id}")
        response = self.session.get(f"{API_BASE}/api/v1/lead-quotes/{baojia_id}")

        if response.status_code == 200:
            baojia = response.json()
            print("✅ 获取报价详情成功")
            return baojia
        else:
            print(f"❌ 获取报价详情失败: {response.status_code}")
            return None
    
    def run_test(self):
        """运行完整测试"""
        print("🚀 开始报价功能测试")
        print("=" * 50)
        
        # 1. 登录
        if not self.login():
            return False
        
        # 2. 获取线索列表
        xiansuo_list = self.get_xiansuo_list()
        if not xiansuo_list:
            print("❌ 没有可用的线索")
            return False
        
        xiansuo = xiansuo_list[0]
        print(f"📍 使用线索: {xiansuo['gongsi_mingcheng']}")
        
        # 3. 获取产品数据
        chanpin_data = self.get_chanpin_data()
        if not chanpin_data:
            return False
        
        # 4. 创建测试报价
        baojia = self.create_test_baojia(xiansuo["id"], chanpin_data)
        if not baojia:
            return False
        
        # 5. 验证报价详情
        baojia_detail = self.get_baojia_detail(baojia["id"])
        if not baojia_detail:
            return False
        
        print("=" * 50)
        print("🎉 报价功能测试完成")
        return True

def main():
    """主函数"""
    client = BaojiaTestClient()
    success = client.run_test()
    
    if success:
        print("✅ 所有测试通过")
        exit(0)
    else:
        print("❌ 测试失败")
        exit(1)

if __name__ == "__main__":
    main()
