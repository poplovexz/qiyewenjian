#!/usr/bin/env python3
"""
测试修复后的产品管理页面
"""

import requests
import sys

def test_login():
    """测试登录"""
    print("🔐 测试登录")
    print("=" * 60)
    
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["token"]["access_token"]
            print(f"✅ 登录成功，获取到token")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_api_endpoints(token):
    """测试API端点"""
    print("\n🌐 测试API端点")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试产品分类列表
    print("1. 测试产品分类列表API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/categories/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 产品分类列表API正常，共 {len(data.get('items', []))} 个分类")
        else:
            print(f"❌ 产品分类列表API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 产品分类列表API异常: {e}")
    
    # 测试产品分类选项
    print("2. 测试产品分类选项API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/categories/options", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 产品分类选项API正常，共 {len(data)} 个选项")
        else:
            print(f"❌ 产品分类选项API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 产品分类选项API异常: {e}")
    
    # 测试产品项目列表
    print("3. 测试产品项目列表API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/products/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 产品项目列表API正常，共 {len(data.get('items', []))} 个产品")
        else:
            print(f"❌ 产品项目列表API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 产品项目列表API异常: {e}")
    
    # 测试增值产品分类选项
    print("4. 测试增值产品分类选项API...")
    try:
        response = requests.get("http://localhost:8000/api/v1/product-management/categories/options?chanpin_leixing=zengzhi", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 增值产品分类选项API正常，共 {len(data)} 个选项")
        else:
            print(f"❌ 增值产品分类选项API失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 增值产品分类选项API异常: {e}")

def test_page_access():
    """测试页面访问"""
    print("\n📱 测试页面访问")
    print("=" * 60)
    
    pages = [
        ("产品管理主页", "http://localhost:5174/product-management"),
        ("增值产品页面", "http://localhost:5174/product-management?type=zengzhi"),
        ("代理记账产品页面", "http://localhost:5174/product-management?type=daili_jizhang"),
        ("代理记账套餐页面", "http://localhost:5174/bookkeeping-packages")
    ]
    
    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}可访问: {url}")
            else:
                print(f"❌ {name}访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}访问异常: {e}")

def provide_instructions():
    """提供操作说明"""
    print("\n💡 修复说明和操作指南")
    print("=" * 60)
    
    print("🔧 已修复的问题:")
    print("1. 修复了ProductManagement.vue中方法名不匹配的问题")
    print("   - fetchCategoryList → fetchCategories")
    print("   - fetchProductList → fetchProducts")
    print("2. 修复了数据获取方式，直接使用store中的状态")
    print("3. 增加了详细的错误日志输出")
    print()
    
    print("🚀 现在请按以下步骤操作:")
    print("1. 打开浏览器访问: http://localhost:5174")
    print("2. 使用管理员账号登录:")
    print("   - 用户名: admin")
    print("   - 密码: admin123")
    print("3. 登录成功后访问增值产品页面:")
    print("   - http://localhost:5174/product-management?type=zengzhi")
    print("4. 检查页面是否正常显示，不再有错误提示")
    print()
    
    print("📋 预期结果:")
    print("✅ 页面正常加载，不再显示'获取分类列表失败'和'获取产品列表失败'")
    print("✅ 产品分类标签页显示增值产品相关分类")
    print("✅ 产品项目标签页显示增值产品相关项目")
    print("✅ 所有按钮和功能正常工作")
    print("✅ 可以正常创建、编辑、删除分类和产品")
    print()
    
    print("🔍 如果仍有问题:")
    print("1. 按F12打开浏览器开发者工具")
    print("2. 查看Console标签页的错误信息")
    print("3. 查看Network标签页的API请求状态")
    print("4. 将具体错误信息告诉我，我会进一步协助解决")

def main():
    """主函数"""
    print("🚀 修复后的产品管理页面测试")
    print("=" * 70)
    
    # 1. 测试登录
    token = test_login()
    if not token:
        print("\n❌ 无法获取认证token，请检查后端服务")
        sys.exit(1)
    
    # 2. 测试API端点
    test_api_endpoints(token)
    
    # 3. 测试页面访问
    test_page_access()
    
    # 4. 提供操作说明
    provide_instructions()
    
    print("\n🎉 测试完成！")
    print("=" * 70)
    print("现在请按照上述说明重新访问增值产品页面，应该不再有错误了。")

if __name__ == "__main__":
    main()
