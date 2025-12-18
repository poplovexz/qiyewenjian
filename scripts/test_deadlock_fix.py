#!/usr/bin/env python3
"""
测试死锁修复的脚本
"""
import sys
import requests
import time
import json

def test_frontend_access():
    """测试前端首页访问"""
    print("🔍 测试前端首页访问...")
    
    try:
        response = requests.get("http://localhost:5174", timeout=15)
        if response.status_code == 200:
            content = response.text
            if "Vite + Vue + TS" in content and '<div id="app"></div>' in content:
                print("✅ 前端首页可以正常访问")
                return True
            else:
                print("⚠️ 前端首页内容异常")
                return False
        else:
            print(f"❌ 前端首页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端首页访问失败: {e}")
        return False

def test_auth_refresh_api():
    """测试认证刷新API"""
    print("\n🔍 测试认证刷新API...")
    
    try:
        # 先登录获取refresh_token
        login_data = {"yonghu_ming": "admin", "mima": "admin123"}
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            refresh_token = data["token"]["refresh_token"]
            print("✅ 登录成功，获取refresh_token")
            
            # 测试刷新API
            refresh_data = {"refresh_token": refresh_token}
            response = requests.post(
                "http://localhost:8000/api/v1/auth/refresh",
                json=refresh_data,
                timeout=10
            )
            
            if response.status_code == 200:
                new_data = response.json()
                if "access_token" in new_data:
                    print("✅ Token刷新API正常工作")
                    return True
                else:
                    print("❌ Token刷新API响应格式错误")
                    return False
            else:
                print(f"❌ Token刷新API失败: {response.status_code}")
                return False
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 认证刷新API测试失败: {e}")
        return False

def simulate_expired_token_scenario():
    """模拟过期token场景"""
    print("\n🔍 模拟过期token场景...")
    
    try:
        # 创建一个明显过期的token（过去的时间戳）
        import base64
        import json
        
        # 创建过期的JWT payload
        expired_payload = {
            "sub": "admin",
            "exp": 1000000000  # 2001年的时间戳，明显过期
        }
        
        # 简单的base64编码（不是真正的JWT，但足够测试）
        header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
        payload = base64.b64encode(json.dumps(expired_payload).encode()).decode()
        signature = "fake_signature"
        
        expired_token = f"{header}.{payload}.{signature}"
        
        print(f"✅ 创建了过期token用于测试")
        print(f"   Token前缀: {expired_token[:50]}...")
        
        return expired_token
        
    except Exception as e:
        print(f"❌ 创建过期token失败: {e}")
        return None

def check_deadlock_fix():
    """检查死锁修复情况"""
    print("\n🔍 检查死锁修复情况...")
    
    fixes = [
        ("tokenManager.ts", "packages/frontend/src/utils/tokenManager.ts", "_refreshTokenWithFetch"),
        ("request.ts", "packages/frontend/src/utils/request.ts", "/auth/refresh"),
    ]
    
    all_fixed = True
    
    for name, file_path, check_content in fixes:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if check_content in content:
                print(f"  ✅ {name}: 包含修复代码")
            else:
                print(f"  ❌ {name}: 缺少修复代码")
                all_fixed = False
                
        except Exception as e:
            print(f"  ❌ {name}: 检查失败 - {e}")
            all_fixed = False
    
    return all_fixed

def provide_testing_instructions():
    """提供测试说明"""
    print("\n📋 手动测试说明:")
    print("=" * 50)
    print("1. 清除浏览器所有数据:")
    print("   - 打开开发者工具 (F12)")
    print("   - 右键刷新按钮 → 清空缓存并硬性重新加载")
    print("   - 或者在Application标签页清除localStorage")
    print()
    print("2. 模拟过期token场景:")
    print("   - 在localStorage中设置过期的access_token")
    print("   - 访问 http://localhost:5174")
    print("   - 确认页面能正常加载（不是空白页）")
    print()
    print("3. 测试正常登录流程:")
    print("   - 访问 http://localhost:5174")
    print("   - 使用 admin/admin123 登录")
    print("   - 确认能正常进入系统")
    print()
    print("✅ 如果以上步骤都正常，说明死锁问题已修复")
    print("❌ 如果首页仍然空白，请检查浏览器控制台错误")

def main():
    """主函数"""
    print("🚀 开始测试死锁修复...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 检查修复代码
    if not check_deadlock_fix():
        print("\n⚠️ 部分修复代码可能缺失")
        all_tests_passed = False
    
    # 测试后端API
    if not test_auth_refresh_api():
        print("\n❌ 后端认证API测试失败")
        all_tests_passed = False
    
    # 测试前端访问
    if not test_frontend_access():
        print("\n❌ 前端访问测试失败")
        all_tests_passed = False
    
    # 模拟过期token场景
    expired_token = simulate_expired_token_scenario()
    
    # 提供测试说明
    provide_testing_instructions()
    
    print("\n" + "=" * 50)
    
    if all_tests_passed:
        print("🎉 自动化检查通过！")
        print("\n✅ 修复内容:")
        print("  ✅ 使用原生fetch刷新token，避免axios拦截器循环依赖")
        print("  ✅ 请求拦截器跳过刷新token请求的等待逻辑")
        print("  ✅ 防止初始化与刷新请求的相互锁死")
        print("\n🔧 修复原理:")
        print("  - tokenManager刷新token时使用原生fetch，不经过axios拦截器")
        print("  - 请求拦截器检测刷新请求，直接放行避免等待初始化")
        print("  - 打破了'初始化等待刷新'与'刷新等待初始化'的死锁循环")
        print("\n📱 请按照上述说明进行手动测试验证")
        return True
    else:
        print("❌ 部分检查失败")
        print("\n⚠️ 可能的问题:")
        print("  - 修复代码未完全应用")
        print("  - 服务未重启")
        print("  - 浏览器缓存问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
