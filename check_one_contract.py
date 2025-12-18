#!/usr/bin/env python3
"""
检查单个合同的详细内容
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong import Hetong
from core.config import settings

def check_contract(hetong_bianhao):
    """检查单个合同"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        contract = session.query(Hetong).filter(
            Hetong.hetong_bianhao == hetong_bianhao,
            Hetong.is_deleted == "N"
        ).first()
        
        if not contract:
            print(f"❌ 找不到合同: {hetong_bianhao}")
            return
        
        print("\n=== 合同详情 ===")
        print(f"合同编号: {contract.hetong_bianhao}")
        print(f"合同名称: {contract.hetong_mingcheng}")
        print(f"创建时间: {contract.created_at}")
        print(f"更新时间: {contract.updated_at}")
        
        print("\n=== 合同内容（前500字符） ===")
        print(contract.hetong_neirong[:500])
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_contract("HT202510300005")

