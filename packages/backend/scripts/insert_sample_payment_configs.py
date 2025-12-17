#!/usr/bin/env python3
"""
插入示例支付配置数据（使用正确的加密）
执行时间: 2025-01-14
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from core.config import settings
from core.security.encryption import AESEncryption
from models.zhifu_guanli.zhifu_peizhi import ZhifuPeizhi

# 创建数据库连接
database_url = str(settings.DATABASE_URL)
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建加密工具
encryption = AESEncryption()

def insert_sample_configs():
    """插入示例支付配置"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在示例数据
        existing = db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.beizhu.like('%测试用的%')
        ).first()
        
        if existing:
            print("⚠️  示例数据已存在，跳过插入")
            return
        
        # 1. 微信支付配置
        weixin_config = ZhifuPeizhi(
            id=str(uuid.uuid4()),
            peizhi_mingcheng="微信支付-测试环境",
            peizhi_leixing="weixin",
            zhuangtai="qiyong",
            huanjing="shachang",
            weixin_appid=encryption.encrypt("wx1234567890abcdef"),
            weixin_shanghu_hao=encryption.encrypt("1234567890"),
            weixin_shanghu_siyao=encryption.encrypt("示例密钥-请替换为真实密钥"),
            weixin_zhengshu_xuliehao=encryption.encrypt("1234567890ABCDEF"),
            weixin_api_v3_miyao=encryption.encrypt("示例APIv3密钥-请替换为真实密钥"),
            tongzhi_url="http://localhost:8000/api/v1/public/payment-callback/weixin/notify",
            beizhu="这是测试用的微信支付配置，请在生产环境中替换为真实配置",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N",
            remark="测试配置"
        )
        
        # 2. 支付宝配置
        zhifubao_config = ZhifuPeizhi(
            id=str(uuid.uuid4()),
            peizhi_mingcheng="支付宝-测试环境",
            peizhi_leixing="zhifubao",
            zhuangtai="qiyong",
            huanjing="shachang",
            zhifubao_appid=encryption.encrypt("2021001234567890"),
            zhifubao_shanghu_siyao=encryption.encrypt("示例私钥-请替换为真实私钥"),
            zhifubao_zhifubao_gongyao=encryption.encrypt("示例公钥-请替换为真实公钥"),
            tongzhi_url="http://localhost:8000/api/v1/public/payment-callback/zhifubao/notify",
            beizhu="这是测试用的支付宝配置，请在生产环境中替换为真实配置",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N",
            remark="测试配置"
        )
        
        # 插入数据
        db.add(weixin_config)
        db.add(zhifubao_config)
        db.commit()
        
        print("✅ 成功插入2条示例支付配置:")
        print(f"   1. {weixin_config.peizhi_mingcheng} (ID: {weixin_config.id})")
        print(f"   2. {zhifubao_config.peizhi_mingcheng} (ID: {zhifubao_config.id})")
        print("\n⚠️  注意：这些是示例数据，仅用于测试界面功能")
        print("   实际使用时请在支付配置管理页面创建真实配置")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_configs()

