#!/usr/bin/env python3
"""
更新线索报价表结构 - 添加报价确认相关字段
用于阶段1：报价确认与线索联动功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import SessionLocal


def update_xiansuo_baojia_table():
    """更新线索报价表结构，添加确认相关字段"""
    db: Session = SessionLocal()
    
    try:
        
        # 添加报价确认相关字段
        alter_statements = [
            # 添加确认人ID字段
            "ALTER TABLE xiansuo_baojia ADD COLUMN IF NOT EXISTS queren_ren_id VARCHAR(36)",
            
            # 添加确认时间字段  
            "ALTER TABLE xiansuo_baojia ADD COLUMN IF NOT EXISTS queren_shijian TIMESTAMP",
            
            # 添加字段注释
            "COMMENT ON COLUMN xiansuo_baojia.queren_ren_id IS '确认人ID（外键关联用户表）'",
            "COMMENT ON COLUMN xiansuo_baojia.queren_shijian IS '确认时间（报价被确认或拒绝的时间戳）'",
            
            # 确保现有状态字段有正确的注释
            "COMMENT ON COLUMN xiansuo_baojia.baojia_zhuangtai IS '报价状态：draft(草稿)、sent(已发送)、accepted(已确认)、rejected(已拒绝)、expired(已过期)'"
        ]
        
        for i, statement in enumerate(alter_statements, 1):
            try:
                db.execute(text(statement))
            except Exception as e:
                # 某些操作可能会失败（比如字段已存在），这是正常的
        
        # 提交更改
        db.commit()
        
        # 验证表结构
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'xiansuo_baojia'
            AND column_name IN ('queren_ren_id', 'queren_shijian', 'baojia_zhuangtai')
            ORDER BY ordinal_position
        """))
        
        for row in result:
            nullable = "可空" if row[2] == "YES" else "非空"
            default = f"默认值: {row[3]}" if row[3] else "无默认值"
        
        # 检查现有数据
        count_result = db.execute(text("SELECT COUNT(*) FROM xiansuo_baojia"))
        total_count = count_result.scalar()
        
        confirmed_result = db.execute(text("""
            SELECT COUNT(*) FROM xiansuo_baojia 
            WHERE baojia_zhuangtai IN ('accepted', 'rejected')
        """))
        confirmed_count = confirmed_result.scalar()
        
        
        return True
        
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def verify_table_structure():
    """验证表结构是否正确更新"""
    db: Session = SessionLocal()
    
    try:
        
        # 检查必需字段是否存在
        required_columns = ['queren_ren_id', 'queren_shijian']
        
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'xiansuo_baojia'
            AND column_name IN ('queren_ren_id', 'queren_shijian')
        """))
        
        existing_columns = [row[0] for row in result]
        
        for col in required_columns:
            if col in existing_columns:
            else:
                return False
        
        return True
        
    except Exception as e:
        return False
    finally:
        db.close()


def main():
    """主函数"""
    
    # 步骤1：更新表结构
    if not update_xiansuo_baojia_table():
        return False
    
    # 步骤2：验证表结构
    if not verify_table_structure():
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
