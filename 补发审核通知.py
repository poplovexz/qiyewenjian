#!/usr/bin/env python3
"""
为现有的审核流程补发通知
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
backend_dir = Path(__file__).parent / "packages" / "backend"
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

from models.shenhe_guanli import ShenheLiucheng, ShenheJilu
from models.zhifu_guanli import ZhifuTongzhi
from models.yonghu_guanli import Yonghu

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def send_notification_for_workflow(db, workflow: ShenheLiucheng):
    """为审核流程发送通知"""
    try:
        # 审核类型映射
        audit_type_map = {
            "hetong": "合同审核",
            "hetong_jine_xiuzheng": "合同金额修正审核",
            "baojia": "报价审核",
            "yinhang_huikuan": "银行汇款审核"
        }
        
        audit_type_name = audit_type_map.get(workflow.shenhe_leixing, workflow.shenhe_leixing)
        
        # 根据审核状态发送不同的通知
        if workflow.shenhe_zhuangtai == "shenhzhong":
            # 审核中 - 发送通知给当前审核人
            current_step = db.query(ShenheJilu).filter(
                ShenheJilu.liucheng_id == workflow.id,
                ShenheJilu.buzhou_bianhao == workflow.dangqian_buzhou,
                ShenheJilu.is_deleted == "N"
            ).first()
            
            if current_step and current_step.shenhe_ren_id:
                # 获取申请人信息
                applicant = db.query(Yonghu).filter(
                    Yonghu.id == workflow.shenqing_ren_id,
                    Yonghu.is_deleted == "N"
                ).first()
                
                applicant_name = applicant.xingming if applicant else "未知用户"
                
                tongzhi_biaoti = f"【待审核】{audit_type_name} - {workflow.liucheng_bianhao}"
                tongzhi_neirong = f"""
您有一个待处理的审核任务：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请人：{applicant_name}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
申请原因：{workflow.shenqing_yuanyin or '无'}
当前步骤：第 {workflow.dangqian_buzhou} 步（共 {workflow.zonggong_buzhou} 步）

请及时登录系统进行审核。
                """.strip()
                
                # 创建通知
                notification = ZhifuTongzhi(
                    jieshou_ren_id=current_step.shenhe_ren_id,
                    tongzhi_leixing="audit_pending",
                    tongzhi_biaoti=tongzhi_biaoti,
                    tongzhi_neirong=tongzhi_neirong,
                    youxian_ji="high",
                    fasong_shijian=datetime.now(),
                    fasong_qudao="system",
                    tongzhi_zhuangtai="unread",
                    lianjie_url=f"/audit/workflow/{workflow.id}",
                    kuozhan_shuju=json.dumps({
                        "workflow_id": workflow.id,
                        "audit_type": workflow.shenhe_leixing,
                        "step_id": current_step.id,
                        "step_number": current_step.buzhou_bianhao
                    }),
                    created_by="system"
                )
                
                db.add(notification)
                print("  ✅ 已为审核人创建待审核通知")
                return True
        
        elif workflow.shenhe_zhuangtai == "yitongguo":
            # 已通过 - 发送通知给申请人
            if workflow.shenqing_ren_id:
                tongzhi_biaoti = f"【审核通过】{audit_type_name} - {workflow.liucheng_bianhao}"
                tongzhi_neirong = f"""
您的审核申请已通过：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
完成时间：{workflow.wancheng_shijian.strftime('%Y-%m-%d %H:%M:%S') if workflow.wancheng_shijian else '未知'}

您的申请已全部审核通过，可以继续后续操作。
                """.strip()
                
                # 创建通知
                notification = ZhifuTongzhi(
                    jieshou_ren_id=workflow.shenqing_ren_id,
                    tongzhi_leixing="audit_approved",
                    tongzhi_biaoti=tongzhi_biaoti,
                    tongzhi_neirong=tongzhi_neirong,
                    youxian_ji="normal",
                    fasong_shijian=datetime.now(),
                    fasong_qudao="system",
                    tongzhi_zhuangtai="unread",
                    lianjie_url=f"/audit/workflow/{workflow.id}",
                    kuozhan_shuju=json.dumps({
                        "workflow_id": workflow.id,
                        "audit_type": workflow.shenhe_leixing,
                        "result": "approved"
                    }),
                    created_by="system"
                )
                
                db.add(notification)
                print("  ✅ 已为申请人创建审核通过通知")
                return True
        
        elif workflow.shenhe_zhuangtai == "jujue":
            # 已拒绝 - 发送通知给申请人
            if workflow.shenqing_ren_id:
                # 查找拒绝的审核步骤
                rejected_step = db.query(ShenheJilu).filter(
                    ShenheJilu.liucheng_id == workflow.id,
                    ShenheJilu.shenhe_jieguo == "jujue",
                    ShenheJilu.is_deleted == "N"
                ).first()
                
                rejection_reason = rejected_step.shenhe_yijian if rejected_step else "无"
                
                tongzhi_biaoti = f"【审核拒绝】{audit_type_name} - {workflow.liucheng_bianhao}"
                tongzhi_neirong = f"""
您的审核申请已被拒绝：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
拒绝时间：{workflow.wancheng_shijian.strftime('%Y-%m-%d %H:%M:%S') if workflow.wancheng_shijian else '未知'}
拒绝原因：{rejection_reason}

如有疑问，请联系审核人了解详情。
                """.strip()
                
                # 创建通知
                notification = ZhifuTongzhi(
                    jieshou_ren_id=workflow.shenqing_ren_id,
                    tongzhi_leixing="audit_rejected",
                    tongzhi_biaoti=tongzhi_biaoti,
                    tongzhi_neirong=tongzhi_neirong,
                    youxian_ji="high",
                    fasong_shijian=datetime.now(),
                    fasong_qudao="system",
                    tongzhi_zhuangtai="unread",
                    lianjie_url=f"/audit/workflow/{workflow.id}",
                    kuozhan_shuju=json.dumps({
                        "workflow_id": workflow.id,
                        "audit_type": workflow.shenhe_leixing,
                        "result": "rejected",
                        "rejection_reason": rejection_reason
                    }),
                    created_by="system"
                )
                
                db.add(notification)
                print("  ✅ 已为申请人创建审核拒绝通知")
                return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ 发送通知失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("为现有审核流程补发通知")
        print("=" * 60)
        print()
        
        # 查询所有审核流程
        workflows = db.query(ShenheLiucheng).filter(
            ShenheLiucheng.is_deleted == "N"
        ).order_by(ShenheLiucheng.created_at.desc()).all()
        
        print(f"找到 {len(workflows)} 个审核流程")
        print()
        
        success_count = 0
        skip_count = 0
        
        for workflow in workflows:
            print(f"处理流程: {workflow.liucheng_bianhao}")
            print(f"  类型: {workflow.shenhe_leixing}")
            print(f"  状态: {workflow.shenhe_zhuangtai}")
            
            # 检查是否已有通知
            existing_notif = db.query(ZhifuTongzhi).filter(
                ZhifuTongzhi.kuozhan_shuju.like(f'%{workflow.id}%'),
                ZhifuTongzhi.is_deleted == "N"
            ).first()
            
            if existing_notif:
                print("  ⏭️  已有通知，跳过")
                skip_count += 1
            else:
                if send_notification_for_workflow(db, workflow):
                    success_count += 1
            
            print()
        
        # 提交所有更改
        db.commit()
        
        print("=" * 60)
        print("补发完成:")
        print(f"  成功: {success_count} 条")
        print(f"  跳过: {skip_count} 条")
        print(f"  总计: {len(workflows)} 条")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

