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
        print("开始更新线索报价表结构...")
        print("=" * 50)
        
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
        
        print("执行数据库变更语句：")
        for i, statement in enumerate(alter_statements, 1):
            try:
                print(f"{i}. {statement}")
                db.execute(text(statement))
                print("   ✅ 执行成功")
            except Exception as e:
                # 某些操作可能会失败（比如字段已存在），这是正常的
                print(f"   ⚠️  执行跳过: {str(e)}")
        
        # 提交更改
        db.commit()
        print("\n" + "=" * 50)
        print("✅ 线索报价表结构更新完成!")
        
        # 验证表结构
        print("\n📋 验证更新后的表结构:")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'xiansuo_baojia'
            AND column_name IN ('queren_ren_id', 'queren_shijian', 'baojia_zhuangtai')
            ORDER BY ordinal_position
        """))
        
        print("关键字段信息：")
        for row in result:
            nullable = "可空" if row[2] == "YES" else "非空"
            default = f"默认值: {row[3]}" if row[3] else "无默认值"
            print(f"  📌 {row[0]}: {row[1]} ({nullable}, {default})")
        
        # 检查现有数据
        count_result = db.execute(text("SELECT COUNT(*) FROM xiansuo_baojia"))
        total_count = count_result.scalar()
        
        confirmed_result = db.execute(text("""
            SELECT COUNT(*) FROM xiansuo_baojia 
            WHERE baojia_zhuangtai IN ('accepted', 'rejected')
        """))
        confirmed_count = confirmed_result.scalar()
        
        print("\n📊 数据统计:")
        print(f"  总报价数量: {total_count}")
        print(f"  已确认/拒绝报价数量: {confirmed_count}")
        print(f"  待确认报价数量: {total_count - confirmed_count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 更新表结构时发生错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_table_structure():
    """验证表结构是否正确更新"""
    db: Session = SessionLocal()
    
    try:
        print("\n🔍 验证表结构完整性...")
        
        # 检查必需字段是否存在
        required_columns = ['queren_ren_id', 'queren_shijian']
        
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'xiansuo_baojia'
            AND column_name IN ('queren_ren_id', 'queren_shijian')
        """))
        
        existing_columns = [row[0] for row in result]
        
        print("字段检查结果：")
        for col in required_columns:
            if col in existing_columns:
                print(f"  ✅ {col}: 存在")
            else:
                print(f"  ❌ {col}: 缺失")
                return False
        
        print("✅ 表结构验证通过！")
        return True
        
    except Exception as e:
        print(f"❌ 验证表结构时发生错误: {e}")
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("线索报价表结构更新脚本")
    print("阶段1：报价确认与线索联动功能")
    print("=" * 60)
    
    # 步骤1：更新表结构
    if not update_xiansuo_baojia_table():
        print("❌ 表结构更新失败，退出脚本")
        return False
    
    # 步骤2：验证表结构
    if not verify_table_structure():
        print("❌ 表结构验证失败，退出脚本")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 线索报价表结构更新完成！")
    print("✅ 新增字段：queren_ren_id, queren_shijian")
    print("✅ 支持报价确认功能开发")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
