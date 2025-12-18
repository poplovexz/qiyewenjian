#!/usr/bin/env python3
"""
创建示例客户数据
"""

import requests
import json
from datetime import datetime, timedelta
import random

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 示例客户数据
SAMPLE_CUSTOMERS = [
    {
        "gongsi_mingcheng": "北京科技创新有限公司",
        "tongyi_shehui_xinyong_daima": "91110000123456789A",
        "chengli_riqi": "2020-01-15T00:00:00",
        "zhuce_dizhi": "北京市海淀区中关村大街123号",
        "faren_xingming": "张伟",
        "faren_shenfenzheng": "110101198501011234",
        "faren_lianxi": "13800138001",
        "lianxi_dianhua": "010-12345678",
        "lianxi_youxiang": "zhangwei@bjkj.com",
        "lianxi_dizhi": "北京市海淀区中关村大街123号",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi_riqi": "2024-01-01T00:00:00"
    },
    {
        "gongsi_mingcheng": "上海智能制造股份有限公司",
        "tongyi_shehui_xinyong_daima": "91310000234567890B",
        "chengli_riqi": "2019-06-20T00:00:00",
        "zhuce_dizhi": "上海市浦东新区张江高科技园区456号",
        "faren_xingming": "李明",
        "faren_shenfenzheng": "310101198203151234",
        "faren_lianxi": "13900139002",
        "lianxi_dianhua": "021-87654321",
        "lianxi_youxiang": "liming@shzn.com",
        "lianxi_dizhi": "上海市浦东新区张江高科技园区456号",
        "kehu_zhuangtai": "renewing",
        "fuwu_kaishi_riqi": "2023-06-01T00:00:00"
    },
    {
        "gongsi_mingcheng": "深圳互联网科技有限公司",
        "tongyi_shehui_xinyong_daima": "91440300345678901C",
        "chengli_riqi": "2021-03-10T00:00:00",
        "zhuce_dizhi": "深圳市南山区科技园南区789号",
        "faren_xingming": "王芳",
        "faren_shenfenzheng": "440301199012251234",
        "faren_lianxi": "13700137003",
        "lianxi_dianhua": "0755-23456789",
        "lianxi_youxiang": "wangfang@szhly.com",
        "lianxi_dizhi": "深圳市南山区科技园南区789号",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi_riqi": "2024-03-01T00:00:00"
    },
    {
        "gongsi_mingcheng": "广州贸易发展有限公司",
        "tongyi_shehui_xinyong_daima": "91440100456789012D",
        "chengli_riqi": "2018-09-05T00:00:00",
        "zhuce_dizhi": "广州市天河区珠江新城101号",
        "faren_xingming": "陈强",
        "faren_shenfenzheng": "440101197808081234",
        "faren_lianxi": "13600136004",
        "lianxi_dianhua": "020-34567890",
        "lianxi_youxiang": "chenqiang@gzmy.com",
        "lianxi_dizhi": "广州市天河区珠江新城101号",
        "kehu_zhuangtai": "terminated",
        "fuwu_kaishi_riqi": "2023-01-01T00:00:00"
    },
    {
        "gongsi_mingcheng": "杭州电子商务有限公司",
        "tongyi_shehui_xinyong_daima": "91330100567890123E",
        "chengli_riqi": "2022-01-20T00:00:00",
        "zhuce_dizhi": "杭州市西湖区文三路202号",
        "faren_xingming": "刘洋",
        "faren_shenfenzheng": "330101198906061234",
        "faren_lianxi": "13500135005",
        "lianxi_dianhua": "0571-45678901",
        "lianxi_youxiang": "liuyang@hzds.com",
        "lianxi_dizhi": "杭州市西湖区文三路202号",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi_riqi": "2024-02-01T00:00:00"
    },
    {
        "gongsi_mingcheng": "成都软件开发有限公司",
        "tongyi_shehui_xinyong_daima": "91510100678901234F",
        "chengli_riqi": "2020-11-12T00:00:00",
        "zhuce_dizhi": "成都市高新区天府大道303号",
        "faren_xingming": "赵敏",
        "faren_shenfenzheng": "510101199204041234",
        "faren_lianxi": "13400134006",
        "lianxi_dianhua": "028-56789012",
        "lianxi_youxiang": "zhaomin@cdrj.com",
        "lianxi_dizhi": "成都市高新区天府大道303号",
        "kehu_zhuangtai": "renewing",
        "fuwu_kaishi_riqi": "2023-11-01T00:00:00"
    }
]

