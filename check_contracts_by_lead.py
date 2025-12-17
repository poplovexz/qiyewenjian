#!/usr/bin/env python3
"""
检查特定线索生成的合同
"""
import sys
sys.path.insert(0, '/var/www/packages/backend/src')

from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from models.hetong_guanli import Hetong
from models.xiansuo_guanli import XiansuoBaojia, Xiansuo
from schemas.hetong_guanli import HetongResponse

def check_contracts_by_lead():
    """检查线索XS20251014001生成的合同"""
    db: Session = SessionLocal()
    
    try:
        # 查找线索
        xiansuo = db.query(Xiansuo).filter(
            Xiansuo.xiansuo_bianma == "XS20251014001",
            Xiansuo.is_deleted == "N"
        ).first()

        if not xiansuo:
            print("❌ 未找到线索 XS20251014001")
            return

        print(f"✅ 找到线索: {xiansuo.xiansuo_bianma}")
        print(f"   线索ID: {xiansuo.id}")
        print(f"   客户ID: {xiansuo.kehu_id}")
        
        # 查找该线索的报价
        baojia_list = db.query(XiansuoBaojia).filter(
            XiansuoBaojia.xiansuo_id == xiansuo.id,
            XiansuoBaojia.is_deleted == "N"
        ).all()
        
        print(f"\n📋 找到 {len(baojia_list)} 个报价:")
        for baojia in baojia_list:
            print(f"   - 报价ID: {baojia.id}, 状态: {baojia.baojia_zhuangtai}, 金额: {baojia.zongji_jine}")
            
            # 查找该报价生成的合同
            hetong_list = db.query(Hetong).options(
                joinedload(Hetong.kehu),
                joinedload(Hetong.hetong_moban)
            ).filter(
                Hetong.baojia_id == baojia.id,
                Hetong.is_deleted == "N"
            ).all()
            
            print(f"     生成了 {len(hetong_list)} 个合同:")
            for hetong in hetong_list:
                response = HetongResponse.model_validate(hetong)
                print(f"       合同编号: {response.hetong_bianhao}")
                print(f"       客户名称: {response.kehu.gongsi_mingcheng if response.kehu else '未知'}")
                print(f"       合同金额: ¥{response.hetong_jine or 0}")
                print(f"       payment_amount: {response.payment_amount}")
                print(f"       合同类型: {response.hetong_moban.hetong_leixing if response.hetong_moban else '未知'}")
                print(f"       状态: {response.hetong_zhuangtai}")
                print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_contracts_by_lead()

