#!/usr/bin/env python3
"""
创建审核工作流相关数据库表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.config import settings
from models import Base
from models.shenhe_guanli import ShenheGuize, ShenheLiucheng, ShenheJilu
from models.zhifu_guanli import HetongZhifu, YinhangHuikuanDanju
from models.hetong_guanli import HetongJineBiangeng


def create_tables():
    """创建审核工作流相关表"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.DATABASE_URL)
        
        
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            ShenheGuize.__table__,
            ShenheLiucheng.__table__,
            ShenheJilu.__table__,
            HetongZhifu.__table__,
            YinhangHuikuanDanju.__table__,
            HetongJineBiangeng.__table__
        ])
        
        
    except Exception as e:
        sys.exit(1)


def init_default_audit_rules():
    """初始化默认审核规则"""
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    import json
    import uuid
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        
        # 合同金额修正审核规则
        hetong_rule = ShenheGuize(
            id=str(uuid.uuid4()),
            guize_mingcheng="合同金额修正审核规则",
            guize_leixing="hetong_jine_xiuzheng",
            chufa_tiaojian=json.dumps({
                "type": "amount_decrease",
                "thresholds": [
                    {"percentage": 10, "approver_level": "supervisor"},
                    {"percentage": 20, "approver_level": "manager"},
                    {"percentage": 30, "approver_level": "director"}
                ]
            }),
            shenhe_liucheng_peizhi=json.dumps({
                "steps": [
                    {"step": 1, "name": "主管审核", "role": "supervisor"},
                    {"step": 2, "name": "经理审核", "role": "manager", "condition": "percentage >= 20"},
                    {"step": 3, "name": "总监审核", "role": "director", "condition": "percentage >= 30"}
                ]
            }),
            shi_qiyong="Y",
            paixu=1,
            guize_miaoshu="当合同金额被修改降低时触发的审核规则",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        # 报价审核规则
        baojia_rule = ShenheGuize(
            id=str(uuid.uuid4()),
            guize_mingcheng="报价审核规则",
            guize_leixing="baojia_shenhe",
            chufa_tiaojian=json.dumps({
                "type": "quote_approval",
                "thresholds": [
                    {"amount": 10000, "approver_level": "supervisor"},
                    {"amount": 50000, "approver_level": "manager"},
                    {"amount": 100000, "approver_level": "director"}
                ]
            }),
            shenhe_liucheng_peizhi=json.dumps({
                "steps": [
                    {"step": 1, "name": "主管审核", "role": "supervisor"},
                    {"step": 2, "name": "经理审核", "role": "manager", "condition": "amount >= 50000"},
                    {"step": 3, "name": "总监审核", "role": "director", "condition": "amount >= 100000"}
                ]
            }),
            shi_qiyong="Y",
            paixu=2,
            guize_miaoshu="报价金额超过阈值时触发的审核规则",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        db.add(hetong_rule)
        db.add(baojia_rule)
        db.commit()
        
        
    except Exception as e:
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    init_default_audit_rules()
