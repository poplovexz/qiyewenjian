#!/usr/bin/env python3
"""
前端报价数据加载调试脚本
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def login():
    """登录获取token"""
    print("🔐 正在登录...")
    response = requests.post(f"{API_BASE}/api/v1/auth/login", json={
        "yonghu_ming": "admin",
        "mima": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token", {})
        if isinstance(token, dict):
            access_token = token.get("access_token")
        else:
            access_token = token
        print(f"✅ 登录成功，token: {access_token[:20]}...")
        return access_token
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return None

def get_leads(token):
    """获取线索列表"""
    print("📋 获取线索列表...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/leads/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        leads = data.get("items", [])
        print(f"✅ 获取到 {len(leads)} 个线索")
        return leads
    else:
        print(f"❌ 获取线索失败: {response.status_code}")
        return []

def get_baojia_for_lead(token, lead_id):
    """获取指定线索的报价列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/lead-quotes/xiansuo/{lead_id}", headers=headers)
    
    if response.status_code == 200:
        baojia_list = response.json()
        return baojia_list
    else:
        print(f"❌ 获取线索 {lead_id} 的报价失败: {response.status_code}")
        return []

def simulate_prefetch_baojia(token, leads):
    """模拟前端的prefetchBaojiaForLeads方法"""
    print("\n🔄 模拟前端prefetchBaojiaForLeads方法...")
    
    # 模拟baojiaMap缓存
    baojia_map = {}
    
    # 过滤需要预取的线索（模拟前端逻辑）
    leads_to_prefetch = []
    for lead in leads:
        lead_id = lead.get("id")
        if lead_id not in baojia_map:
            leads_to_prefetch.append(lead_id)
    
    print(f"📝 需要预取报价的线索: {len(leads_to_prefetch)} 个")
    
    # 并发获取报价数据（这里简化为串行）
    for lead_id in leads_to_prefetch:
        print(f"🔍 正在获取线索 {lead_id} 的报价...")
        baojia_list = get_baojia_for_lead(token, lead_id)
        baojia_map[lead_id] = baojia_list
        print(f"   ✅ 获取到 {len(baojia_list)} 个报价")
        
        # 显示报价详情
        for i, baojia in enumerate(baojia_list):
            status = baojia.get("baojia_zhuangtai", "unknown")
            expired = baojia.get("is_expired", False)
            created = baojia.get("created_at", "")
            print(f"      报价 {i+1}: 状态={status}, 过期={expired}, 创建时间={created}")
    
    return baojia_map

def check_button_logic(lead, baojia_list):
    """检查按钮显示逻辑"""
    lead_id = lead.get("id")
    lead_name = lead.get("gongsi_mingcheng", "未知公司")
    lead_status = lead.get("dangqian_zhuangtai") or lead.get("xiansuo_zhuangtai", "new")
    
    print(f"\n🔍 检查线索 {lead_name} ({lead_id}) 的按钮逻辑:")
    print(f"   线索状态: {lead_status}")
    print(f"   报价数量: {len(baojia_list)}")
    
    # 检查是否有有效报价（模拟hasValidBaojia）
    valid_baojia = []
    for baojia in baojia_list:
        is_expired = baojia.get("is_expired", False)
        status = baojia.get("baojia_zhuangtai", "")
        if not is_expired and status != "rejected":
            valid_baojia.append(baojia)
    
    has_valid_baojia = len(valid_baojia) > 0 or lead_status in ["quoted", "won"]
    print(f"   有效报价数量: {len(valid_baojia)}")
    print(f"   hasValidBaojia: {has_valid_baojia}")
    
    # 获取最新报价状态（模拟getBaojiaStatus）
    latest_status = None
    if valid_baojia:
        # 按创建时间排序，获取最新的
        sorted_baojia = sorted(valid_baojia, key=lambda x: x.get("created_at", ""), reverse=True)
        latest_status = sorted_baojia[0].get("baojia_zhuangtai")
    
    print(f"   最新报价状态: {latest_status}")
    
    # 判断按钮显示
    show_quote_button = not has_valid_baojia
    show_view_button = has_valid_baojia
    show_contract_button = has_valid_baojia and latest_status == "accepted"
    
    print(f"   按钮显示:")
    print(f"     报价按钮: {'显示' if show_quote_button else '隐藏'}")
    print(f"     查看报价按钮: {'显示' if show_view_button else '隐藏'}")
    print(f"     生成合同按钮: {'显示' if show_contract_button else '隐藏'}")
    
    return {
        "has_valid_baojia": has_valid_baojia,
        "latest_status": latest_status,
        "show_quote_button": show_quote_button,
        "show_view_button": show_view_button,
        "show_contract_button": show_contract_button
    }

def main():
    print("🚀 开始前端报价数据加载调试...")
    
    # 登录
    token = login()
    if not token:
        return
    
    # 获取线索列表
    leads = get_leads(token)
    if not leads:
        return
    
    # 模拟前端预取报价数据
    baojia_map = simulate_prefetch_baojia(token, leads)
    
    # 检查每个线索的按钮逻辑
    print("\n" + "="*60)
    print("📊 按钮显示逻辑检查结果:")
    print("="*60)
    
    for lead in leads:
        lead_id = lead.get("id")
        baojia_list = baojia_map.get(lead_id, [])
        button_logic = check_button_logic(lead, baojia_list)
    
    print("\n🎉 调试完成！")

if __name__ == "__main__":
    main()