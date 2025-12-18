#!/usr/bin/env python3
"""
数据修复脚本：为现有的没有客户ID的线索创建客户记录
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "yonghu_ming": "admin",
            "mima": "admin123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token", {}).get("access_token")
    return None

def get_all_leads(token):
    """获取所有线索"""
    headers = {"Authorization": f"Bearer {token}"}
    all_leads = []
    page = 1
    
    while True:
        response = requests.get(
            f"{BASE_URL}/leads",
            headers=headers,
            params={"page": page, "size": 100}
        )
        
        if response.status_code != 200:
            break
            
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            break
            
        all_leads.extend(items)
        
        if len(items) < 100:
            break
            
        page += 1
    
    return all_leads

def create_customer_for_lead(token, lead):
    """为线索创建客户"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 生成临时信用代码
    import uuid
    temp_credit_code = f"TEMP{uuid.uuid4().hex[:14].upper()}"
    
    customer_data = {
        "gongsi_mingcheng": lead.get("gongsi_mingcheng"),
        "tongyi_shehui_xinyong_daima": temp_credit_code,
        "faren_xingming": lead.get("lianxi_ren", "待补充"),
        "lianxi_dianhua": lead.get("lianxi_dianhua"),
        "lianxi_youxiang": lead.get("lianxi_youxiang"),
        "lianxi_dizhi": lead.get("zhuce_dizhi"),
        "zhuce_dizhi": lead.get("zhuce_dizhi"),
        "kehu_zhuangtai": "active"
    }
    
    response = requests.post(
        f"{BASE_URL}/customers",
        headers=headers,
        json=customer_data
    )
    
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"   ❌ 创建客户失败: {response.status_code} - {response.text}")
        return None

def update_lead_customer(token, lead_id, customer_id):
    """更新线索的客户ID"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.put(
        f"{BASE_URL}/leads/{lead_id}",
        headers=headers,
        json={"kehu_id": customer_id}
    )
    
    return response.status_code == 200

def check_customer_exists(token, company_name):
    """检查客户是否已存在"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/customers",
        headers=headers,
        params={"search": company_name, "page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        
        # 查找完全匹配的客户
        for item in items:
            if item.get("gongsi_mingcheng") == company_name:
                return item.get("id")
    
    return None

def main():
    print("=" * 70)
    print("数据修复：为现有线索创建客户记录")
    print("=" * 70)
    
    # 1. 登录
    print("\n1. 登录系统...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✅ 登录成功")
    
    # 2. 获取所有线索
    print("\n2. 获取所有线索...")
    leads = get_all_leads(token)
    print(f"✅ 找到 {len(leads)} 个线索")
    
    # 3. 筛选没有客户ID的线索
    leads_without_customer = [lead for lead in leads if not lead.get("kehu_id")]
    print(f"\n3. 筛选结果：")
    print(f"   - 总线索数: {len(leads)}")
    print(f"   - 已有客户: {len(leads) - len(leads_without_customer)}")
    print(f"   - 需要修复: {len(leads_without_customer)}")
    
    if not leads_without_customer:
        print("\n✅ 所有线索都已关联客户，无需修复！")
        return
    
    # 4. 确认是否继续
    print(f"\n⚠️  将为 {len(leads_without_customer)} 个线索创建客户记录")
    print("   这些客户将使用临时信用代码（TEMP前缀），需要后续补充真实信息")
    
    confirm = input("\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 操作已取消")
        return
    
    # 5. 处理每个线索
    print(f"\n4. 开始处理线索...")
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, lead in enumerate(leads_without_customer, 1):
        lead_id = lead.get("id")
        company_name = lead.get("gongsi_mingcheng")
        lead_code = lead.get("xiansuo_bianma")
        
        print(f"\n[{i}/{len(leads_without_customer)}] 处理线索: {lead_code} - {company_name}")
        
        # 检查是否已存在同名客户
        existing_customer_id = check_customer_exists(token, company_name)
        
        if existing_customer_id:
            print(f"   ℹ️  找到已存在的客户: {existing_customer_id}")
            customer_id = existing_customer_id
        else:
            # 创建新客户
            print(f"   📝 创建新客户...")
            customer_id = create_customer_for_lead(token, lead)
            
            if not customer_id:
                print(f"   ❌ 创建客户失败")
                fail_count += 1
                continue
            
            print(f"   ✅ 客户创建成功: {customer_id}")
        
        # 更新线索
        print(f"   🔗 关联客户到线索...")
        if update_lead_customer(token, lead_id, customer_id):
            print(f"   ✅ 线索更新成功")
            success_count += 1
        else:
            print(f"   ❌ 线索更新失败")
            fail_count += 1
    
    # 6. 总结
    print("\n" + "=" * 70)
    print("修复完成！")
    print("=" * 70)
    print(f"✅ 成功: {success_count}")
    print(f"⏭️  跳过: {skip_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📊 总计: {len(leads_without_customer)}")
    
    if success_count > 0:
        print(f"\n⚠️  提醒：")
        print(f"   - 已为 {success_count} 个线索创建了客户记录")
        print(f"   - 这些客户使用临时信用代码（TEMP前缀）")
        print(f"   - 请提醒用户补充完整的客户信息")

if __name__ == "__main__":
    main()

