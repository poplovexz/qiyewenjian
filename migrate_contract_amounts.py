#!/usr/bin/env python3
"""
迁移脚本：为现有合同填充payment_amount字段

从合同内容中的变量值或关联的报价中提取合同金额，并更新到payment_amount字段
"""
import sys
import re
import json
sys.path.insert(0, '/var/www/packages/backend/src')

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.hetong_guanli import Hetong
from models.xiansuo_guanli import XiansuoBaojia

def extract_amount_from_content(hetong_neirong: str) -> float:
    """从合同内容中提取金额"""
    # 尝试匹配常见的金额模式
    patterns = [
        r'合同金额[：:]\s*¥?\s*([\d,]+\.?\d*)',
        r'总金额[：:]\s*¥?\s*([\d,]+\.?\d*)',
        r'服务费[：:]\s*¥?\s*([\d,]+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, hetong_neirong)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
    
    return None

def migrate_contract_amounts():
    """迁移合同金额"""
    db: Session = SessionLocal()
    
    try:
        # 查找所有payment_amount为空的合同
        contracts = db.query(Hetong).filter(
            Hetong.is_deleted == "N",
            Hetong.payment_amount.is_(None)
        ).all()
        
        print(f"📋 找到 {len(contracts)} 个需要更新的合同\n")
        
        updated_count = 0
        skipped_count = 0
        
        for hetong in contracts:
            print(f"处理合同: {hetong.hetong_bianhao}")
            
            amount = None
            source = None
            
            # 方法1: 从关联的报价获取金额
            if hetong.baojia_id:
                baojia = db.query(XiansuoBaojia).filter(
                    XiansuoBaojia.id == hetong.baojia_id
                ).first()
                
                if baojia and baojia.zongji_jine:
                    amount = float(baojia.zongji_jine)
                    source = "报价"
            
            # 方法2: 从合同内容中提取金额
            if amount is None and hetong.hetong_neirong:
                extracted_amount = extract_amount_from_content(hetong.hetong_neirong)
                if extracted_amount:
                    amount = extracted_amount
                    source = "合同内容"
            
            # 更新合同
            if amount is not None:
                hetong.payment_amount = str(amount)
                print(f"  ✅ 更新金额: ¥{amount} (来源: {source})")
                updated_count += 1
            else:
                print(f"  ⚠️  无法确定金额，跳过")
                skipped_count += 1
            
            print()
        
        # 提交更改
        if updated_count > 0:
            db.commit()
            print(f"\n✅ 成功更新 {updated_count} 个合同")
        
        if skipped_count > 0:
            print(f"⚠️  跳过 {skipped_count} 个合同（无法确定金额）")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("合同金额迁移脚本")
    print("=" * 60)
    print()
    
    response = input("是否继续执行迁移? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate_contract_amounts()
    else:
        print("已取消")

