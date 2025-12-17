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
        
        print("开始创建办公管理数据表...")
        
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            BaoxiaoShenqing.__table__,
            QingjiaShenqing.__table__,
            DuiwaiFukuanShenqing.__table__,
            CaigouShenqing.__table__,
            GongzuoJiaojie.__table__
        ])
        
        print("✅ 办公管理数据表创建成功！")
        print("创建的表包括：")
        print("- baoxiao_shenqing (报销申请表)")
        print("- qingjia_shenqing (请假申请表)")
        print("- duiwai_fukuan_shenqing (对外付款申请表)")
        print("- caigou_shenqing (采购申请表)")
        print("- gongzuo_jiaojie (工作交接单表)")
        
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    print("=" * 50)
    print("办公管理模块 - 数据库初始化")
    print("=" * 50)
    
    create_tables()
    
    print("=" * 50)
    print("✓ 办公管理模块数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()

