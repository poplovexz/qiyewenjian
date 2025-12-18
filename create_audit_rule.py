#!/usr/bin/env python3
"""
创建合同金额修正审核规则
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import json

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_audit_rule():
    """创建合同金额修正审核规则"""
    session = Session()
    
    try:
        # 检查是否已存在该类型的规则
        existing_rule = session.execute(
            text("""
            SELECT id FROM shenhe_guize
            WHERE guize_leixing = 'hetong_jine_xiuzheng'
            AND is_deleted = 'N'
            """)
        ).fetchone()
        
        if existing_rule:
            print(f"✅ 审核规则已存在: {existing_rule[0]}")
            return existing_rule[0]
        
        # 创建新规则
        rule_id = str(uuid.uuid4())
        now = datetime.now()
        
        # 触发条件：价格降低任何金额都触发审核
        trigger_condition = {
            "thresholds": [
                {
                    "percentage": 0,  # 任何降价都触发
                    "description": "价格降低需要审核"
                }
            ]
        }
        
        # 审核流程配置：需要管理员审核
        workflow_config = {
            "steps": [
                {
                    "step_order": 1,
                    "step_name": "管理员审核",
                    "approver_role": "admin",
                    "description": "管理员审核合同金额修正",
                    "expected_time": 24,
                    "is_required": True
                }
            ]
        }
        
        # 插入规则
        session.execute(
            text("""
            INSERT INTO shenhe_guize (
                id, guize_mingcheng, guize_leixing, guize_miaoshu,
                chufa_tiaojian, shenhe_liucheng_peizhi,
                shi_qiyong, paixu,
                created_at, updated_at, is_deleted
            ) VALUES (
                :id, :name, :type, :desc,
                :trigger, :workflow,
                :enabled, :order,
                :created_at, :updated_at, :is_deleted
            )
            """),
            {
                "id": rule_id,
                "name": "合同金额修正审核",
                "type": "hetong_jine_xiuzheng",
                "desc": "当合同金额低于报价金额时，需要进行审核",
                "trigger": json.dumps(trigger_condition),
                "workflow": json.dumps(workflow_config),
                "enabled": "Y",
                "order": 1,
                "created_at": now,
                "updated_at": now,
                "is_deleted": "N"
            }
        )
        
        session.commit()
        print(f"✅ 成功创建审核规则: {rule_id}")
        print("   规则名称: 合同金额修正审核")
        print("   规则类型: hetong_jine_xiuzheng")
        print("   触发条件: 价格降低任何金额")
        print("   审核流程: 管理员审核")
        
        return rule_id
        
    except Exception as e:
        session.rollback()
        print(f"❌ 创建审核规则失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建合同金额修正审核规则")
    print("=" * 60)
    
    rule_id = create_audit_rule()
    
    if rule_id:
        print("\n" + "=" * 60)
        print("✅ 审核规则创建成功！")
        print("=" * 60)
        print("\n现在可以测试合同生成功能：")
        print("1. 创建一个报价")
        print("2. 生成合同时，设置价格低于报价价格")
        print("3. 系统会自动触发审核流程")
        print("4. 管理员可以在'我的审核'页面看到待审核任务")
    else:
        print("\n" + "=" * 60)
        print("❌ 审核规则创建失败！")
        print("=" * 60)
        sys.exit(1)

