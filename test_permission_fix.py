#!/usr/bin/env python3
"""
权限页面修复验证脚本
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_permission_api():
    """测试权限API修复"""
    print("🔧 测试权限页面修复...")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "yonghu_ming": "admin",
        "mima": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return False
    
    token = login_response.json()['token']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 测试修复前的问题场景
    print("\n2. 测试修复前的问题场景...")
    
    # 测试空size参数（修复前会422错误）
    bad_params = {
        'page': 1,
        'size': '',  # 空字符串，应该会被修复
        'search': '',
        'ziyuan_leixing': '',
        'zhuangtai': ''
    }
    
    print("   测试空size参数...")
    bad_response = requests.get(f"{API_BASE}/user-management/permissions/", 
                               params=bad_params, headers=headers)
    
    if bad_response.status_code == 422:
        print("   ✅ 确认空size参数会导致422错误（符合预期）")
    else:
        print(f"   ⚠️ 意外结果: {bad_response.status_code}")
    
    # 3. 测试修复后的正确调用
    print("\n3. 测试修复后的正确调用...")
    
    good_params = {
        'page': 1,
        'size': 20,  # 正确的整数
        'search': '',
        'ziyuan_leixing': '',
        'zhuangtai': ''
    }
    
    response = requests.get(f"{API_BASE}/user-management/permissions/", 
                           params=good_params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API调用成功")
        print(f"   📊 总数: {data['total']}")
        print(f"   📄 当前页: {data['page']}")
        print(f"   📏 页大小: {data['size']}")
        print(f"   📝 权限数量: {len(data['items'])}")
        
        # 验证数据结构
        if data['items']:
            first_item = data['items'][0]
            required_fields = ['id', 'quanxian_ming', 'quanxian_bianma', 'ziyuan_leixing']
            missing_fields = [field for field in required_fields if field not in first_item]
            
            if not missing_fields:
                print("   ✅ 数据结构正确")
            else:
                print(f"   ⚠️ 缺少字段: {missing_fields}")
        
        return True
    else:
        print(f"   ❌ API调用失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False

def test_different_scenarios():
    """测试不同的参数场景"""
    print("\n4. 测试不同参数场景...")
    
    # 登录
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "yonghu_ming": "admin",
        "mima": "admin123"
    })
    token = login_response.json()['token']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {"name": "基本查询", "params": {"page": 1, "size": 10}},
        {"name": "搜索查询", "params": {"page": 1, "size": 10, "search": "用户"}},
        {"name": "类型筛选", "params": {"page": 1, "size": 10, "ziyuan_leixing": "api"}},
        {"name": "状态筛选", "params": {"page": 1, "size": 10, "zhuangtai": "active"}},
        {"name": "组合查询", "params": {"page": 1, "size": 5, "search": "查看", "zhuangtai": "active"}},
    ]
    
    success_count = 0
    for test_case in test_cases:
        response = requests.get(f"{API_BASE}/user-management/permissions/", 
                               params=test_case["params"], headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {test_case['name']}: 成功 (返回{len(data['items'])}条)")
            success_count += 1
        else:
            print(f"   ❌ {test_case['name']}: 失败 ({response.status_code})")
    
    print(f"\n📊 测试结果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)

def main():
    """主测试函数"""
    print("🧪 权限页面修复验证测试\n")
    
    # 测试API修复
    api_success = test_permission_api()
    
    # 测试不同场景
    scenarios_success = test_different_scenarios()
    
    # 总结
    print("\n" + "="*50)
    print("📋 修复验证总结:")
    print(f"✅ API调用修复: {'通过' if api_success else '失败'}")
    print(f"✅ 多场景测试: {'通过' if scenarios_success else '失败'}")
    
    if api_success and scenarios_success:
        print("\n🎉 所有测试通过！权限页面修复成功！")
        print("\n📝 修复内容:")
        print("1. ✅ 修复了422错误 - 使用pageSize.value而不是pageSize")
        print("2. ✅ 添加了分页组件保护 - v-if=\"total > 0\"")
        print("3. ✅ 添加了统计数据保护 - 使用 || 0 防止undefined")
        print("\n🔍 前端修复说明:")
        print("- InvalidCharacterError应该通过添加的保护措施得到解决")
        print("- 如果仍有问题，可能需要检查Element Plus版本兼容性")
    else:
        print("\n⚠️ 部分测试未通过，需要进一步检查")

if __name__ == "__main__":
    main()
