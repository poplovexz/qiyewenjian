"""
测试财务设置API
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from core.config import settings

def test_finance_settings():
    """测试财务设置数据"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        print("=" * 60)
        print("财务设置数据测试")
        print("=" * 60)
        
        # 测试收付款渠道
        print("\n1. 收付款渠道:")
        result = conn.execute(text("SELECT COUNT(*) as count FROM shoufukuan_qudao WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        print(f"   总数: {count}")
        
        result = conn.execute(text("SELECT mingcheng, leixing FROM shoufukuan_qudao WHERE is_deleted = 'N' LIMIT 5"))
        for row in result:
            print(f"   - {row[0]} ({row[1]})")
        
        # 测试收入类别
        print("\n2. 收入类别:")
        result = conn.execute(text("SELECT COUNT(*) as count FROM shouru_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        print(f"   总数: {count}")
        
        # 测试报销类别
        print("\n3. 报销类别:")
        result = conn.execute(text("SELECT COUNT(*) as count FROM baoxiao_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        print(f"   总数: {count}")
        
        # 测试支出类别
        print("\n4. 支出类别:")
        result = conn.execute(text("SELECT COUNT(*) as count FROM zhichu_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        print(f"   总数: {count}")
        
        # 按分类统计支出类别
        print("\n   按分类统计:")
        result = conn.execute(text("""
            SELECT fenlei, COUNT(*) as count 
            FROM zhichu_leibie 
            WHERE is_deleted = 'N' 
            GROUP BY fenlei 
            ORDER BY count DESC
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]} 项")
        
        # 显示部分支出类别
        print("\n   部分支出类别:")
        result = conn.execute(text("""
            SELECT fenlei, mingcheng 
            FROM zhichu_leibie 
            WHERE is_deleted = 'N' 
            ORDER BY paixu 
            LIMIT 10
        """))
        for row in result:
            print(f"   - {row[0]} > {row[1]}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

if __name__ == "__main__":
    test_finance_settings()

