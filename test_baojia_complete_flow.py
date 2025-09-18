#!/usr/bin/env python3
"""
报价单创建功能完整性测试
测试从选择线索到创建报价的完整流程
"""
import requests
import json
from datetime import datetime, timedelta

# 配置
API_BASE = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "yonghu_ming": "admin",
    "mima": "admin123"
}

class BaojiaCompleteFlowTest:
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
            print(f"❌ 登录失败: {response.status_code}")
            return False
    
    def test_complete_baojia_flow(self):
        """测试完整的报价创建流程"""
        print("\n🚀 开始完整报价流程测试")
        print("=" * 60)
        
        # 步骤1：获取线索列表
        print("📋 步骤1：获取线索列表")
        response = self.session.get(f"{API_BASE}/api/v1/leads/")
        if response.status_code != 200:
            print(f"❌ 获取线索列表失败: {response.status_code}")
            return False
        
        xiansuo_list = response.json().get("items", [])
        if not xiansuo_list:
            print("❌ 没有可用的线索")
            return False
        
        xiansuo = xiansuo_list[0]
        print(f"✅ 选择线索: {xiansuo['gongsi_mingcheng']} (联系人: {xiansuo['lianxi_ren']})")
        
        # 步骤2：获取产品数据
        print("\n🛍️ 步骤2：获取产品数据")
        response = self.session.get(f"{API_BASE}/api/v1/lead-quotes/product-data")
        if response.status_code != 200:
            print(f"❌ 获取产品数据失败: {response.status_code}")
            return False
        
        chanpin_data = response.json()
        print("✅ 产品数据获取成功")
        print(f"   - 代理记账项目: {len(chanpin_data.get('daili_jizhang_xiangmu', []))} 个")
        print(f"   - 增值服务项目: {len(chanpin_data.get('zengzhi_xiangmu', []))} 个")
        
        # 步骤3：构建报价数据（包含所有必需字段）
        print("\n📝 步骤3：构建完整报价数据")
        
        # 选择多个服务项目
        xiangmu_list = []
        
        # 添加代理记账服务
        daili_items = chanpin_data.get("daili_jizhang_xiangmu", [])
        if daili_items:
            for i, item in enumerate(daili_items[:2]):  # 选择前2个
                xiangmu_list.append({
                    "chanpin_xiangmu_id": item["id"],
                    "xiangmu_mingcheng": item["xiangmu_mingcheng"],
                    "shuliang": i + 1,  # 数量递增
                    "danjia": float(item.get("yewu_baojia", 1000)) + (i * 200),  # 单价递增
                    "danwei": item.get("baojia_danwei", "yuan"),
                    "paixu": i,
                    "beizhu": f"代理记账服务项目{i+1}"
                })
        
        # 添加增值服务
        zengzhi_items = chanpin_data.get("zengzhi_xiangmu", [])
        if zengzhi_items:
            for i, item in enumerate(zengzhi_items[:2]):  # 选择前2个
                xiangmu_list.append({
                    "chanpin_xiangmu_id": item["id"],
                    "xiangmu_mingcheng": item["xiangmu_mingcheng"],
                    "shuliang": 1,
                    "danjia": float(item.get("yewu_baojia", 500)),
                    "danwei": item.get("baojia_danwei", "yuan"),
                    "paixu": len(xiangmu_list),
                    "beizhu": f"增值服务项目{i+1}"
                })
        
        if not xiangmu_list:
            print("❌ 没有可用的服务项目")
            return False
        
        # 构建完整的报价数据
        youxiao_qi = datetime.now() + timedelta(days=15)
        baojia_data = {
            "xiansuo_id": xiansuo["id"],
            "baojia_mingcheng": f"{xiansuo['gongsi_mingcheng']}专业服务报价单",
            "youxiao_qi": youxiao_qi.isoformat(),
            "beizhu": "这是一份完整的专业服务报价单，包含代理记账和增值服务项目。",
            "xiangmu_list": xiangmu_list
        }
        
        print(f"✅ 报价数据构建完成，包含 {len(xiangmu_list)} 个服务项目")
        
        # 计算预期总金额
        expected_total = sum(item["shuliang"] * item["danjia"] for item in xiangmu_list)
        print(f"💰 预期总金额: ¥{expected_total:.2f}")
        
        # 步骤4：创建报价
        print("\n📋 步骤4：创建报价")
        response = self.session.post(
            f"{API_BASE}/api/v1/lead-quotes/",
            json=baojia_data
        )
        
        if response.status_code != 200:
            print(f"❌ 报价创建失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
        
        baojia = response.json()
        print(f"✅ 报价创建成功")
        print(f"   - 报价编码: {baojia['baojia_bianma']}")
        print(f"   - 报价名称: {baojia['baojia_mingcheng']}")
        print(f"   - 有效期: {baojia['youxiao_qi']}")
        print(f"   - 报价状态: {baojia['baojia_zhuangtai']}")
        print(f"   - 总金额: ¥{baojia['zongji_jine']}")
        
        # 步骤5：验证金额计算
        print("\n🧮 步骤5：验证金额计算")
        actual_total = float(baojia['zongji_jine'])
        
        if abs(expected_total - actual_total) < 0.01:
            print("✅ 总金额计算正确")
        else:
            print(f"❌ 总金额计算错误: 预期 ¥{expected_total:.2f}, 实际 ¥{actual_total:.2f}")
            return False
        
        # 验证每个项目的小计
        print("📊 项目明细验证:")
        for item in baojia.get("xiangmu_list", []):
            expected_xiaoji = float(item["shuliang"]) * float(item["danjia"])
            actual_xiaoji = float(item["xiaoji"])
            
            if abs(expected_xiaoji - actual_xiaoji) < 0.01:
                status = "✅"
            else:
                status = "❌"
                
            print(f"   {status} {item['xiangmu_mingcheng']}: {item['shuliang']} × ¥{item['danjia']} = ¥{item['xiaoji']}")
        
        # 步骤6：验证报价状态管理
        print("\n📈 步骤6：验证报价状态管理")
        
        # 测试状态更新
        status_update_data = {
            "baojia_zhuangtai": "sent"
        }
        
        response = self.session.patch(
            f"{API_BASE}/api/v1/lead-quotes/{baojia['id']}/status",
            json=status_update_data
        )
        
        if response.status_code == 200:
            updated_baojia = response.json()
            print(f"✅ 状态更新成功: {updated_baojia['baojia_zhuangtai']}")
        else:
            print(f"⚠️ 状态更新失败: {response.status_code}")
        
        # 步骤7：获取报价详情验证
        print("\n🔍 步骤7：获取报价详情验证")
        response = self.session.get(f"{API_BASE}/api/v1/lead-quotes/{baojia['id']}")
        
        if response.status_code == 200:
            detail_baojia = response.json()
            print("✅ 报价详情获取成功")
            print(f"   - 项目数量: {len(detail_baojia.get('xiangmu_list', []))}")
            print(f"   - 是否过期: {detail_baojia.get('is_expired', False)}")
        else:
            print(f"❌ 获取报价详情失败: {response.status_code}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 完整报价流程测试成功！")
        print(f"📋 报价编码: {baojia['baojia_bianma']}")
        print(f"💰 总金额: ¥{baojia['zongji_jine']}")
        print(f"📊 服务项目: {len(baojia.get('xiangmu_list', []))} 个")
        
        return True
    
    def run_test(self):
        """运行测试"""
        if not self.login():
            return False
        
        return self.test_complete_baojia_flow()

def main():
    """主函数"""
    test = BaojiaCompleteFlowTest()
    success = test.run_test()
    
    if success:
        print("\n✅ 所有测试通过 - 报价创建功能完整性验证成功")
        exit(0)
    else:
        print("\n❌ 测试失败")
        exit(1)

if __name__ == "__main__":
    main()
