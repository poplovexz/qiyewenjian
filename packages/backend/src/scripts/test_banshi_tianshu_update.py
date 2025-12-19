"""
测试产品步骤办事天数自动更新功能

验证：
1. 创建步骤时自动更新产品项目的办事天数
2. 更新步骤时自动更新产品项目的办事天数
3. 删除步骤时自动更新产品项目的办事天数
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinXiangmu
from services.chanpin_guanli import ChanpinBuzouService
from schemas.chanpin_guanli import ChanpinBuzouCreate, ChanpinBuzouUpdate


def print_section(title: str):
    """打印分节标题"""


async def main():
    """主测试函数"""
    # 创建数据库连接
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print_section("产品步骤办事天数自动更新测试")
        
        # 1. 查找一个测试产品
        print_section("1. 查找测试产品")
        xiangmu = db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()
        
        if not xiangmu:
            return
        
        
        # 2. 创建测试步骤
        print_section("2. 创建测试步骤")
        service = ChanpinBuzouService(db)
        
        # 创建第一个步骤：12天
        step1_data = ChanpinBuzouCreate(
            buzou_mingcheng="测试步骤1 - 国标网申请注册",
            xiangmu_id=xiangmu.id,
            yugu_shichang=Decimal("12"),
            shichang_danwei="tian",
            buzou_feiyong=Decimal("0.00"),
            paixu=0,
            shi_bixu="Y",
            zhuangtai="active"
        )
        
        step1 = await service.create_buzou(step1_data, "test_user")
        
        # 刷新产品信息
        db.refresh(xiangmu)
        
        # 创建第二个步骤：180天
        step2_data = ChanpinBuzouCreate(
            buzou_mingcheng="测试步骤2 - 领取商标注册证",
            xiangmu_id=xiangmu.id,
            yugu_shichang=Decimal("180"),
            shichang_danwei="tian",
            buzou_feiyong=Decimal("0.00"),
            paixu=1,
            shi_bixu="Y",
            zhuangtai="active"
        )
        
        step2 = await service.create_buzou(step2_data, "test_user")
        
        # 刷新产品信息
        db.refresh(xiangmu)
        
        if xiangmu.banshi_tianshu == 192:
        else:
        
        # 3. 更新步骤测试
        print_section("3. 更新步骤测试")
        
        # 将步骤1的时长从12天改为24小时（3个工作日）
        update_data = ChanpinBuzouUpdate(
            yugu_shichang=Decimal("24"),
            shichang_danwei="xiaoshi"
        )
        
        updated_step1 = await service.update_buzou(step1.id, update_data, "test_user")
        
        # 刷新产品信息
        db.refresh(xiangmu)
        
        if xiangmu.banshi_tianshu == 183:
        else:
        
        # 4. 删除步骤测试
        print_section("4. 删除步骤测试")
        
        await service.delete_buzou(step1.id, "test_user")
        
        # 刷新产品信息
        db.refresh(xiangmu)
        
        if xiangmu.banshi_tianshu == 180:
        else:
        
        # 5. 清理测试数据
        print_section("5. 清理测试数据")
        
        await service.delete_buzou(step2.id, "test_user")
        
        # 刷新产品信息
        db.refresh(xiangmu)
        
        if xiangmu.banshi_tianshu == 0:
        else:
        
        print_section("测试完成")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

