#!/usr/bin/env python3
"""
修复当前汇款单据：分配给真实业务员并发送通知
"""
import sys
sys.path.insert(0, 'packages/backend/src')

from core.database import SessionLocal
from models.zhifu_guanli.yinhang_huikuan_danju import YinhangHuikuanDanju
from models.zhifu_guanli.zhifu_tongzhi import ZhifuTongzhi
from models.yonghu_guanli.yonghu import Yonghu
from models.hetong_guanli.hetong import Hetong
from datetime import datetime
import uuid

def fix_huikuan_danju():
    """修复汇款单据"""
    session = SessionLocal()
    
    try:
        # 1. 查询汇款单据
        danju = session.query(YinhangHuikuanDanju).filter(
            YinhangHuikuanDanju.danju_bianhao == 'HK202510301443179ED9B3'
        ).first()
        
        if not danju:
            print("❌ 未找到汇款单据")
            return
        
        print("="*80)
        print("📋 当前汇款单据信息：")
        print(f"单据编号: {danju.danju_bianhao}")
        print(f"状态: {danju.shenhe_zhuangtai}")
        print(f"当前分配给: {danju.shangchuan_ren_id}")
        print("="*80)
        
        # 2. 查找业务员用户（yewu001）
        yewuyuan = session.query(Yonghu).filter(
            Yonghu.yonghu_ming == 'yewu001',
            Yonghu.is_deleted == 'N'
        ).first()
        
        if not yewuyuan:
            print("❌ 未找到业务员用户（yewu001）")
            return
        
        print(f"\n✅ 找到业务员：{yewuyuan.xingming}（{yewuyuan.yonghu_ming}）")
        print(f"业务员ID: {yewuyuan.id}")
        
        # 3. 更新汇款单据，分配给业务员
        old_shangchuan_ren_id = danju.shangchuan_ren_id
        danju.shangchuan_ren_id = yewuyuan.id
        danju.updated_at = datetime.now()
        
        print(f"\n✅ 更新汇款单据：{old_shangchuan_ren_id} → {yewuyuan.id}")
        
        # 4. 查询合同信息（用于通知内容）
        hetong = None
        kehu_mingcheng = "客户"
        hetong_bianhao = ""
        
        if danju.hetong_zhifu_id:
            from models.zhifu_guanli.hetong_zhifu import HetongZhifu
            hetong_zhifu = session.query(HetongZhifu).filter(
                HetongZhifu.id == danju.hetong_zhifu_id,
                HetongZhifu.is_deleted == 'N'
            ).first()
            
            if hetong_zhifu and hetong_zhifu.hetong_id:
                hetong = session.query(Hetong).filter(
                    Hetong.id == hetong_zhifu.hetong_id,
                    Hetong.is_deleted == 'N'
                ).first()
                
                if hetong:
                    hetong_bianhao = hetong.hetong_bianhao
                    if hetong.kehu_id:
                        from models.kehu_guanli.kehu import Kehu
                        kehu = session.query(Kehu).filter(
                            Kehu.id == hetong.kehu_id,
                            Kehu.is_deleted == 'N'
                        ).first()
                        if kehu:
                            kehu_mingcheng = kehu.gongsi_mingcheng
        
        # 5. 创建通知
        tongzhi = ZhifuTongzhi(
            id=str(uuid.uuid4()),
            hetong_id=hetong.id if hetong else None,
            jieshou_ren_id=yewuyuan.id,
            tongzhi_leixing="task_assigned",
            tongzhi_biaoti="新的银行汇款单据待处理",
            tongzhi_neirong=f"{kehu_mingcheng}已确认使用银行转账支付，单据编号：{danju.danju_bianhao}，金额：¥{danju.huikuan_jine}，请及时上传汇款凭证并填写汇款信息。",
            tongzhi_zhuangtai="unread",
            youxian_ji="high",
            fasong_shijian=datetime.now(),
            lianjie_url="/payment/bank-transfer-manage",
            kuozhan_shuju=f'{{"danju_id": "{danju.id}", "danju_bianhao": "{danju.danju_bianhao}", "hetong_bianhao": "{hetong_bianhao}"}}',
            created_by="system",
            updated_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        session.add(tongzhi)
        
        print(f"\n✅ 创建通知：")
        print(f"   接收人: {yewuyuan.xingming}（{yewuyuan.yonghu_ming}）")
        print(f"   通知类型: {tongzhi.tongzhi_leixing}")
        print(f"   通知标题: {tongzhi.tongzhi_biaoti}")
        print(f"   通知内容: {tongzhi.tongzhi_neirong}")
        print(f"   优先级: {tongzhi.youxian_ji}")
        print(f"   链接URL: {tongzhi.lianjie_url}")
        
        # 6. 提交事务
        session.commit()
        
        print("\n" + "="*80)
        print("✅ 修复完成！")
        print("="*80)
        print("\n📧 业务员现在可以：")
        print("1. 登录系统（用户名：yewu001，密码：yewu123456）")
        print("2. 查看通知中心，看到新的银行汇款单据待处理通知")
        print("3. 点击通知链接，进入银行汇款管理页面")
        print("4. 上传汇款凭证并填写汇款信息")
        print("5. 提交后自动触发审核流程，财务收到通知")
        print("="*80)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    fix_huikuan_danju()

