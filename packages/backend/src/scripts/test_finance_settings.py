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
        
        # 测试收付款渠道
        result = conn.execute(text("SELECT COUNT(*) as count FROM shoufukuan_qudao WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        
        result = conn.execute(text("SELECT mingcheng, leixing FROM shoufukuan_qudao WHERE is_deleted = 'N' LIMIT 5"))
        for row in result:
        
        # 测试收入类别
        result = conn.execute(text("SELECT COUNT(*) as count FROM shouru_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        
        # 测试报销类别
        result = conn.execute(text("SELECT COUNT(*) as count FROM baoxiao_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        
        # 测试支出类别
        result = conn.execute(text("SELECT COUNT(*) as count FROM zhichu_leibie WHERE is_deleted = 'N'"))
        count = result.fetchone()[0]
        
        # 按分类统计支出类别
        result = conn.execute(text("""
            SELECT fenlei, COUNT(*) as count 
            FROM zhichu_leibie 
            WHERE is_deleted = 'N' 
            GROUP BY fenlei 
            ORDER BY count DESC
        """))
        for row in result:
        
        # 显示部分支出类别
        result = conn.execute(text("""
            SELECT fenlei, mingcheng 
            FROM zhichu_leibie 
            WHERE is_deleted = 'N' 
            ORDER BY paixu 
            LIMIT 10
        """))
        for row in result:
        

if __name__ == "__main__":
    test_finance_settings()

