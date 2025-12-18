#!/usr/bin/env python3
"""
检查合同内容中的变量替换情况
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong import Hetong
from core.config import settings

def check_contracts():
    """检查最近的合同变量替换情况"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 查询最近的5个合同
        contracts = session.query(Hetong).filter(
            Hetong.is_deleted == "N"
        ).order_by(Hetong.created_at.desc()).limit(5).all()
        
        print(f"\n=== 检查最近的 {len(contracts)} 个合同 ===\n")
        
        for i, contract in enumerate(contracts, 1):
            print(f"\n【合同 {i}】")
            print(f"合同编号: {contract.hetong_bianhao}")
            print(f"合同名称: {contract.hetong_mingcheng}")
            print(f"创建时间: {contract.created_at}")
            print(f"合同状态: {contract.hetong_zhuangtai}")
            
            # 检查内容中是否有未替换的变量
            content = contract.hetong_neirong or ""
            
            # 查找所有 {{ }} 格式的变量
            import re
            variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', content)
            
            if variables:
                print(f"❌ 发现 {len(variables)} 个未替换的变量:")
                # 去重并显示
                unique_vars = list(set(variables))
                for var in unique_vars[:10]:  # 只显示前10个
                    print(f"   - {{ {var} }}")
                if len(unique_vars) > 10:
                    print(f"   ... 还有 {len(unique_vars) - 10} 个变量")
            else:
                print("✅ 所有变量已替换")
            
            # 显示内容预览
            print("\n内容预览（前200字符）:")
            print(content[:200])
            print("...\n")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_contracts()

