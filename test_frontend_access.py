#!/usr/bin/env python3
"""
测试前端页面访问
"""

import requests
import time

def test_frontend_access():
    """测试前端页面访问"""
    print("🌐 测试前端页面访问...")
    
    # 测试页面列表
    pages = [
        {
            'name': '登录页面',
            'url': 'http://localhost:5174/login',
            'should_work': True
        },
        {
            'name': '工作台',
            'url': 'http://localhost:5174/dashboard',
            'should_work': True
        },
        {
            'name': '合同列表',
            'url': 'http://localhost:5174/contracts',
            'should_work': True
        },
        {
            'name': '合同模板',
            'url': 'http://localhost:5174/contract-templates',
            'should_work': True
        },
        {
            'name': '客户管理',
            'url': 'http://localhost:5174/customers',
            'should_work': True
        }
    ]
    
    print(f"\n📋 测试 {len(pages)} 个页面...")
    
    for page in pages:
        try:
            response = requests.get(page['url'], timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {page['name']}: 正常访问")
                
                # 检查是否返回了HTML内容
                if 'html' in response.text.lower():
                    print(f"   📄 返回HTML内容")
                else:
                    print(f"   ⚠️  未返回HTML内容")
                    
            else:
                print(f"❌ {page['name']}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {page['name']}: 连接错误 - {e}")
        except Exception as e:
            print(f"❌ {page['name']}: 未知错误 - {e}")
    
    print("\n🔧 故障排除建议:")
    print("1. 确保前端服务正在运行: http://localhost:5174")
    print("2. 确保后端服务正在运行: http://localhost:8000")
    print("3. 清除浏览器缓存并重新登录")
    print("4. 检查浏览器控制台是否有JavaScript错误")
    print("5. 检查网络请求是否正常")


def test_api_endpoints():
    """测试API端点"""
    print("\n🔌 测试API端点...")
    
    # 先登录获取token
    login_data = {'yonghu_ming': 'admin', 'mima': 'admin123'}
    response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json()['token']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试API端点
    endpoints = [
        {
            'name': '合同模板列表',
            'url': 'http://localhost:8000/api/v1/contract-templates/',
            'method': 'GET'
        },
        {
            'name': '合同模板统计',
            'url': 'http://localhost:8000/api/v1/contract-templates/statistics/overview',
            'method': 'GET'
        },
        {
            'name': '客户列表',
            'url': 'http://localhost:8000/api/v1/customers/',
            'method': 'GET'
        }
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers, timeout=5)
            else:
                response = requests.post(endpoint['url'], headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']}: API正常")
            else:
                print(f"❌ {endpoint['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint['name']}: 错误 - {e}")


def check_services():
    """检查服务状态"""
    print("\n🔍 检查服务状态...")
    
    # 检查前端服务
    try:
        response = requests.get('http://localhost:5174', timeout=3)
        if response.status_code == 200:
            print("✅ 前端服务 (5174): 正常运行")
        else:
            print(f"⚠️  前端服务 (5174): HTTP {response.status_code}")
    except:
        print("❌ 前端服务 (5174): 无法连接")
    
    # 检查后端服务
    try:
        response = requests.get('http://localhost:8000/health', timeout=3)
        if response.status_code == 200:
            print("✅ 后端服务 (8000): 正常运行")
        else:
            print(f"⚠️  后端服务 (8000): HTTP {response.status_code}")
    except:
        print("❌ 后端服务 (8000): 无法连接")
    
    # 检查API文档
    try:
        response = requests.get('http://localhost:8000/docs', timeout=3)
        if response.status_code == 200:
            print("✅ API文档: 可访问")
        else:
            print(f"⚠️  API文档: HTTP {response.status_code}")
    except:
        print("❌ API文档: 无法访问")


if __name__ == "__main__":
    print("🚀 开始前端访问测试")
    print("=" * 50)
    
    # 检查服务状态
    check_services()
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试前端页面
    test_frontend_access()
    
    print("\n" + "=" * 50)
    print("📝 测试完成")
    print("\n💡 如果遇到权限问题:")
    print("1. 打开浏览器访问: http://localhost:5174/login")
    print("2. 使用 admin / admin123 登录")
    print("3. 登录后访问: http://localhost:5174/contract-templates")
    print("4. 如果仍有问题，请检查浏览器控制台错误信息")
