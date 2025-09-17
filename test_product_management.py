#!/usr/bin/env python3
"""
产品管理模块功能测试脚本
测试产品分类、产品项目和产品步骤的完整功能
"""

import requests
import json
import sys
import random
import string
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 全局变量存储token和测试数据
auth_token = None
test_category_id = None
test_product_id = None

def login() -> bool:
    """登录获取token"""
    global auth_token
    
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        print(f"登录响应状态: {response.status_code}")
        print(f"登录响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            token_data = data.get("token", {})
            auth_token = token_data.get("access_token")
            print(f"获取到token: {auth_token[:20]}..." if auth_token else "未获取到token")
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def get_headers() -> Dict[str, str]:
    """获取请求头"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

def test_product_categories():
    """测试产品分类功能"""
    global test_category_id
    
    print("\n🧪 测试产品分类功能")
    print("=" * 50)
    
    # 1. 获取分类列表
    print("1. 获取产品分类列表...")
    response = requests.get(f"{API_BASE}/product-management/categories/", headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取分类列表成功，共 {data.get('total', 0)} 个分类")
    else:
        print(f"❌ 获取分类列表失败: {response.status_code}")
    
    # 2. 创建新分类
    print("2. 创建新产品分类...")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    category_data = {
        "fenlei_mingcheng": f"测试增值产品分类_{random_suffix}",
        "fenlei_bianma": f"TEST_ZENGZHI_{random_suffix}",
        "chanpin_leixing": "zengzhi",
        "miaoshu": "这是一个测试用的增值产品分类",
        "paixu": 100,
        "zhuangtai": "active"
    }
    
    response = requests.post(f"{API_BASE}/product-management/categories/", 
                           json=category_data, headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        test_category_id = data.get("id")
        print(f"✅ 创建分类成功，ID: {test_category_id}")
    else:
        print(f"❌ 创建分类失败: {response.status_code} - {response.text}")
    
    # 3. 获取分类选项
    print("3. 获取分类选项...")
    response = requests.get(f"{API_BASE}/product-management/categories/options", headers=get_headers())
    if response.status_code == 200:
        options = response.json()
        print(f"✅ 获取分类选项成功，共 {len(options)} 个选项")
    else:
        print(f"❌ 获取分类选项失败: {response.status_code}")

def test_products():
    """测试产品项目功能"""
    global test_product_id
    
    print("\n🧪 测试产品项目功能")
    print("=" * 50)
    
    if not test_category_id:
        print("❌ 需要先创建产品分类")
        return
    
    # 1. 获取产品列表
    print("1. 获取产品项目列表...")
    response = requests.get(f"{API_BASE}/product-management/products/", headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取产品列表成功，共 {data.get('total', 0)} 个产品")
    else:
        print(f"❌ 获取产品列表失败: {response.status_code}")
    
    # 2. 创建新产品
    print("2. 创建新产品项目...")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    product_data = {
        "xiangmu_mingcheng": f"测试产品项目_{random_suffix}",
        "xiangmu_bianma": f"TEST_PRODUCT_{random_suffix}",
        "fenlei_id": test_category_id,
        "yewu_baojia": 1500.00,
        "baojia_danwei": "元",
        "banshi_tianshu": 7,
        "xiangmu_beizhu": "这是一个测试用的产品项目",
        "zhuangtai": "active"
    }
    
    response = requests.post(f"{API_BASE}/product-management/products/", 
                           json=product_data, headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        test_product_id = data.get("id")
        print(f"✅ 创建产品成功，ID: {test_product_id}")
    else:
        print(f"❌ 创建产品失败: {response.status_code} - {response.text}")
    
    # 3. 获取产品详情
    if test_product_id:
        print("3. 获取产品详情...")
        response = requests.get(f"{API_BASE}/product-management/products/{test_product_id}", 
                              headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取产品详情成功: {data.get('xiangmu_mingcheng')}")
        else:
            print(f"❌ 获取产品详情失败: {response.status_code}")

def test_product_steps():
    """测试产品步骤功能"""
    print("\n🧪 测试产品步骤功能")
    print("=" * 50)
    
    if not test_product_id:
        print("❌ 需要先创建产品项目")
        return
    
    # 1. 创建产品步骤
    print("1. 创建产品步骤...")
    steps_data = [
        {
            "buzou_mingcheng": "资料收集",
            "yugu_shichang": 2,
            "shichang_danwei": "小时",
            "buzou_feiyong": 200.00,
            "paixu": 1,
            "shi_bixu": "Y"
        },
        {
            "buzou_mingcheng": "方案设计",
            "yugu_shichang": 4,
            "shichang_danwei": "小时", 
            "buzou_feiyong": 500.00,
            "paixu": 2,
            "shi_bixu": "Y"
        },
        {
            "buzou_mingcheng": "实施执行",
            "yugu_shichang": 8,
            "shichang_danwei": "小时",
            "buzou_feiyong": 800.00,
            "paixu": 3,
            "shi_bixu": "Y"
        }
    ]
    
    created_steps = []
    for step_data in steps_data:
        step_data["xiangmu_id"] = test_product_id
        response = requests.post(f"{API_BASE}/product-management/steps", 
                               json=step_data, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            created_steps.append(data.get("id"))
            print(f"✅ 创建步骤成功: {step_data['buzou_mingcheng']}")
        else:
            print(f"❌ 创建步骤失败: {response.status_code} - {response.text}")
    
    # 2. 获取产品步骤列表
    print("2. 获取产品步骤列表...")
    response = requests.get(f"{API_BASE}/product-management/products/{test_product_id}/steps", 
                          headers=get_headers())
    if response.status_code == 200:
        steps = response.json()
        print(f"✅ 获取步骤列表成功，共 {len(steps)} 个步骤")
    else:
        print(f"❌ 获取步骤列表失败: {response.status_code}")
    
    # 3. 获取产品完整详情（包含步骤）
    print("3. 获取产品完整详情...")
    response = requests.get(f"{API_BASE}/product-management/products/{test_product_id}/detail", 
                          headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        steps_count = len(data.get("buzou_list", []))
        print(f"✅ 获取完整详情成功，包含 {steps_count} 个步骤")
    else:
        print(f"❌ 获取完整详情失败: {response.status_code}")

def main():
    """主函数"""
    print("🚀 产品管理模块功能测试")
    print("=" * 60)
    
    # 1. 登录
    if not login():
        sys.exit(1)
    
    # 2. 测试产品分类
    test_product_categories()
    
    # 3. 测试产品项目
    test_products()
    
    # 4. 测试产品步骤
    test_product_steps()
    
    print("\n🎉 测试完成！")
    print("=" * 60)
    print("请检查以上测试结果，确保所有功能正常工作。")
    print("您可以访问以下地址查看详细信息：")
    print(f"- API文档: {BASE_URL}/docs")
    print(f"- 前端应用: http://localhost:5174")

if __name__ == "__main__":
    main()
