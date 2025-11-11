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
        print('=' * 80)
        print('  更新所有产品的办事天数')
        print('=' * 80)
        
        # 获取所有未删除的产品
        xiangmu_list = db.query(ChanpinXiangmu).filter(
            ChanpinXiangmu.is_deleted == 'N'
        ).all()
        
        print(f'\n找到 {len(xiangmu_list)} 个产品需要更新')
        
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
                print(f'  ✅ 更新: {xiangmu.xiangmu_mingcheng}')
                print(f'     {old_value} 天 → {total_days_int} 天 (步骤数: {len(buzou_list)})')
            else:
                unchanged_count += 1
        
        # 提交所有更改
        db.commit()
        
        print('\n' + '=' * 80)
        print('  更新完成')
        print('=' * 80)
        print(f'  ✅ 已更新: {updated_count} 个产品')
        print(f'  ⏭️  未变化: {unchanged_count} 个产品')
        print(f'  📊 总计: {len(xiangmu_list)} 个产品')
        print('=' * 80)
        
    except Exception as e:
        print(f'\n❌ 更新过程中发生错误: {str(e)}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(main())

