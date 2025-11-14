"""
插入线下支付配置示例数据（银行汇款、现金）
"""
import sys
import os
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.zhifu_guanli.zhifu_peizhi import ZhifuPeizhi


def insert_offline_payment_configs():
    """插入线下支付配置示例数据"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已存在示例数据
        existing = db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.beizhu.like('%线下支付示例%')
        ).first()
        
        if existing:
            print("⚠️  线下支付示例配置已存在，跳过插入")
            return
        
        # 1. 银行汇款配置
        yinhang_config = ZhifuPeizhi(
            id=str(uuid.uuid4()),
            peizhi_mingcheng="中国银行-对公账户",
            peizhi_leixing="yinhang",
            zhuangtai="qiyong",
            huanjing="wuxu",  # 线下支付不需要环境区分
            yinhang_mingcheng="中国银行",
            yinhang_zhanghu_mingcheng="某某科技有限公司",
            yinhang_zhanghu_haoma="6217000012345678901",
            kaihuhang_mingcheng="中国银行北京分行营业部",
            kaihuhang_lianhanghao="104100000004",
            beizhu="线下支付示例 - 银行汇款配置",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        # 2. 现金支付配置
        xianjin_config = ZhifuPeizhi(
            id=str(uuid.uuid4()),
            peizhi_mingcheng="现金支付",
            peizhi_leixing="xianjin",
            zhuangtai="qiyong",
            huanjing="wuxu",  # 线下支付不需要环境区分
            beizhu="线下支付示例 - 现金支付配置",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        # 插入数据
        db.add(yinhang_config)
        db.add(xianjin_config)
        db.commit()
        
        print("✅ 成功插入2条线下支付配置:")
        print(f"   1. {yinhang_config.peizhi_mingcheng} (ID: {yinhang_config.id})")
        print(f"   2. {xianjin_config.peizhi_mingcheng} (ID: {xianjin_config.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    insert_offline_payment_configs()

