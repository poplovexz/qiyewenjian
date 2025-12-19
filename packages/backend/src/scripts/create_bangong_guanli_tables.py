#!/usr/bin/env python3
"""
创建办公管理模块数据表
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from core.config import settings
from models.base import Base
from models.bangong_guanli import (
    BaoxiaoShenqing,
    QingjiaShenqing,
    DuiwaiFukuanShenqing,
    CaigouShenqing,
    GongzuoJiaojie
)

def create_tables():
    """创建办公管理相关数据表"""
    try:
        # 创建数据库引擎
        engine = create_engine(str(settings.DATABASE_URL))
        
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            BaoxiaoShenqing.__table__,
            QingjiaShenqing.__table__,
            DuiwaiFukuanShenqing.__table__,
            CaigouShenqing.__table__,
            GongzuoJiaojie.__table__
        ])
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """主函数"""
    
    create_tables()
    
if __name__ == "__main__":
    main()
