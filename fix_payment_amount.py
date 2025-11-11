#!/usr/bin/env python3
"""
修复合同的payment_amount字段
从报价中获取金额，如果没有报价则设置默认值
"""

import sys
sys.path.insert(0, '/var/www/packages/backend/src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong import Hetong
from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
from datetime import datetime

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def fix_payment_amounts():
    """修复所有合同的payment_amount"""
    db = SessionLocal()
    
    try:
        # 获取所有没有payment_amount的合同
        contracts = db.query(Hetong).filter(
            Hetong.is_deleted == "N",
            (Hetong.payment_amount == None) | (Hetong.payment_amount == "")
        ).all()
        
        print(f"找到 {len(contracts)} 个需要修复的合同")
        
        for contract in contracts:
            print(f"\n处理合同: {contract.hetong_bianhao}")
            
            # 尝试从报价获取金额
            if contract.baojia_id:
                baojia = db.query(XiansuoBaojia).filter(
                    XiansuoBaojia.id == contract.baojia_id
                ).first()
                
                if baojia:
                    # 检查报价表的字段
                    amount = None
                    if hasattr(baojia, 'baojia_jine'):
                        amount = baojia.baojia_jine
                    elif hasattr(baojia, 'jine'):
                        amount = baojia.jine
                    elif hasattr(baojia, 'zong_jine'):
                        amount = baojia.zong_jine
                    
                    if amount:
                        contract.payment_amount = str(amount)
                        print(f"  从报价获取金额: {amount}")
                    else:
                        # 设置默认金额
                        contract.payment_amount = "5000.00"
                        print(f"  报价无金额，设置默认值: 5000.00")
                else:
                    # 设置默认金额
                    contract.payment_amount = "5000.00"
                    print(f"  报价不存在，设置默认值: 5000.00")
            else:
                # 设置默认金额
                contract.payment_amount = "5000.00"
                print(f"  无报价ID，设置默认值: 5000.00")
            
            contract.updated_at = datetime.now()
        
        # 提交更改
        db.commit()
        print(f"\n✅ 成功修复 {len(contracts)} 个合同的payment_amount字段")
        
        # 显示修复后的结果
        print("\n修复后的合同列表:")
        for contract in contracts:
            print(f"  {contract.hetong_bianhao}: ¥{contract.payment_amount}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("修复合同payment_amount字段")
    print("=" * 60)
    fix_payment_amounts()

