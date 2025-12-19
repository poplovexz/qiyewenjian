"""
一次性脚本：更新所有产品的办事天数
"""
import asyncio
import math
from decimal import Decimal
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinXiangmu, ChanpinBuzou


def convert_to_days(time: Decimal, unit: str) -> float:
    """将时间转换为天数"""
    unit_map = {
        'tian': 1.0,           # 天 -> 天
        'xiaoshi': 1.0/8.0,    # 小时 -> 天（按8小时工作日）
        'fenzhong': 1.0/480.0  # 分钟 -> 天（480分钟 = 8小时 = 1天）
    }
    return float(time) * unit_map.get(unit, 1.0)


async def main():
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        
        # 获取所有未删除的产品
        xiangmu_list = db.query(ChanpinXiangmu).filter(
            ChanpinXiangmu.is_deleted == 'N'
        ).all()
        
        
        updated_count = 0
        unchanged_count = 0
        
        for xiangmu in xiangmu_list:
            # 获取该产品的所有步骤
            buzou_list = db.query(ChanpinBuzou).filter(
                and_(
                    ChanpinBuzou.xiangmu_id == xiangmu.id,
                    ChanpinBuzou.is_deleted == "N"
                )
            ).all()
            
            # 计算总天数
            total_days = 0.0
            for buzou in buzou_list:
                days = convert_to_days(buzou.yugu_shichang, buzou.shichang_danwei)
                total_days += days
            
            # 向上取整
            total_days_int = math.ceil(total_days)
            
            # 检查是否需要更新
            if xiangmu.banshi_tianshu != total_days_int:
                old_value = xiangmu.banshi_tianshu
                xiangmu.banshi_tianshu = total_days_int
                updated_count += 1
            else:
                unchanged_count += 1
        
        # 提交所有更改
        db.commit()
        
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(main())

