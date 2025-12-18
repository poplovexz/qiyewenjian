#!/usr/bin/env python3
"""
快速修复验证脚本
"""
import sys
import requests

def test_frontend_access():
    """测试前端访问"""
    print("🔍 测试前端访问...")
    
    try:
        # 测试主页面
        response = requests.get("http://localhost:5174", timeout=10)
        if response.status_code == 200:
            print("✅ 主页面可以访问")
            return True
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端访问测试失败: {e}")
        return False

def test_backend_auth():
    """测试后端认证"""
    print("🔍 测试后端认证...")
    
    try:
        # 测试登录
        login_data = {"yonghu_ming": "admin", "mima": "admin123"}
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["token"]["access_token"]
            print("✅ 登录功能正常")
            
            # 测试用户信息获取
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                "http://localhost:8000/api/v1/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ 用户信息获取正常: {user_data['xingming']}")
                return True
            else:
                print(f"❌ 用户信息获取失败: {response.status_code}")
                return False
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 后端认证测试失败: {e}")
        return False

def test_test_page():
    """测试测试页面"""
    print("🔍 测试测试页面...")
    
    try:
        response = requests.get("http://localhost:5174/test-page.html", timeout=10)
        if response.status_code == 200:
            print("✅ 测试页面可以访问")
            return True
        else:
            print(f"❌ 测试页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试页面访问失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始快速修复验证...")
    print("=" * 40)
    
    all_tests_passed = True
    
    # 测试前端访问
    if not test_frontend_access():
        all_tests_passed = False
    
    # 测试后端认证
    if not test_backend_auth():
        all_tests_passed = False
    
    # 测试测试页面
    if not test_test_page():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    
    if all_tests_passed:
        print("🎉 快速验证通过！")
        print("\n✅ 验证结果:")
        print("  ✅ 前端可以正常访问")
        print("  ✅ 后端认证功能正常")
        print("  ✅ 测试页面可以访问")
        print("\n🔧 修复建议:")
        print("  1. 在浏览器中打开: http://localhost:5174/test-page.html")
        print("  2. 点击各个测试按钮验证功能")
        print("  3. 如果测试页面正常，再尝试访问主应用: http://localhost:5174")
        return True
    else:
        print("❌ 快速验证失败")
        print("\n⚠️ 需要进一步排查问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
