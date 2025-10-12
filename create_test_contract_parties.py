#!/usr/bin/env python3
"""
创建测试的乙方主体数据
"""

import requests
import json

# API配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
PARTY_URL = f"{BASE_URL}/api/v1/contract-parties"

def login():
    """登录获取token"""
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        result = response.json()
        token_data = result.get("token", {})
        return token_data.get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def create_contract_party(token, party_data):
    """创建乙方主体"""
    headers = get_headers(token)
    response = requests.post(PARTY_URL, json=party_data, headers=headers)
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"创建乙方主体失败: {response.status_code} - {response.text}")
        return None

def main():
    print("=== 创建测试的乙方主体数据 ===")
    
    # 1. 登录
    print("\n1. 登录系统...")
    token = login()
    if not token:
        print("登录失败，退出")
        return
    print("✅ 登录成功")
    
    # 2. 创建测试乙方主体
    test_parties = [
        {
            "zhuti_mingcheng": "北京智慧财税服务有限公司",
            "zhuti_leixing": "gongsi",
            "tongyi_shehui_xinyong_daima": "91110000MA01234567",
            "faren_daibiao": "张三",
            "lianxi_ren": "张三",
            "zhuce_dizhi": "北京市朝阳区建国路88号",
            "lianxi_dianhua": "010-12345678",
            "youxiang": "contact@bjzh.com",
            "yinhang_mingcheng": "中国工商银行北京分行",
            "yinhang_zhanghu": "6222021234567890123",
            "zhanghu_mingcheng": "北京智慧财税服务有限公司",
            "kaihuhang": "工商银行北京朝阳支行",
            "beizhu": "专业代理记账服务公司"
        },
        {
            "zhuti_mingcheng": "上海创新企业管理咨询有限公司",
            "zhuti_leixing": "gongsi",
            "tongyi_shehui_xinyong_daima": "91310000MA02345678",
            "faren_daibiao": "李四",
            "lianxi_ren": "李四",
            "zhuce_dizhi": "上海市浦东新区陆家嘴环路1000号",
            "lianxi_dianhua": "021-87654321",
            "youxiang": "info@shcx.com",
            "yinhang_mingcheng": "中国建设银行上海分行",
            "yinhang_zhanghu": "6227001234567890123",
            "zhanghu_mingcheng": "上海创新企业管理咨询有限公司",
            "kaihuhang": "建设银行上海浦东支行",
            "beizhu": "企业管理咨询和增值服务"
        },
        {
            "zhuti_mingcheng": "深圳前海财务顾问有限公司",
            "zhuti_leixing": "gongsi",
            "tongyi_shehui_xinyong_daima": "91440300MA03456789",
            "faren_daibiao": "王五",
            "lianxi_ren": "王五",
            "zhuce_dizhi": "深圳市前海深港合作区前湾一路1号",
            "lianxi_dianhua": "0755-23456789",
            "youxiang": "service@szqh.com",
            "yinhang_mingcheng": "招商银行深圳分行",
            "yinhang_zhanghu": "6225881234567890123",
            "zhanghu_mingcheng": "深圳前海财务顾问有限公司",
            "kaihuhang": "招商银行深圳前海支行",
            "beizhu": "财务顾问和税务筹划服务"
        },
        {
            "zhuti_mingcheng": "广州天河商务服务中心",
            "zhuti_leixing": "gongsi",
            "tongyi_shehui_xinyong_daima": "91440100MA04567890",
            "faren_daibiao": "赵六",
            "lianxi_ren": "赵六",
            "zhuce_dizhi": "广州市天河区珠江新城花城大道85号",
            "lianxi_dianhua": "020-34567890",
            "youxiang": "admin@gzth.com",
            "yinhang_mingcheng": "中国银行广州分行",
            "yinhang_zhanghu": "6216601234567890123",
            "zhanghu_mingcheng": "广州天河商务服务中心",
            "kaihuhang": "中国银行广州天河支行",
            "beizhu": "综合商务服务和代理记账"
        }
    ]
    
    print(f"\n2. 创建 {len(test_parties)} 个测试乙方主体...")
    
    created_count = 0
    for i, party_data in enumerate(test_parties, 1):
        print(f"\n创建第 {i} 个乙方主体: {party_data['zhuti_mingcheng']}")
        
        result = create_contract_party(token, party_data)
        if result:
            print(f"✅ 创建成功，ID: {result.get('id', 'N/A')}")
            created_count += 1
        else:
            print(f"❌ 创建失败")
    
    print(f"\n=== 创建完成 ===")
    print(f"成功创建 {created_count}/{len(test_parties)} 个乙方主体")
    
    if created_count > 0:
        print("\n现在可以在合同生成页面中选择这些乙方主体了！")

if __name__ == "__main__":
    main()