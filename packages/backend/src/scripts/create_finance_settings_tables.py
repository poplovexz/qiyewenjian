"""
创建财务设置相关表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from core.config import settings

def create_finance_settings_tables():
    """创建财务设置相关表"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        # 创建收付款渠道表
        print("创建收付款渠道表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS shoufukuan_qudao (
                id VARCHAR(36) PRIMARY KEY,
                mingcheng VARCHAR(100) NOT NULL,
                leixing VARCHAR(50) NOT NULL,
                zhanghu_mingcheng VARCHAR(200),
                zhanghu_haoma VARCHAR(100),
                kaihuhang VARCHAR(200),
                lianhanghao VARCHAR(50),
                miaoshu TEXT,
                paixu INT DEFAULT 0,
                zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
                created_by VARCHAR(36),
                updated_by VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted VARCHAR(1) DEFAULT 'N'
            );
            CREATE INDEX IF NOT EXISTS idx_qudao_leixing ON shoufukuan_qudao(leixing);
            CREATE INDEX IF NOT EXISTS idx_qudao_zhuangtai ON shoufukuan_qudao(zhuangtai);
            CREATE INDEX IF NOT EXISTS idx_qudao_created_at ON shoufukuan_qudao(created_at);
        """))
        conn.commit()
        print("收付款渠道表创建成功")
        
        # 创建收入类别表
        print("创建收入类别表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS shouru_leibie (
                id VARCHAR(36) PRIMARY KEY,
                mingcheng VARCHAR(100) NOT NULL,
                bianma VARCHAR(50) UNIQUE,
                miaoshu TEXT,
                paixu INT DEFAULT 0,
                zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
                created_by VARCHAR(36),
                updated_by VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted VARCHAR(1) DEFAULT 'N'
            );
            CREATE INDEX IF NOT EXISTS idx_shouru_zhuangtai ON shouru_leibie(zhuangtai);
            CREATE INDEX IF NOT EXISTS idx_shouru_created_at ON shouru_leibie(created_at);
        """))
        conn.commit()
        print("收入类别表创建成功")
        
        # 创建报销类别表
        print("创建报销类别表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS baoxiao_leibie (
                id VARCHAR(36) PRIMARY KEY,
                mingcheng VARCHAR(100) NOT NULL,
                bianma VARCHAR(50) UNIQUE,
                miaoshu TEXT,
                paixu INT DEFAULT 0,
                zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
                created_by VARCHAR(36),
                updated_by VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted VARCHAR(1) DEFAULT 'N'
            );
            CREATE INDEX IF NOT EXISTS idx_baoxiao_zhuangtai ON baoxiao_leibie(zhuangtai);
            CREATE INDEX IF NOT EXISTS idx_baoxiao_created_at ON baoxiao_leibie(created_at);
        """))
        conn.commit()
        print("报销类别表创建成功")
        
        # 创建支出类别表
        print("创建支出类别表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS zhichu_leibie (
                id VARCHAR(36) PRIMARY KEY,
                mingcheng VARCHAR(100) NOT NULL,
                bianma VARCHAR(50) UNIQUE,
                fenlei VARCHAR(100),
                miaoshu TEXT,
                paixu INT DEFAULT 0,
                zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
                created_by VARCHAR(36),
                updated_by VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted VARCHAR(1) DEFAULT 'N'
            );
            CREATE INDEX IF NOT EXISTS idx_zhichu_fenlei ON zhichu_leibie(fenlei);
            CREATE INDEX IF NOT EXISTS idx_zhichu_zhuangtai ON zhichu_leibie(zhuangtai);
            CREATE INDEX IF NOT EXISTS idx_zhichu_created_at ON zhichu_leibie(created_at);
        """))
        conn.commit()
        print("支出类别表创建成功")
        
    print("\n所有财务设置表创建完成！")

if __name__ == "__main__":
    create_finance_settings_tables()