def create_sample_customers():
    """创建示例客户数据"""
    print("🚀 开始创建示例客户数据...")
    print("=" * 50)
    
    # 登录获取token
    print("🔐 正在登录...")
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", {}).get("access_token")
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ 登录成功")
            else:
                print("❌ 未获取到token")
                return False
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 创建客户
    print(f"\n📋 正在创建 {len(SAMPLE_CUSTOMERS)} 个示例客户...")
    success_count = 0
    
    for i, customer_data in enumerate(SAMPLE_CUSTOMERS, 1):
        try:
            print(f"{i}. 创建客户: {customer_data['gongsi_mingcheng']}")
            response = requests.post(f"{API_BASE}/customers/", json=customer_data, headers=headers)
            
            if response.status_code == 200:
                customer = response.json()
                print(f"   ✅ 创建成功 (ID: {customer['id'][:8]}...)")
                success_count += 1
                
                # 为每个客户创建一些服务记录
                create_service_records_for_customer(customer['id'], customer_data['gongsi_mingcheng'], headers)
                
            else:
                print(f"   ❌ 创建失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ 创建异常: {e}")
    
    print(f"\n📊 创建结果: {success_count}/{len(SAMPLE_CUSTOMERS)} 个客户创建成功")
    
    # 验证创建结果
    print("\n🔍 验证创建结果...")
    try:
        response = requests.get(f"{API_BASE}/customers/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 数据库中现有客户数量: {data['total']}")
            
            # 显示客户列表
            if data['items']:
                print("\n📋 客户列表:")
                for customer in data['items']:
                    status_text = {
                        'active': '活跃',
                        'renewing': '续约中', 
                        'terminated': '已终止'
                    }.get(customer['kehu_zhuangtai'], customer['kehu_zhuangtai'])
                    print(f"  • {customer['gongsi_mingcheng']} ({status_text})")
        else:
            print(f"❌ 验证失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 验证异常: {e}")
        return False
    
    return success_count > 0

def create_service_records_for_customer(customer_id, customer_name, headers):
    """为客户创建服务记录"""
    service_records = [
        {
            "kehu_id": customer_id,
            "goutong_fangshi": "phone",
            "goutong_neirong": f"与{customer_name}进行电话沟通，了解税务申报需求",
            "goutong_shijian": "2024-01-15 10:30:00",
            "wenti_leixing": "shuiwu",
            "wenti_miaoshu": "询问增值税申报流程和注意事项",
            "chuli_zhuangtai": "completed",
            "chuli_jieguo": "已详细解答客户疑问，提供相关资料"
        },
        {
            "kehu_id": customer_id,
            "goutong_fangshi": "wechat",
            "goutong_neirong": f"通过微信与{customer_name}沟通工商变更事宜",
            "goutong_shijian": "2024-02-20 14:15:00",
            "wenti_leixing": "gongshang",
            "wenti_miaoshu": "公司地址变更登记",
            "chuli_zhuangtai": "processing",
            "chuli_jieguo": "正在准备相关材料"
        }
    ]
    
    for record_data in service_records:
        try:
            response = requests.post(f"{API_BASE}/service-records/", json=record_data, headers=headers)
            if response.status_code == 200:
                print("     ✅ 创建服务记录成功")
            else:
                print(f"     ⚠️ 服务记录创建失败: {response.status_code}")
        except Exception as e:
            print(f"     ⚠️ 服务记录创建异常: {e}")

def main():
    """主函数"""
    print("🎯 客户管理模块示例数据创建工具")
    print("=" * 50)
    
    success = create_sample_customers()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 示例数据创建完成！")
        print("\n💡 现在你可以访问以下页面查看数据:")
        print("  • 客户列表: http://localhost:5174/customers")
        print("  • 服务记录: http://localhost:5174/customer-services")
        print("\n🔑 登录信息:")
        print("  • 用户名: admin")
        print("  • 密码: admin123")
    else:
        print("❌ 示例数据创建失败")
    
    return success

if __name__ == "__main__":
    main()
