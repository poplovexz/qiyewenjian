#!/usr/bin/env python3
"""
调试前端客户管理问题
"""

import requests
import json
import time

def debug_customer_frontend():
    """调试前端客户管理问题"""
    print("🔍 调试前端客户管理问题")
    print("=" * 50)
    
    # 1. 检查后端API
    print("1️⃣ 检查后端客户API...")
    try:
        # 登录获取token
        login_data = {"yonghu_ming": "admin", "mima": "admin123"}
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["token"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ 登录成功")
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            return False
        
        # 测试客户列表API
        response = requests.get("http://localhost:8000/api/v1/customers/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 后端API正常，返回 {data['total']} 个客户")
            print(f"   📋 数据结构: {list(data.keys())}")
            if data['items']:
                print(f"   📝 第一个客户: {data['items'][0]['gongsi_mingcheng']}")
        else:
            print(f"   ❌ 后端API失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 后端API异常: {e}")
        return False
    
    # 2. 检查前端服务
    print("\n2️⃣ 检查前端服务...")
    try:
        response = requests.get("http://localhost:5174/customers", timeout=10)
        if response.status_code == 200:
            print("   ✅ 前端页面可访问")
            
            # 检查页面内容
            html = response.text
            if "客户管理" in html or "customer" in html.lower():
                print("   ✅ 页面包含客户相关内容")
            else:
                print("   ⚠️ 页面可能不包含客户内容")
                
            # 检查是否有JavaScript错误标识
            if "error" in html.lower() or "exception" in html.lower():
                print("   ⚠️ 页面可能包含错误信息")
            
            print(f"   📊 页面大小: {len(html)} 字符")
        else:
            print(f"   ❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 前端页面访问异常: {e}")
        return False
    
    # 3. 检查前端API调用
    print("\n3️⃣ 模拟前端API调用...")
    try:
        # 模拟前端的API调用
        headers_frontend = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 测试客户列表API（带分页参数）
        params = {"page": 1, "size": 10}
        response = requests.get("http://localhost:8000/api/v1/customers/", 
                              headers=headers_frontend, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 前端API调用成功")
            print(f"   📊 返回数据: total={data['total']}, items={len(data['items'])}")
            print(f"   📄 分页信息: page={data['page']}, size={data['size']}")
            
            # 检查数据格式
            if data['items']:
                customer = data['items'][0]
                required_fields = ['id', 'gongsi_mingcheng', 'kehu_zhuangtai']
                missing_fields = [field for field in required_fields if field not in customer]
                if missing_fields:
                    print(f"   ⚠️ 客户数据缺少字段: {missing_fields}")
                else:
                    print("   ✅ 客户数据格式正确")
        else:
            print(f"   ❌ 前端API调用失败: {response.status_code}")
            print(f"   📝 错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 前端API调用异常: {e}")
        return False
    
    # 4. 检查CORS和网络问题
    print("\n4️⃣ 检查CORS和网络问题...")
    try:
        # 检查OPTIONS请求
        response = requests.options("http://localhost:8000/api/v1/customers/")
        if response.status_code == 200:
            print("   ✅ CORS预检请求正常")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            print(f"   📋 CORS头信息: {cors_headers}")
        else:
            print(f"   ⚠️ CORS预检请求异常: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ CORS检查异常: {e}")
    
    # 5. 生成调试建议
    print("\n5️⃣ 调试建议...")
    print("   💡 请在浏览器中执行以下步骤:")
    print("   1. 打开 http://localhost:5174/customers")
    print("   2. 按F12打开开发者工具")
    print("   3. 查看Console标签页的错误信息")
    print("   4. 查看Network标签页的网络请求")
    print("   5. 检查是否有失败的API请求")
    
    print("\n   🔧 常见问题排查:")
    print("   • 如果Console有JavaScript错误，说明前端代码有问题")
    print("   • 如果Network中API请求失败，检查认证token")
    print("   • 如果API请求成功但页面无数据，检查前端数据绑定")
    print("   • 如果页面完全空白，可能是路由或组件加载问题")
    
    return True

def check_frontend_console_errors():
    """检查可能的前端控制台错误"""
    print("\n🔍 检查前端可能的问题...")
    
    # 检查前端编译状态
    try:
        import subprocess
        result = subprocess.run(
            ["pnpm", "run", "type-check"], 
            cwd="/var/www/packages/frontend",
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ TypeScript编译检查通过")
        else:
            print("   ❌ TypeScript编译有错误:")
            print(f"   {result.stderr}")
            return False
    except Exception as e:
        print(f"   ⚠️ 无法检查TypeScript编译: {e}")
    
    return True

def main():
    """主函数"""
    print("🎯 前端客户管理调试工具")
    print("=" * 50)
    
    success = debug_customer_frontend()
    check_frontend_console_errors()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 基础检查完成！")
        print("\n💡 下一步:")
        print("1. 在浏览器中打开开发者工具查看具体错误")
        print("2. 检查Network标签页的API请求状态")
        print("3. 查看Console标签页的JavaScript错误")
        print("4. 如果需要，清除浏览器缓存后重试")
    else:
        print("❌ 发现问题，请根据上述信息进行修复")
    
    return success

if __name__ == "__main__":
    main()
