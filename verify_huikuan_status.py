#!/usr/bin/env python3
"""
验证银行汇款状态和审核规则配置
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import text
import json

# 从后端配置获取数据库连接
from core.database import SessionLocal

def get_session():
    """获取数据库会话"""
    return SessionLocal()

def check_huikuan_status():
    """检查汇款单据当前状态"""
    session = get_session()
    try:
        print("="*80)
        print("【任务1】检查汇款单据当前状态")
        print("="*80)
        
        query = text("""
            SELECT 
                id, danju_bianhao, huikuan_jine, huikuan_ren, 
                huikuan_yinhang, shenhe_zhuangtai, 
                shangchuan_ren_id, shangchuan_shijian,
                danju_lujing, created_at, updated_at
            FROM yinhang_huikuan_danju 
            WHERE danju_bianhao = :bianhao
            AND is_deleted = 'N'
        """)
        
        result = session.execute(query, {"bianhao": "HK202510301443179ED9B3"}).fetchone()
        
        if result:
            print("\n✅ 找到汇款单据:\n")
            print(f"  单据编号: {result.danju_bianhao}")
            print(f"  汇款金额: {result.huikuan_jine}")
            print(f"  汇款人: {result.huikuan_ren}")
            print(f"  汇款银行: {result.huikuan_yinhang}")
            print(f"  审核状态: {result.shenhe_zhuangtai}")
            print(f"  上传人ID: {result.shangchuan_ren_id}")
            print(f"  上传时间: {result.shangchuan_shijian}")
            print(f"  凭证路径: {result.danju_lujing or '未上传'}")
            print(f"  创建时间: {result.created_at}")
            print(f"  更新时间: {result.updated_at}")
            
            # 判断状态变化
            if result.shenhe_zhuangtai == 'waiting_voucher':
                print("\n⚠️  状态未变化：仍在等待业务员上传凭证")
                return 'waiting_voucher', result.id
            elif result.shenhe_zhuangtai == 'pending_audit':
                print("\n✅ 状态已变化：已上传凭证，等待审核")
                return 'pending_audit', result.id
            else:
                print(f"\n✅ 状态：{result.shenhe_zhuangtai}")
                return result.shenhe_zhuangtai, result.id
        else:
            print("\n❌ 未找到汇款单据")
            return None, None
            
    finally:
        session.close()

def check_audit_workflow(danju_id):
    """检查是否创建了审核流程"""
    session = get_session()
    try:
        print(f"\n{'='*80}")
        print("【任务1.1】检查审核流程")
        print("="*80)
        
        query = text("""
            SELECT 
                id, liucheng_bianhao, shenhe_leixing, shenhe_zhuangtai,
                shenqing_ren_id, dangqian_buzhou, zonggong_buzhou,
                created_at
            FROM shenhe_liucheng 
            WHERE guanlian_id = :guanlian_id
            AND shenhe_leixing = 'yinhang_huikuan'
            AND is_deleted = 'N'
            ORDER BY created_at DESC
        """)
        
        workflows = session.execute(query, {"guanlian_id": danju_id}).fetchall()
        
        if workflows:
            print(f"\n✅ 找到 {len(workflows)} 个审核流程:\n")
            for wf in workflows:
                print(f"  流程编号: {wf.liucheng_bianhao}")
                print(f"  审核类型: {wf.shenhe_leixing}")
                print(f"  审核状态: {wf.shenhe_zhuangtai}")
                print(f"  当前步骤: {wf.dangqian_buzhou}/{wf.zonggong_buzhou}")
                print(f"  创建时间: {wf.created_at}")
                
                # 检查审核步骤
                step_query = text("""
                    SELECT 
                        buzhou_bianhao, buzhou_mingcheng, shenhe_ren_id,
                        jilu_zhuangtai, shenhe_shijian
                    FROM shenhe_jilu
                    WHERE liucheng_id = :liucheng_id
                    AND is_deleted = 'N'
                    ORDER BY buzhou_bianhao
                """)
                
                steps = session.execute(step_query, {"liucheng_id": wf.id}).fetchall()
                if steps:
                    print("  审核步骤:")
                    for step in steps:
                        print(f"    - 步骤{step.buzhou_bianhao}: {step.buzhou_mingcheng} - {step.jilu_zhuangtai} (审核人: {step.shenhe_ren_id})")
                print()
            return True
        else:
            print("\n❌ 未找到审核流程")
            return False
            
    finally:
        session.close()

def check_notifications(danju_bianhao):
    """检查通知"""
    session = get_session()
    try:
        print(f"\n{'='*80}")
        print("【任务1.2】检查通知")
        print("="*80)
        
        query = text("""
            SELECT 
                id, tongzhi_leixing, tongzhi_biaoti, 
                jieshou_ren_id, tongzhi_zhuangtai,
                fasong_shijian, yuedu_shijian
            FROM zhifu_tongzhi 
            WHERE tongzhi_neirong LIKE :pattern
            OR kuozhan_shuju LIKE :pattern
            ORDER BY fasong_shijian DESC
        """)
        
        notifications = session.execute(query, {"pattern": f"%{danju_bianhao}%"}).fetchall()
        
        if notifications:
            print(f"\n✅ 找到 {len(notifications)} 条通知:\n")
            for notif in notifications:
                print(f"  通知类型: {notif.tongzhi_leixing}")
                print(f"  通知标题: {notif.tongzhi_biaoti}")
                print(f"  接收人ID: {notif.jieshou_ren_id}")
                print(f"  通知状态: {notif.tongzhi_zhuangtai}")
                print(f"  发送时间: {notif.fasong_shijian}")
                print(f"  阅读时间: {notif.yuedu_shijian or '未读'}")
                print()
            return True
        else:
            print("\n❌ 未找到通知")
            return False
            
    finally:
        session.close()

def check_audit_rules():
    """检查审核规则配置"""
    session = get_session()
    try:
        print(f"\n{'='*80}")
        print("【任务2】检查审核规则配置")
        print("="*80)
        
        # 查询所有工作流模板类型的规则
        query = text("""
            SELECT 
                id, guize_mingcheng, guize_leixing, 
                chufa_tiaojian, shenhe_liucheng_peizhi,
                shi_qiyong, paixu
            FROM shenhe_guize 
            WHERE guize_leixing = 'workflow_template'
            AND shi_qiyong = 'Y'
            AND is_deleted = 'N'
            ORDER BY paixu
        """)
        
        rules = session.execute(query).fetchall()
        
        print(f"\n找到 {len(rules)} 个工作流模板规则:\n")
        
        yinhang_huikuan_rule = None
        for rule in rules:
            try:
                condition = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian
                audit_type = condition.get('audit_type', 'N/A')
                
                print(f"  规则ID: {rule.id}")
                print(f"  规则名称: {rule.guize_mingcheng}")
                print(f"  审核类型: {audit_type}")
                print(f"  是否启用: {rule.shi_qiyong}")
                print(f"  排序: {rule.paixu}")
                
                if audit_type == 'yinhang_huikuan':
                    yinhang_huikuan_rule = rule
                    print("  ✅ 这是银行汇款审核规则")
                    
                    # 解析审核流程配置
                    flow_config = json.loads(rule.shenhe_liucheng_peizhi) if isinstance(rule.shenhe_liucheng_peizhi, str) else rule.shenhe_liucheng_peizhi
                    steps = flow_config.get('steps', [])
                    print(f"  审核步骤数: {len(steps)}")
                    for step in steps:
                        print(f"    - 步骤{step.get('step_order', step.get('step'))}: {step.get('step_name', step.get('name'))} (审核人ID: {step.get('approver_user_id', '未配置')})")
                
                print()
            except Exception as e:
                print(f"  解析规则失败: {e}")
                print()
        
        if yinhang_huikuan_rule:
            print("\n✅ 找到银行汇款审核规则配置")
            return True
        else:
            print("\n❌ 未找到银行汇款审核规则配置")
            print("\n⚠️  需要创建 audit_type='yinhang_huikuan' 的审核规则")
            return False
            
    finally:
        session.close()

def main():
    print("\n" + "="*80)
    print("银行汇款通知问题验证")
    print("="*80 + "\n")
    
    # 任务1：检查汇款单据状态
    status, danju_id = check_huikuan_status()
    
    if status and danju_id:
        # 任务1.1：检查审核流程
        has_workflow = check_audit_workflow(danju_id)
        
        # 任务1.2：检查通知
        has_notification = check_notifications("HK202510301443179ED9B3")
        
        # 总结任务1
        print(f"\n{'='*80}")
        print("【任务1总结】")
        print("="*80)
        print(f"\n当前状态: {status}")
        print(f"审核流程: {'✅ 已创建' if has_workflow else '❌ 未创建'}")
        print(f"通知: {'✅ 已发送' if has_notification else '❌ 未发送'}")
        
        if status == 'waiting_voucher':
            print("\n⚠️  下一步：业务员需要上传汇款凭证")
        elif status == 'pending_audit':
            if has_workflow and has_notification:
                print("\n✅ 流程正常：已触发审核并发送通知")
            elif has_workflow and not has_notification:
                print("\n⚠️  问题：审核流程已创建，但未发送通知")
            else:
                print("\n⚠️  问题：已上传凭证，但未触发审核流程")
    
    # 任务2：检查审核规则配置
    has_rule = check_audit_rules()
    
    # 总结任务2
    print(f"\n{'='*80}")
    print("【任务2总结】")
    print("="*80)
    if has_rule:
        print("\n✅ 审核规则配置正常")
    else:
        print("\n❌ 缺少银行汇款审核规则配置")
        print("\n建议：创建 audit_type='yinhang_huikuan' 的审核规则")
    
    print(f"\n{'='*80}")
    print("验证完成")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

