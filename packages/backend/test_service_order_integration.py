"""
测试服务工单集成功能
"""
import sys
sys.path.insert(0, 'src')

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.hetong_guanli import Hetong
from models.xiansuo_guanli import XiansuoBaojia, XiansuoBaojiaXiangmu
from models.chanpin_guanli import ChanpinXiangmu, ChanpinBuzou
from services.fuwu_guanli.fuwu_gongdan_service import FuwuGongdanService

def test_service_order_creation():
    """测试基于合同创建服务工单"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("测试服务工单创建功能")
        print("=" * 80)
        
        # 1. 查找一个已签署的合同
        print("\n1. 查找已签署的合同...")
        hetong = db.query(Hetong).filter(
            Hetong.hetong_zhuangtai == "signed",
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            print("❌ 没有找到已签署的合同，请先创建并签署一个合同")
            return
        
        print(f"✅ 找到合同: {hetong.hetong_bianhao} - {hetong.hetong_mingcheng}")
        print(f"   合同ID: {hetong.id}")
        print(f"   报价ID: {hetong.baojia_id}")
        
        # 2. 查看合同关联的报价和产品
        if hetong.baojia_id:
            print("\n2. 查看合同关联的报价...")
            baojia = db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == hetong.baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()
            
            if baojia:
                print(f"✅ 找到报价: {baojia.baojia_bianhao}")
                print(f"   报价项目数: {len(baojia.xiangmu_list)}")
                
                # 查看每个报价项目的产品步骤
                for idx, baojia_xiangmu in enumerate(baojia.xiangmu_list, 1):
                    if baojia_xiangmu.chanpin_xiangmu_id:
                        chanpin = db.query(ChanpinXiangmu).filter(
                            ChanpinXiangmu.id == baojia_xiangmu.chanpin_xiangmu_id,
                            ChanpinXiangmu.is_deleted == "N"
                        ).first()
                        
                        if chanpin:
                            print(f"\n   报价项目 {idx}: {chanpin.xiangmu_mingcheng}")
                            print(f"   产品步骤数: {len(chanpin.buzou_list)}")
                            
                            for buzou in chanpin.buzou_list:
                                if buzou.is_deleted == "N" and buzou.zhuangtai == "active":
                                    print(f"     - {buzou.buzou_mingcheng}: {buzou.yugu_shichang} {buzou.shichang_danwei}")
        else:
            print("\n⚠️  合同没有关联报价，将使用默认模板")
        
        # 3. 创建服务工单
        print("\n3. 创建服务工单...")
        service = FuwuGongdanService(db)
        
        try:
            gongdan = service.create_gongdan_from_hetong(hetong.id, "test_user")
            print("✅ 服务工单创建成功!")
            print(f"   工单编号: {gongdan.gongdan_bianhao}")
            print(f"   工单标题: {gongdan.gongdan_biaoti}")
            print(f"   服务类型: {gongdan.fuwu_leixing}")
            print(f"   工单任务数: {len(gongdan.xiangmu_list)}")
            
            print("\n   工单任务列表:")
            for idx, xiangmu in enumerate(gongdan.xiangmu_list, 1):
                print(f"   {idx}. {xiangmu.xiangmu_mingcheng}")
                print(f"      描述: {xiangmu.xiangmu_miaoshu or '无'}")
                print(f"      计划工时: {xiangmu.jihua_gongshi} 小时")
                print(f"      排序: {xiangmu.paixu}")
            
            print("\n✅ 测试通过！服务工单创建功能正常")
            
        except Exception as e:
            print(f"❌ 创建服务工单失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_service_order_creation()

