#!/usr/bin/env python3
"""
通过API创建审核权限
"""
import requests

def login_admin():
    """登录获取token"""
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "yonghu_ming": "admin",
        "mima": "admin123"
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        result = response.json()
        return result.get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def create_permission(token, permission_data):
    """创建权限"""
    url = "http://localhost:8000/api/v1/user-management/permissions/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=permission_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建权限失败: {response.status_code} - {response.text}")
        return None

def get_permissions(token):
    """获取权限列表"""
    url = "http://localhost:8000/api/v1/user-management/permissions/tree"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取权限失败: {response.status_code} - {response.text}")
        return None

def main():
    print("🚀 开始通过API创建审核权限...")
    
    # 登录获取token
    token = login_admin()
    if not token:
        print("❌ 登录失败，无法继续")
        return False
    
    print("✅ 登录成功，获取到token")
    
    # 定义审核权限
    audit_permissions = [
        {
            "quanxian_ming": "审核管理菜单",
            "quanxian_bianma": "audit_menu",
            "miaoshu": "访问审核管理菜单的权限",
            "ziyuan_leixing": "menu",
            "ziyuan_lujing": "/audit",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "审核任务管理",
            "quanxian_bianma": "audit_manage",
            "miaoshu": "管理审核任务的权限",
            "ziyuan_leixing": "menu",
            "ziyuan_lujing": "/audit/tasks",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "审核流程配置",
            "quanxian_bianma": "audit_config",
            "miaoshu": "配置审核流程的权限",
            "ziyuan_leixing": "menu",
            "ziyuan_lujing": "/audit/workflow-config",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "审核规则配置",
            "quanxian_bianma": "audit_rule_config",
            "miaoshu": "配置审核规则的权限",
            "ziyuan_leixing": "menu",
            "ziyuan_lujing": "/audit/rule-config",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "查看审核任务",
            "quanxian_bianma": "audit:read",
            "miaoshu": "查看审核任务列表和详情的权限",
            "ziyuan_leixing": "api",
            "ziyuan_lujing": "/api/v1/audit/tasks",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "处理审核任务",
            "quanxian_bianma": "audit:process",
            "miaoshu": "处理审核任务的权限",
            "ziyuan_leixing": "api",
            "ziyuan_lujing": "/api/v1/audit/process",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "合同审核",
            "quanxian_bianma": "contract_audit",
            "miaoshu": "审核合同的权限",
            "ziyuan_leixing": "api",
            "ziyuan_lujing": "/api/v1/contracts/audit",
            "zhuangtai": "active"
        },
        {
            "quanxian_ming": "报价审核",
            "quanxian_bianma": "quote_audit",
            "miaoshu": "审核报价的权限",
            "ziyuan_leixing": "api",
            "ziyuan_lujing": "/api/v1/quotes/audit",
            "zhuangtai": "active"
        }
    ]
    
    # 创建权限
    created_count = 0
    for perm_data in audit_permissions:
        result = create_permission(token, perm_data)
        if result:
            print(f"✅ 创建权限: {perm_data['quanxian_ming']} ({perm_data['quanxian_bianma']})")
            created_count += 1
        else:
            print(f"⚠️ 权限可能已存在: {perm_data['quanxian_ming']}")
    
    print(f"\n📊 创建了 {created_count} 个新权限")
    
    # 获取并显示当前权限列表
    print("\n📋 获取当前权限列表...")
    permissions = get_permissions(token)
    if permissions:
        print("✅ 权限列表获取成功")
        
        # 查找审核相关权限
        audit_perms = []
        for perm in permissions:
            if 'audit' in perm.get('quanxian_bianma', '').lower():
                audit_perms.append(perm)
        
        if audit_perms:
            print(f"\n🔍 找到 {len(audit_perms)} 个审核相关权限:")
            for perm in audit_perms:
                print(f"  - {perm.get('quanxian_ming')} ({perm.get('quanxian_bianma')})")
        else:
            print("⚠️ 未找到审核相关权限")
    
    return True

if __name__ == "__main__":
    try:
        if main():
            print("\n🎉 审核权限创建完成！")
        else:
            print("\n❌ 审核权限创建失败！")
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
