#!/usr/bin/env python3
"""
客户管理模块完整功能测试
测试客户管理和服务记录管理的所有功能
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 测试数据
TEST_CUSTOMER = {
    "gongsi_mingcheng": "测试科技有限公司",
    "tongyi_shehui_xinyong_daima": "91110000123456789X",
    "chengli_riqi": "2020-01-01T00:00:00",
    "zhuce_dizhi": "北京市朝阳区测试路123号",
    "faren_xingming": "张三",
    "faren_shenfenzheng": "110101199001011234",
    "faren_lianxi": "13800138000",
    "lianxi_dianhua": "010-12345678",
    "lianxi_youxiang": "test@example.com",
    "lianxi_dizhi": "北京市朝阳区联系地址456号",
    "kehu_zhuangtai": "active",
    "fuwu_kaishi_riqi": "2024-01-01T00:00:00"
}

TEST_SERVICE_RECORD = {
    "goutong_fangshi": "phone",
    "goutong_neirong": "客户咨询税务申报相关问题",
    "goutong_shijian": "2024-01-15 10:30:00",
    "wenti_leixing": "shuiwu",
    "wenti_miaoshu": "询问增值税申报流程和注意事项",
    "chuli_zhuangtai": "pending"
}

class CustomerManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.customer_id = None
        self.service_record_id = None
        
    def login(self):
        """登录获取token"""
        print("🔐 正在登录...")
        login_data = {
            "yonghu_ming": "admin",
            "mima": "admin123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                # 修正token获取路径
                token_data = data.get("token", {})
                self.token = token_data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    print("✅ 登录成功")
                    return True
                else:
                    print(f"❌ 未获取到token: {data}")
                    return False
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_customer_crud(self):
        """测试客户CRUD操作"""
        print("\n📋 测试客户管理功能...")
        
        # 1. 创建客户
        print("1️⃣ 创建客户...")
        try:
            response = self.session.post(f"{API_BASE}/customers/", json=TEST_CUSTOMER)
            if response.status_code == 200:
                customer_data = response.json()
                self.customer_id = customer_data["id"]
                print(f"✅ 客户创建成功，ID: {self.customer_id}")
            else:
                print(f"❌ 客户创建失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 客户创建异常: {e}")
            return False
        
        # 2. 获取客户详情
        print("2️⃣ 获取客户详情...")
        try:
            response = self.session.get(f"{API_BASE}/customers/{self.customer_id}")
            if response.status_code == 200:
                customer_data = response.json()
                print(f"✅ 客户详情获取成功: {customer_data['gongsi_mingcheng']}")
            else:
                print(f"❌ 客户详情获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户详情获取异常: {e}")
            return False
        
        # 3. 更新客户信息
        print("3️⃣ 更新客户信息...")
        try:
            update_data = {"lianxi_dianhua": "010-87654321"}
            response = self.session.put(f"{API_BASE}/customers/{self.customer_id}", json=update_data)
            if response.status_code == 200:
                print("✅ 客户信息更新成功")
            else:
                print(f"❌ 客户信息更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户信息更新异常: {e}")
            return False
        
        # 4. 更新客户状态
        print("4️⃣ 更新客户状态...")
        try:
            response = self.session.patch(f"{API_BASE}/customers/{self.customer_id}/status", 
                                        params={"new_status": "renewing"})
            if response.status_code == 200:
                print("✅ 客户状态更新成功")
            else:
                print(f"❌ 客户状态更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户状态更新异常: {e}")
            return False
        
        # 5. 获取客户列表
        print("5️⃣ 获取客户列表...")
        try:
            response = self.session.get(f"{API_BASE}/customers/", params={"page": 1, "size": 10})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 客户列表获取成功，共 {data['total']} 个客户")
            else:
                print(f"❌ 客户列表获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户列表获取异常: {e}")
            return False
        
        return True
    
    def test_service_records(self):
        """测试服务记录管理"""
        print("\n📝 测试服务记录管理功能...")
        
        if not self.customer_id:
            print("❌ 需要先创建客户")
            return False
        
        # 1. 创建服务记录
        print("1️⃣ 创建服务记录...")
        try:
            record_data = {**TEST_SERVICE_RECORD, "kehu_id": self.customer_id}
            response = self.session.post(f"{API_BASE}/service-records/", json=record_data)
            if response.status_code == 200:
                service_data = response.json()
                self.service_record_id = service_data["id"]
                print(f"✅ 服务记录创建成功，ID: {self.service_record_id}")
            else:
                print(f"❌ 服务记录创建失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 服务记录创建异常: {e}")
            return False
        
        # 2. 获取服务记录详情
        print("2️⃣ 获取服务记录详情...")
        try:
            response = self.session.get(f"{API_BASE}/service-records/{self.service_record_id}")
            if response.status_code == 200:
                print("✅ 服务记录详情获取成功")
            else:
                print(f"❌ 服务记录详情获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务记录详情获取异常: {e}")
            return False
        
        # 3. 更新服务记录状态
        print("3️⃣ 更新服务记录状态...")
        try:
            response = self.session.patch(f"{API_BASE}/service-records/{self.service_record_id}/status",
                                        params={"new_status": "completed", "chuli_jieguo": "问题已解决"})
            if response.status_code == 200:
                print("✅ 服务记录状态更新成功")
            else:
                print(f"❌ 服务记录状态更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务记录状态更新异常: {e}")
            return False
        
        # 4. 获取客户服务记录
        print("4️⃣ 获取客户服务记录...")
        try:
            response = self.session.get(f"{API_BASE}/service-records/kehu/{self.customer_id}/records")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 客户服务记录获取成功，共 {data['total']} 条记录")
            else:
                print(f"❌ 客户服务记录获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户服务记录获取异常: {e}")
            return False
        
        return True
    
    def test_statistics(self):
        """测试统计功能"""
        print("\n📊 测试统计功能...")
        
        # 1. 客户统计
        print("1️⃣ 获取客户统计...")
        try:
            response = self.session.get(f"{API_BASE}/customers/statistics/overview")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 客户统计获取成功: 总客户数 {stats['total_customers']}")
            else:
                print(f"❌ 客户统计获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 客户统计获取异常: {e}")
            return False
        
        # 2. 服务记录统计
        print("2️⃣ 获取服务记录统计...")
        try:
            response = self.session.get(f"{API_BASE}/service-records/statistics/overview")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 服务记录统计获取成功: 总记录数 {stats['total_records']}")
            else:
                print(f"❌ 服务记录统计获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务记录统计获取异常: {e}")
            return False
        
        return True
    
    def cleanup(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        # 删除服务记录
        if self.service_record_id:
            try:
                response = self.session.delete(f"{API_BASE}/service-records/{self.service_record_id}")
                if response.status_code == 200:
                    print("✅ 服务记录删除成功")
                else:
                    print(f"⚠️ 服务记录删除失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 服务记录删除异常: {e}")
        
        # 删除客户
        if self.customer_id:
            try:
                response = self.session.delete(f"{API_BASE}/customers/{self.customer_id}")
                if response.status_code == 200:
                    print("✅ 客户删除成功")
                else:
                    print(f"⚠️ 客户删除失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 客户删除异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始客户管理模块完整功能测试")
        print("=" * 50)
        
        # 登录
        if not self.login():
            return False
        
        # 测试客户管理
        if not self.test_customer_crud():
            return False
        
        # 测试服务记录管理
        if not self.test_service_records():
            return False
        
        # 测试统计功能
        if not self.test_statistics():
            return False
        
        # 清理数据
        self.cleanup()
        
        print("\n" + "=" * 50)
        print("🎉 客户管理模块所有功能测试通过！")
        return True

def main():
    """主函数"""
    tester = CustomerManagementTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        tester.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        tester.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
