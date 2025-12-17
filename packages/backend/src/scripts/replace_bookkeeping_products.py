#!/usr/bin/env python3
"""
替换代理记账产品数据脚本
根据图片中的真实数据替换现有的测试数据
"""
import sys
sys.path.insert(0, 'src')

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli.chanpin_xiangmu import ChanpinXiangmu
from models.chanpin_guanli.chanpin_fenlei import ChanpinFenlei
from decimal import Decimal

# 真实的代理记账产品数据（从用户提供的截图中提取）
REAL_PRODUCTS = [
    # 第一张图片的产品
    {"name": "税金计提、核算", "price": 200.00, "days": 0, "unit": "元 / 次"},
    {"name": "往来款项核算", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "收入、成本、费用核算", "price": 300.00, "days": 0, "unit": "元 / 月"},
    {"name": "账套数据迁移", "price": 1000.00, "days": 0, "unit": "元 / 次"},
    {"name": "企业账套建立", "price": 1000.00, "days": 0, "unit": "元 / 次"},
    {"name": "新设企业税务登记", "price": 1000.00, "days": 0, "unit": "元 / 次"},
    {"name": "社保/公积金减", "price": 29.00, "days": 0, "unit": "元 / 次"},
    {"name": "代开发票", "price": 19.00, "days": 0, "unit": "元 / 张"},

    # 第二张图片的产品
    {"name": "财务凭证装订及保管", "price": 100.00, "days": 0, "unit": "元 / 次"},
    {"name": "季度明细账核对", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "应收应付往来账目核对", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "月度报表出具", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "涉税事项税务网厅操作", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "纳税申报、税款缴纳", "price": 300.00, "days": 0, "unit": "元 / 月"},
    {"name": "社保、公积金计提、核算", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "员工工资介预核算", "price": 300.00, "days": 0, "unit": "元 / 月"},

    # 第三张图片的产品
    {"name": "税款缴纳/退税申请", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "申报所得税汇算清缴", "price": 500.00, "days": 0, "unit": "元 / 次"},
    {"name": "年度申报工商公示", "price": 200.00, "days": 0, "unit": "元 / 次"},
    {"name": "网厅审请增加授信额度", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "开票托管年12个账", "price": 1200.00, "days": 0, "unit": "元 / 年"},
    {"name": "财税咨询保达风险管理", "price": 1000.00, "days": 0, "unit": "元 / 次"},
    {"name": "财税知识普及", "price": 300.00, "days": 0, "unit": "元 / 次"},
    {"name": "指导协助企业办理日常涉税", "price": 300.00, "days": 0, "unit": "元 / 次"},
]

def main():
    engine = create_engine(str(settings.DATABASE_URL))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print('=' * 80)
        print('代理记账产品数据替换脚本')
        print('=' * 80)
        
        # 1. 查找代理记账分类
        daili_fenlei = db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.chanpin_leixing == 'daili_jizhang',
                ChanpinFenlei.is_deleted == 'N'
            )
        ).first()
        
        if not daili_fenlei:
            print('❌ 未找到代理记账分类')
            return
        
        print(f'\n✅ 找到代理记账分类: {daili_fenlei.fenlei_mingcheng} (ID: {daili_fenlei.id})')
        
        # 2. 删除现有的代理记账产品（软删除）
        existing_products = db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.fenlei_id == daili_fenlei.id,
                ChanpinXiangmu.is_deleted == 'N'
            )
        ).all()
        
        print(f'\n📋 找到 {len(existing_products)} 个现有产品，准备删除...')
        for product in existing_products:
            product.is_deleted = 'Y'
            print(f'  - 删除: {product.xiangmu_mingcheng}')
        
        db.commit()
        print('✅ 现有产品已删除')
        
        # 3. 创建真实的产品数据
        print(f'\n📝 创建 {len(REAL_PRODUCTS)} 个真实产品...')
        for idx, product_data in enumerate(REAL_PRODUCTS, 1):
            # 提取单位（如果有的话）
            unit = product_data.get('unit', 'yuan')
            # 从单位中提取报价单位（去掉"元 / "前缀）
            if '/' in unit:
                baojia_danwei = unit.split('/')[-1].strip()
            else:
                baojia_danwei = 'yuan'

            product = ChanpinXiangmu(
                xiangmu_mingcheng=product_data['name'],
                xiangmu_bianma=f'daili_jizhang_{idx}',
                fenlei_id=daili_fenlei.id,
                yewu_baojia=Decimal(str(product_data['price'])),
                baojia_danwei=baojia_danwei,
                banshi_tianshu=product_data['days'],
                xiangmu_beizhu='',
                paixu=idx,
                zhuangtai='active',
                created_by='system'
            )
            db.add(product)
            print(f'  {idx}. {product_data["name"]} - {product_data["price"]} {unit}')

        db.commit()
        print('\n✅ 真实产品数据创建完成！')
        
        # 4. 验证
        new_products = db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.fenlei_id == daili_fenlei.id,
                ChanpinXiangmu.is_deleted == 'N'
            )
        ).all()
        
        print(f'\n📊 验证: 现在有 {len(new_products)} 个代理记账产品')
        print('=' * 80)
        
    except Exception as e:
        print(f'\n❌ 错误: {str(e)}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()

