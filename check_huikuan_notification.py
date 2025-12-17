#!/usr/bin/env python3
"""
检查银行汇款通知问题
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

def check_huikuan_notification():
    """检查汇款通知"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        huikuan_bianhao = "HK202510301443179ED9B3"
        
        print(f"\n{'='*80}")
        print(f"检查银行汇款通知问题")
        print(f"{'='*80}\n")
        
        # 查询汇款记录
        print(f"【1】查询汇款单据: {huikuan_bianhao}\n")

        huikuan_query = text("""
            SELECT
                id, danju_bianhao, hetong_zhifu_id,
                huikuan_jine, huikuan_riqi, huikuan_ren,
                shenhe_zhuangtai, shangchuan_ren_id,
                created_at, updated_at
            FROM yinhang_huikuan_danju
            WHERE danju_bianhao = :bianhao
        """)
        
        huikuan = session.execute(huikuan_query, {"bianhao": huikuan_bianhao}).fetchone()

        if not huikuan:
            print(f"❌ 找不到汇款单据: {huikuan_bianhao}")
            return

        print(f"✅ 找到汇款单据:")
        print(f"  ID: {huikuan.id}")
        print(f"  单据编号: {huikuan.danju_bianhao}")
        print(f"  合同支付ID: {huikuan.hetong_zhifu_id}")
        print(f"  汇款金额: {huikuan.huikuan_jine}")
        print(f"  汇款日期: {huikuan.huikuan_riqi}")
        print(f"  汇款人: {huikuan.huikuan_ren}")
        print(f"  审核状态: {huikuan.shenhe_zhuangtai}")
        print(f"  上传人ID: {huikuan.shangchuan_ren_id}")
        print(f"  创建时间: {huikuan.created_at}")
        print(f"  更新时间: {huikuan.updated_at}")
        
        # 查询相关通知
        print(f"\n{'='*80}")
        print(f"【2】查询相关通知\n")

        notification_query = text("""
            SELECT
                id, tongzhi_leixing, tongzhi_biaoti, tongzhi_neirong,
                lianjie_url, jieshou_ren_id, tongzhi_zhuangtai,
                created_at
            FROM zhifu_tongzhi
            WHERE tongzhi_neirong LIKE :pattern
            OR kuozhan_shuju LIKE :pattern
            ORDER BY created_at DESC
            LIMIT 10
        """)

        notifications = session.execute(
            notification_query,
            {"pattern": f"%{huikuan_bianhao}%"}
        ).fetchall()

        if notifications:
            print(f"✅ 找到 {len(notifications)} 条相关通知:")
            for notif in notifications:
                print(f"\n  通知ID: {notif.id}")
                print(f"  通知类型: {notif.tongzhi_leixing}")
                print(f"  通知标题: {notif.tongzhi_biaoti}")
                print(f"  接收用户ID: {notif.jieshou_ren_id}")
                print(f"  通知状态: {notif.tongzhi_zhuangtai}")
                print(f"  创建时间: {notif.created_at}")
        else:
            print(f"❌ 没有找到相关通知")
        
        # 查询审核流程
        print(f"\n{'='*80}")
        print(f"【3】查询审核流程\n")

        workflow_query = text("""
            SELECT
                id, liucheng_bianhao, shenhe_leixing, shenhe_zhuangtai,
                guanlian_id, shenqing_ren_id, dangqian_buzhou, zonggong_buzhou,
                created_at
            FROM shenhe_liucheng
            WHERE guanlian_id = :guanlian_id
            AND shenhe_leixing = 'yinhang_huikuan'
            AND is_deleted = 'N'
            ORDER BY created_at DESC
            LIMIT 5
        """)

        workflows = session.execute(
            workflow_query,
            {"guanlian_id": str(huikuan.id)}
        ).fetchall()
        
        if workflows:
            print(f"✅ 找到 {len(workflows)} 个审核流程:")
            for wf in workflows:
                print(f"\n  流程ID: {wf.id}")
                print(f"  流程编号: {wf.liucheng_bianhao}")
                print(f"  审核类型: {wf.shenhe_leixing}")
                print(f"  审核状态: {wf.shenhe_zhuangtai}")
                print(f"  关联ID: {wf.guanlian_id}")
                print(f"  申请人ID: {wf.shenqing_ren_id}")
                print(f"  当前步骤: {wf.dangqian_buzhou}/{wf.zonggong_buzhou}")
                print(f"  创建时间: {wf.created_at}")

                # 查询该流程的审核步骤
                step_query = text("""
                    SELECT
                        id, buzhou_bianhao, buzhou_mingcheng, shenhe_ren_id,
                        jilu_zhuangtai, shenhe_shijian
                    FROM shenhe_jilu
                    WHERE liucheng_id = :liucheng_id
                    AND is_deleted = 'N'
                    ORDER BY buzhou_bianhao
                """)

                steps = session.execute(
                    step_query,
                    {"liucheng_id": str(wf.id)}
                ).fetchall()

                if steps:
                    print(f"  审核步骤:")
                    for step in steps:
                        print(f"    - 步骤{step.buzhou_bianhao}: {step.buzhou_mingcheng} - {step.jilu_zhuangtai} (审核人: {step.shenhe_ren_id})")
        else:
            print(f"❌ 没有找到审核流程")
        
        # 检查后端日志
        print(f"\n{'='*80}")
        print(f"【4】检查后端日志（最近的汇款相关日志）\n")
        
        import subprocess
        try:
            log_result = subprocess.run(
                ["tail", "-100", "/tmp/backend_8000.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if log_result.returncode == 0:
                lines = log_result.stdout.split('\n')
                huikuan_lines = [line for line in lines if 'huikuan' in line.lower() or 'HK2025' in line]
                
                if huikuan_lines:
                    print(f"找到 {len(huikuan_lines)} 条汇款相关日志（最近100行）:")
                    for line in huikuan_lines[-10:]:  # 只显示最后10条
                        print(f"  {line}")
                else:
                    print("没有找到汇款相关日志")
            else:
                print("无法读取日志文件")
        except Exception as e:
            print(f"读取日志失败: {e}")
        
        # 分析问题
        print(f"\n{'='*80}")
        print(f"【5】问题分析\n")
        
        if not notifications:
            print("❌ 问题确认：没有发送通知")
            print("\n可能的原因：")
            
            if not workflows:
                print("  1. ❌ 没有创建审核流程")
                print("     → 检查汇款创建时是否调用了审核流程创建")
            else:
                print("  1. ✅ 审核流程已创建")
                print("     → 检查审核流程引擎是否发送了通知")
            
            print("\n  2. 检查通知服务是否正常工作")
            print("  3. 检查审核流程配置是否正确")
        else:
            print("✅ 已发送通知")
            print(f"   共 {len(notifications)} 条通知")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_huikuan_notification()

