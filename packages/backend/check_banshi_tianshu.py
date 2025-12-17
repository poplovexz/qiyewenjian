#!/usr/bin/env python
"""检查产品办事天数数据"""
import sys
sys.path.insert(0, '/var/www/packages/backend/src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinXiangmu, ChanpinBuzou

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 查询几个产品及其步骤
    xiangmu_list = db.query(ChanpinXiangmu).filter(
        ChanpinXiangmu.is_deleted == 'N',
        ChanpinXiangmu.chanpin_leixing == 'zengzhi'
    ).limit(10).all()
    
    print('=' * 80)
    print('产品及其步骤信息')
    print('=' * 80)
    
    for xiangmu in xiangmu_list:
        print(f'\n产品: {xiangmu.xiangmu_mingcheng}')
        print(f'  ID: {xiangmu.id}')
        print(f'  当前办事天数: {xiangmu.banshi_tianshu} 天')
        
        # 查询该产品的步骤
        buzou_list = db.query(ChanpinBuzou).filter(
            ChanpinBuzou.xiangmu_id == xiangmu.id,
            ChanpinBuzou.is_deleted == 'N'
        ).all()
        
        print(f'  步骤数量: {len(buzou_list)}')
        
        if buzou_list:
            total_days = 0
            for buzou in buzou_list:
                # 转换为天数
                unit_map = {'tian': 1.0, 'xiaoshi': 1.0/8.0, 'fenzhong': 1.0/480.0}
                days = float(buzou.yugu_shichang) * unit_map.get(buzou.shichang_danwei, 1.0)
                total_days += days
                print(f'    - {buzou.buzou_mingcheng}: {buzou.yugu_shichang} {buzou.shichang_danwei} = {days:.2f} 天')
            
            import math
            expected_days = math.ceil(total_days)
            print(f'  计算的总天数: {total_days:.2f} 天 (向上取整: {expected_days} 天)')
            
            if xiangmu.banshi_tianshu != expected_days:
                print(f'  ⚠️  数据不一致！数据库中是 {xiangmu.banshi_tianshu} 天，应该是 {expected_days} 天')
            else:
                print(f'  ✅ 数据一致')
        else:
            print(f'  ⚠️  没有步骤数据')
            if xiangmu.banshi_tianshu != 0:
                print(f'  ⚠️  数据不一致！没有步骤但办事天数是 {xiangmu.banshi_tianshu} 天')
    
finally:
    db.close()

