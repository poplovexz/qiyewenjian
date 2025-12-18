#!/usr/bin/env python3
"""
验证银行汇款审核配置
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from core.database import SessionLocal
from sqlalchemy import text
import json

def main():
    print("\n" + "="*80)
    print("验证银行汇款审核配置")
    print("="*80 + "\n")
    
    session = SessionLocal()
    
    try:
        # 1. 验证角色
        print("【1】角色配置")
        print("-"*80)
        
        role_query = text("""
            SELECT id, jiaose_ming, jiaose_bianma, zhuangtai
            FROM jiaose
            WHERE is_deleted = 'N'
            AND jiaose_bianma IN ('caiwu', 'yewuyuan', 'admin')
            ORDER BY created_at
        """)
        
        roles = session.execute(role_query).fetchall()
        print(f"找到 {len(roles)} 个角色:\n")
        
        for role in roles:
            print(f"  ✅ {role.jiaose_ming} ({role.jiaose_bianma})")
            print(f"     ID: {role.id}")
            print(f"     状态: {role.zhuangtai}")
            print()
        
        # 2. 验证用户
        print("\n【2】用户配置")
        print("-"*80)
        
        user_query = text("""
            SELECT 
                y.id, y.yonghu_ming, y.xingming, y.zhuangtai,
                j.jiaose_ming, j.jiaose_bianma
            FROM yonghu y
            LEFT JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id AND yj.is_deleted = 'N'
            LEFT JOIN jiaose j ON yj.jiaose_id = j.id AND j.is_deleted = 'N'
            WHERE y.is_deleted = 'N'
            AND y.yonghu_ming IN ('caiwu001', 'yewu001')
            ORDER BY y.created_at
        """)
        
        users = session.execute(user_query).fetchall()
        print(f"找到 {len(users)} 个用户:\n")
        
        caiwu_user_id = None
        yewu_user_id = None
        
        for user in users:
            print(f"  ✅ {user.xingming} ({user.yonghu_ming})")
            print(f"     ID: {user.id}")
            print(f"     角色: {user.jiaose_ming or '未分配'} ({user.jiaose_bianma or 'N/A'})")
            print(f"     状态: {user.zhuangtai}")
            print()
            
            if user.jiaose_bianma == 'caiwu':
                caiwu_user_id = user.id
            elif user.jiaose_bianma == 'yewuyuan':
                yewu_user_id = user.id
        
        # 3. 验证审核规则
        print("\n【3】审核规则配置")
        print("-"*80)
        
        rule_query = text("""
            SELECT 
                id, guize_mingcheng, chufa_tiaojian, 
                shenhe_liucheng_peizhi, shi_qiyong
            FROM shenhe_guize
            WHERE id = '6218e1e3-0c1b-459f-8cfa-e7d27a735a4c'
            AND is_deleted = 'N'
        """)
        
        rule = session.execute(rule_query).fetchone()
        
        if rule:
            print(f"规则名称: {rule.guize_mingcheng}")
            print(f"规则ID: {rule.id}")
            print(f"是否启用: {rule.shi_qiyong}")
            
            # 解析触发条件
            condition = rule.chufa_tiaojian
            if isinstance(condition, str):
                condition = json.loads(condition)
            
            print("\n触发条件:")
            print(f"  类型: {condition.get('type')}")
            print(f"  审核类型: {condition.get('audit_type')}")
            
            # 解析审核流程配置
            config = rule.shenhe_liucheng_peizhi
            if isinstance(config, str):
                config = json.loads(config)
            
            print("\n审核流程配置:")
            steps = config.get('steps', [])
            print(f"  步骤数: {len(steps)}")
            
            for i, step in enumerate(steps, 1):
                print(f"\n  步骤 {i}:")
                print(f"    步骤编号: {step.get('step')}")
                print(f"    步骤名称: {step.get('name')}")
                print(f"    审核人ID: {step.get('approver_user_id')}")
                print(f"    审核角色: {step.get('approver_role')}")
                print(f"    预期时间: {step.get('expected_time')}小时")
                
                # 验证审核人
                approver_id = step.get('approver_user_id')
                if approver_id:
                    if approver_id == caiwu_user_id:
                        print("    ✅ 审核人已正确配置（财务用户）")
                    else:
                        print("    ⚠️  审核人ID与财务用户不匹配")
                else:
                    print("    ❌ 审核人ID未配置")
        else:
            print("❌ 未找到审核规则")
        
        # 4. 测试审核流程触发
        print("\n\n【4】测试审核流程触发")
        print("-"*80)
        
        print("\n模拟场景：业务员上传银行汇款凭证")
        print(f"  业务员ID: {yewu_user_id or '未找到'}")
        print(f"  财务审核人ID: {caiwu_user_id or '未找到'}")
        
        if caiwu_user_id and yewu_user_id:
            print("\n✅ 配置完整，可以触发审核流程")
            print("\n预期流程:")
            print(f"  1. 业务员({yewu_user_id})上传汇款凭证")
            print("  2. 系统触发审核流程（audit_type='yinhang_huikuan'）")
            print("  3. 查找审核规则（规则ID: 6218e1e3-0c1b-459f-8cfa-e7d27a735a4c）")
            print("  4. 创建审核流程实例")
            print(f"  5. 创建审核步骤（审核人: {caiwu_user_id}）")
            print(f"  6. 发送通知给财务用户({caiwu_user_id})")
        else:
            print("\n❌ 配置不完整，无法触发审核流程")
            if not caiwu_user_id:
                print("  - 缺少财务用户")
            if not yewu_user_id:
                print("  - 缺少业务员用户")
        
        # 5. 总结
        print("\n\n" + "="*80)
        print("配置总结")
        print("="*80)
        
        checks = [
            ("角色配置", len(roles) >= 2),
            ("用户配置", len(users) >= 2),
            ("财务用户", caiwu_user_id is not None),
            ("业务员用户", yewu_user_id is not None),
            ("审核规则", rule is not None),
            ("审核人配置", caiwu_user_id and rule and json.loads(rule.shenhe_liucheng_peizhi if isinstance(rule.shenhe_liucheng_peizhi, str) else json.dumps(rule.shenhe_liucheng_peizhi)).get('steps', [{}])[0].get('approver_user_id') == caiwu_user_id)
        ]
        
        all_passed = all(check[1] for check in checks)
        
        print()
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        print()
        if all_passed:
            print("✅ 所有配置检查通过！银行汇款审核流程已就绪。")
            print("\n下一步操作:")
            print("  1. 业务员登录系统（用户名: yewu001, 密码: yewu123456）")
            print("  2. 进入银行汇款管理页面")
            print("  3. 找到待上传凭证的单据（HK202510301443179ED9B3）")
            print("  4. 上传汇款凭证并填写汇款信息")
            print("  5. 提交后系统自动触发审核流程")
            print("  6. 财务用户收到审核通知")
        else:
            print("❌ 部分配置检查未通过，请修复后再试。")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()

