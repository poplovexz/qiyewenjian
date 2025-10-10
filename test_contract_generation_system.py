#!/usr/bin/env python3
"""
合同生成系统测试脚本
测试新的合同生成、签署、支付功能
"""
import requests
import json
import sys
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

# 测试用户凭据
TEST_USER = {
    "yonghu_ming": "admin",
    "mima": "admin123"
}

def login():
    """登录获取token"""
    try:
        response = requests.post(LOGIN_URL, json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_contract_generation_api(token):
    """测试合同生成API"""
    print("\n🧪 测试合同生成API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试数据
    test_data = {
        "baojia_id": "test-quote-id",
        "contract_types": ["daili_jizhang", "zengzhi_fuwu"],
        "daili_jizhang_config": {
            "price": 2000.0,
            "count": 1,
            "party_id": "test-party-id",
            "price_change_reason": "优惠调整"
        },
        "zengzhi_fuwu_config": {
            "price": 1500.0,
            "count": 1,
            "party_id": "test-party-id",
            "price_change_reason": "促销活动"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/contract-generate/generate",
            json=test_data,
            headers=headers
        )
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 合同生成API响应正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"   ❌ 合同生成API失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 合同生成API异常: {e}")
        return False

def test_contract_preview_api(token):
    """测试合同预览API"""
    print("\n🧪 测试合同预览API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试数据
    test_data = {
        "contract_type": "daili_jizhang",
        "customer_name": "测试公司",
        "contract_amount": 2000.0,
        "template_id": "default-template"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/contract-generate/preview",
            json=test_data,
            headers=headers
        )
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 合同预览API响应正常")
            print(f"   预览内容长度: {len(data.get('content', ''))}")
            return True
        else:
            print(f"   ❌ 合同预览API失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 合同预览API异常: {e}")
        return False

def test_public_contract_signing_api():
    """测试公共合同签署API"""
    print("\n🧪 测试公共合同签署API...")
    
    # 测试获取合同信息（无需token）
    test_token = "test-signing-token"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/public/contract-signing/token/{test_token}"
        )
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            print(f"   ✅ 公共签署API响应正常（测试token不存在）")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ 公共签署API响应正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"   ❌ 公共签署API失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 公共签署API异常: {e}")
        return False

def test_public_contract_payment_api():
    """测试公共合同支付API"""
    print("\n🧪 测试公共合同支付API...")
    
    # 测试获取合同支付信息（无需token）
    test_contract_id = "test-contract-id"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/public/contract-payment/{test_contract_id}/info"
        )
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 404:
            print(f"   ✅ 公共支付API响应正常（测试合同不存在）")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ 公共支付API响应正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"   ❌ 公共支付API失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 公共支付API异常: {e}")
        return False

def test_backend_health():
    """测试后端健康状态"""
    print("\n🧪 测试后端健康状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 后端服务正常运行")
            return True
        else:
            print(f"   ❌ 后端服务异常: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 后端服务连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试合同生成系统...")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试后端健康状态
    test_results.append(("后端健康检查", test_backend_health()))
    
    # 2. 登录获取token
    print("\n🔐 用户登录...")
    token = login()
    if not token:
        print("❌ 无法获取认证token，跳过需要认证的测试")
        token = None
    else:
        print(f"✅ 登录成功，获取到token")
    
    # 3. 测试合同生成相关API
    if token:
        test_results.append(("合同生成API", test_contract_generation_api(token)))
        test_results.append(("合同预览API", test_contract_preview_api(token)))
    
    # 4. 测试公共API（无需认证）
    test_results.append(("公共合同签署API", test_public_contract_signing_api()))
    test_results.append(("公共合同支付API", test_public_contract_payment_api()))
    
    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！合同生成系统功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return 1

if __name__ == "__main__":
    sys.exit(main())
