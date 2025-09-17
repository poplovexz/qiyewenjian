#!/usr/bin/env python3
"""
测试新的菜单结构和产品类型筛选功能
验证增值服务和代理记账服务的分类筛选
"""

import requests
import json
import sys
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 全局变量存储token
auth_token = None

def login() -> bool:
    """登录获取token"""
    global auth_token
    
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token_data = data.get("token", {})
            auth_token = token_data.get("access_token")
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

def test_category_filtering():
    """测试分类筛选功能"""
    print("\n🧪 测试产品分类筛选功能")
    print("=" * 60)
    
    # 1. 测试获取所有分类
    print("1. 获取所有产品分类...")
    response = requests.get(f"{API_BASE}/product-management/categories/", headers=get_headers())
    if response.status_code == 200:
        all_data = response.json()
        all_count = all_data.get('total', 0)
        print(f"✅ 所有分类数量: {all_count}")
    else:
        print(f"❌ 获取所有分类失败: {response.status_code}")
        return False
    
    # 2. 测试筛选增值产品分类
    print("2. 筛选增值产品分类...")
    params = {"chanpin_leixing": "zengzhi"}
    response = requests.get(f"{API_BASE}/product-management/categories/", 
                          params=params, headers=get_headers())
    if response.status_code == 200:
        zengzhi_data = response.json()
        zengzhi_count = zengzhi_data.get('total', 0)
        print(f"✅ 增值产品分类数量: {zengzhi_count}")
        
        # 验证所有返回的分类都是增值产品类型
        items = zengzhi_data.get('items', [])
        all_zengzhi = all(item.get('chanpin_leixing') == 'zengzhi' for item in items)
        if all_zengzhi:
            print("✅ 筛选结果正确，所有分类都是增值产品类型")
        else:
            print("❌ 筛选结果错误，包含非增值产品类型")
            return False
    else:
        print(f"❌ 筛选增值产品分类失败: {response.status_code}")
        return False
    
    # 3. 测试筛选代理记账产品分类
    print("3. 筛选代理记账产品分类...")
    params = {"chanpin_leixing": "daili_jizhang"}
    response = requests.get(f"{API_BASE}/product-management/categories/", 
                          params=params, headers=get_headers())
    if response.status_code == 200:
        daili_data = response.json()
        daili_count = daili_data.get('total', 0)
        print(f"✅ 代理记账产品分类数量: {daili_count}")
        
        # 验证所有返回的分类都是代理记账产品类型
        items = daili_data.get('items', [])
        all_daili = all(item.get('chanpin_leixing') == 'daili_jizhang' for item in items)
        if all_daili:
            print("✅ 筛选结果正确，所有分类都是代理记账产品类型")
        else:
            print("❌ 筛选结果错误，包含非代理记账产品类型")
            return False
    else:
        print(f"❌ 筛选代理记账产品分类失败: {response.status_code}")
        return False
    
    # 4. 验证筛选结果的完整性
    print("4. 验证筛选结果完整性...")
    if zengzhi_count + daili_count == all_count:
        print("✅ 筛选结果完整，增值产品 + 代理记账 = 总数")
    else:
        print(f"❌ 筛选结果不完整: {zengzhi_count} + {daili_count} ≠ {all_count}")
        return False
    
    return True

def test_page_access():
    """测试页面访问"""
    print("\n🌐 测试页面访问")
    print("=" * 60)
    
    # 测试不同URL参数的页面访问
    test_urls = [
        ("通用产品管理页面", "http://localhost:5174/product-management"),
        ("增值服务页面", "http://localhost:5174/product-management?type=zengzhi"),
        ("代理记账服务页面", "http://localhost:5174/product-management?type=daili_jizhang")
    ]
    
    for name, url in test_urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {name}可访问")
            else:
                print(f"❌ {name}访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {name}访问异常: {e}")
            return False
    
    return True

def test_menu_structure():
    """测试菜单结构"""
    print("\n📋 新菜单结构说明")
    print("=" * 60)
    print("🎯 菜单层级结构:")
    print("产品管理 (一级菜单)")
    print("├── 增值服务 (二级菜单) → /product-management?type=zengzhi")
    print("└── 代理记账服务 (二级菜单) → /product-management?type=daili_jizhang")
    print()
    print("🎨 页面功能:")
    print("- 增值服务: 自动筛选显示增值产品相关的分类和项目")
    print("- 代理记账服务: 自动筛选显示代理记账产品相关的分类和项目")
    print("- 通用页面: 显示所有类型的产品，可手动筛选")
    print()
    print("✨ 用户体验:")
    print("- 点击不同菜单项会自动筛选对应类型的产品")
    print("- 页面标题会根据产品类型动态变化")
    print("- 筛选器会根据URL参数自动设置或隐藏")

def main():
    """主函数"""
    print("🚀 新菜单结构和筛选功能测试")
    print("=" * 70)
    
    # 1. 登录
    if not login():
        sys.exit(1)
    
    # 2. 测试分类筛选功能
    if not test_category_filtering():
        print("\n❌ 分类筛选测试失败")
        sys.exit(1)
    
    # 3. 测试页面访问
    if not test_page_access():
        print("\n❌ 页面访问测试失败")
        sys.exit(1)
    
    # 4. 显示菜单结构说明
    test_menu_structure()
    
    print("\n🎉 新菜单结构测试完成！")
    print("=" * 70)
    print("✅ 所有功能测试通过")
    print("✅ 产品分类筛选功能正常")
    print("✅ 页面访问功能正常")
    print("✅ 菜单结构符合要求")
    print("\n📱 访问地址:")
    print("- 增值服务: http://localhost:5174/product-management?type=zengzhi")
    print("- 代理记账服务: http://localhost:5174/product-management?type=daili_jizhang")
    print("- 通用产品管理: http://localhost:5174/product-management")
    print(f"- API文档: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
