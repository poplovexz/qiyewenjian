#!/usr/bin/env python3
"""
认证修复验证脚本
测试所有修复的认证问题是否正常工作
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE = "http://localhost:8000/api/v1"

def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    
    response = requests.post(f"{API_BASE}/auth/login", json={
        "yonghu_ming": "admin",
        "mima": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功: {data['user']['xingming']}")
        return data['token']['access_token'], data['token']['refresh_token']
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None, None

def test_api_with_token(token, endpoint, description):
    """使用token测试API端点"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('items', [])) if 'items' in data else data.get('total', 'N/A')
            print(f"✅ {description}: 成功 (数据量: {count})")
            return True
        elif response.status_code == 401:
            print(f"❌ {description}: 401未授权")
            return False
        elif response.status_code == 403:
            print(f"⚠️ {description}: 403权限不足")
            return False
        else:
            print(f"❌ {description}: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {description}: 异常 - {str(e)}")
        return False

def test_token_refresh(refresh_token):
    """测试token刷新功能"""
    print("🔄 测试Token刷新功能...")
    
    response = requests.post(f"{API_BASE}/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Token刷新成功")
        return data['access_token'], data['refresh_token']
    else:
        print(f"❌ Token刷新失败: {response.status_code} - {response.text}")
        return None, None

def test_concurrent_requests(token):
    """测试并发请求"""
    print("🚀 测试并发请求...")
    
    endpoints = [
        ("/user-management/roles/?page=1&size=5", "角色API"),
        ("/users/?page=1&size=5", "用户API"),
        ("/user-management/permissions/?page=1&size=5", "权限API"),
        ("/user-management/roles/?page=2&size=5", "角色API-2"),
        ("/users/?page=2&size=5", "用户API-2"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(test_api_with_token, token, endpoint, desc): desc 
            for endpoint, desc in endpoints
        }
        
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    
    print(f"📊 并发请求结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_invalid_token():
    """测试无效token的处理"""
    print("🔒 测试无效Token处理...")
    
    invalid_token = "invalid.token.here"
    result = test_api_with_token(invalid_token, "/user-management/roles/?page=1&size=5", "无效Token测试")
    
    if not result:
        print("✅ 无效Token正确被拒绝")
        return True
    else:
        print("❌ 无效Token未被正确拒绝")
        return False

def test_expired_token():
    """测试过期token的处理"""
    print("⏰ 测试过期Token处理...")
    
    # 这是一个已过期的token示例
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwMDAwMDAwMH0.invalid"
    result = test_api_with_token(expired_token, "/user-management/roles/?page=1&size=5", "过期Token测试")
    
    if not result:
        print("✅ 过期Token正确被拒绝")
        return True
    else:
        print("❌ 过期Token未被正确拒绝")
        return False

def main():
    """主测试函数"""
    print("🧪 开始认证修复验证测试\n")
    
    # 1. 测试登录
    access_token, refresh_token = test_login()
    if not access_token:
        print("❌ 登录失败，无法继续测试")
        return
    
    print()
    
    # 2. 测试各个API端点
    print("📡 测试API端点...")
    api_tests = [
        ("/user-management/roles/?page=1&size=5", "角色管理API"),
        ("/users/?page=1&size=5", "用户管理API"),
        ("/user-management/permissions/?page=1&size=5", "权限管理API"),
        ("/leads/?page=1&size=5", "线索管理API"),
        ("/lead-sources/?page=1&size=5", "线索来源API"),
    ]
    
    api_success_count = 0
    for endpoint, description in api_tests:
        if test_api_with_token(access_token, endpoint, description):
            api_success_count += 1
    
    print(f"📊 API测试结果: {api_success_count}/{len(api_tests)} 成功\n")
    
    # 3. 测试Token刷新
    new_access_token, new_refresh_token = test_token_refresh(refresh_token)
    if new_access_token:
        # 用新token测试一个API
        test_api_with_token(new_access_token, "/user-management/roles/?page=1&size=5", "新Token测试")
    
    print()
    
    # 4. 测试并发请求
    concurrent_success = test_concurrent_requests(access_token)
    
    print()
    
    # 5. 测试无效和过期token
    invalid_success = test_invalid_token()
    expired_success = test_expired_token()
    
    print()
    
    # 总结
    print("📋 测试总结:")
    print(f"✅ 登录功能: {'正常' if access_token else '异常'}")
    print(f"✅ API权限验证: {api_success_count}/{len(api_tests)} 正常")
    print(f"✅ Token刷新: {'正常' if new_access_token else '异常'}")
    print(f"✅ 并发请求: {'正常' if concurrent_success else '异常'}")
    print(f"✅ 无效Token处理: {'正常' if invalid_success else '异常'}")
    print(f"✅ 过期Token处理: {'正常' if expired_success else '异常'}")
    
    total_tests = 6
    passed_tests = sum([
        bool(access_token),
        api_success_count == len(api_tests),
        bool(new_access_token),
        concurrent_success,
        invalid_success,
        expired_success
    ])
    
    print(f"\n🎯 总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有认证修复验证通过！")
    else:
        print("⚠️ 部分测试未通过，需要进一步检查")

if __name__ == "__main__":
    main()
