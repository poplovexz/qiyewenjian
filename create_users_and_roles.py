#!/usr/bin/env python3
"""
创建基础用户和角色
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from core.database import SessionLocal
from core.security import get_password_hash
from models.yonghu_guanli.jiaose import Jiaose
from models.yonghu_guanli.yonghu import Yonghu
from models.yonghu_guanli.yonghu_jiaose import YonghuJiaose
from sqlalchemy import text
import uuid
from datetime import datetime

def create_roles(session):
    """创建角色"""
    print("="*80)
    print("【步骤1】创建角色")
    print("="*80)
    
    roles_data = [
        {
            "jiaose_ming": "财务",
            "jiaose_bianma": "caiwu",
            "miaoshu": "财务人员，负责审核银行汇款凭证",
            "zhuangtai": "active"
        },
        {
            "jiaose_ming": "业务员",
            "jiaose_bianma": "yewuyuan",
            "miaoshu": "业务员，负责上传银行汇款凭证",
            "zhuangtai": "active"
        },
        {
            "jiaose_ming": "管理员",
            "jiaose_bianma": "admin",
            "miaoshu": "系统管理员",
            "zhuangtai": "active"
        }
    ]
    
    created_roles = {}
    
    for role_data in roles_data:
        # 检查角色是否已存在
        existing_role = session.query(Jiaose).filter(
            Jiaose.jiaose_bianma == role_data["jiaose_bianma"],
            Jiaose.is_deleted == "N"
        ).first()
        
        if existing_role:
            print(f"\n✅ 角色已存在: {role_data['jiaose_ming']} ({role_data['jiaose_bianma']})")
            print(f"   角色ID: {existing_role.id}")
            created_roles[role_data["jiaose_bianma"]] = existing_role.id
        else:
            role = Jiaose(
                id=str(uuid.uuid4()),
                jiaose_ming=role_data["jiaose_ming"],
                jiaose_bianma=role_data["jiaose_bianma"],
                miaoshu=role_data["miaoshu"],
                zhuangtai=role_data["zhuangtai"],
                created_by="system",
                updated_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )
            
            session.add(role)
            session.flush()
            
            print(f"\n✅ 创建角色: {role_data['jiaose_ming']} ({role_data['jiaose_bianma']})")
            print(f"   角色ID: {role.id}")
            created_roles[role_data["jiaose_bianma"]] = role.id
    
    session.commit()
    return created_roles

def create_users(session, roles):
    """创建用户"""
    print(f"\n{'='*80}")
    print("【步骤2】创建用户")
    print("="*80)
    
    users_data = [
        {
            "yonghu_ming": "caiwu001",
            "mima": "caiwu123456",
            "youxiang": "caiwu@example.com",
            "xingming": "财务张三",
            "shouji": "13800000001",
            "zhuangtai": "active",
            "role": "caiwu"
        },
        {
            "yonghu_ming": "yewu001",
            "mima": "yewu123456",
            "youxiang": "yewu@example.com",
            "xingming": "业务李四",
            "shouji": "13800000002",
            "zhuangtai": "active",
            "role": "yewuyuan"
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        # 检查用户是否已存在
        existing_user = session.query(Yonghu).filter(
            Yonghu.yonghu_ming == user_data["yonghu_ming"],
            Yonghu.is_deleted == "N"
        ).first()
        
        if existing_user:
            print(f"\n✅ 用户已存在: {user_data['xingming']} ({user_data['yonghu_ming']})")
            print(f"   用户ID: {existing_user.id}")
            created_users[user_data["role"]] = existing_user.id
        else:
            user = Yonghu(
                id=str(uuid.uuid4()),
                yonghu_ming=user_data["yonghu_ming"],
                mima=get_password_hash(user_data["mima"]),
                youxiang=user_data["youxiang"],
                xingming=user_data["xingming"],
                shouji=user_data["shouji"],
                zhuangtai=user_data["zhuangtai"],
                denglu_cishu="0",
                created_by="system",
                updated_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )
            
            session.add(user)
            session.flush()
            
            print(f"\n✅ 创建用户: {user_data['xingming']} ({user_data['yonghu_ming']})")
            print(f"   用户ID: {user.id}")
            print(f"   密码: {user_data['mima']}")
            created_users[user_data["role"]] = user.id
    
    session.commit()
    return created_users

def assign_roles(session, users, roles):
    """分配角色给用户"""
    print(f"\n{'='*80}")
    print("【步骤3】分配角色")
    print("="*80)
    
    assignments = [
        {"user_role": "caiwu", "role_code": "caiwu"},
        {"user_role": "yewuyuan", "role_code": "yewuyuan"}
    ]
    
    for assignment in assignments:
        user_id = users.get(assignment["user_role"])
        role_id = roles.get(assignment["role_code"])
        
        if not user_id or not role_id:
            print("\n❌ 跳过分配: 用户或角色不存在")
            continue
        
        # 检查是否已分配
        existing = session.query(YonghuJiaose).filter(
            YonghuJiaose.yonghu_id == user_id,
            YonghuJiaose.jiaose_id == role_id,
            YonghuJiaose.is_deleted == "N"
        ).first()
        
        if existing:
            print(f"\n✅ 角色已分配: {assignment['user_role']} -> {assignment['role_code']}")
        else:
            user_role = YonghuJiaose(
                id=str(uuid.uuid4()),
                yonghu_id=user_id,
                jiaose_id=role_id,
                created_by="system",
                updated_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )
            
            session.add(user_role)
            print(f"\n✅ 分配角色: {assignment['user_role']} -> {assignment['role_code']}")
    
    session.commit()

def update_audit_rule(session, caiwu_user_id):
    """更新审核规则，设置财务用户为审核人"""
    print(f"\n{'='*80}")
    print("【步骤4】更新审核规则")
    print("="*80)

    import json

    # 先查询当前配置
    query = text("""
        SELECT shenhe_liucheng_peizhi
        FROM shenhe_guize
        WHERE id = '6218e1e3-0c1b-459f-8cfa-e7d27a735a4c'
        AND is_deleted = 'N'
    """)

    result = session.execute(query).fetchone()
    if not result:
        print("\n❌ 未找到审核规则")
        return

    # 解析配置
    config = result[0]
    if isinstance(config, str):
        config = json.loads(config)

    # 更新审核人ID
    if 'steps' in config and len(config['steps']) > 0:
        config['steps'][0]['approver_user_id'] = caiwu_user_id

    # 更新数据库
    update_query = text("""
        UPDATE shenhe_guize
        SET shenhe_liucheng_peizhi = :config,
            updated_at = :updated_at,
            updated_by = 'system'
        WHERE id = '6218e1e3-0c1b-459f-8cfa-e7d27a735a4c'
        AND is_deleted = 'N'
    """)

    result = session.execute(
        update_query,
        {
            "config": json.dumps(config),
            "updated_at": datetime.now()
        }
    )

    session.commit()
    
    if result.rowcount > 0:
        print("\n✅ 更新审核规则成功")
        print(f"   审核人ID: {caiwu_user_id}")
        
        # 验证更新
        verify_query = text("""
            SELECT shenhe_liucheng_peizhi
            FROM shenhe_guize 
            WHERE id = '6218e1e3-0c1b-459f-8cfa-e7d27a735a4c'
        """)
        
        result = session.execute(verify_query).fetchone()
        if result:
            import json
            config = result[0]
            print("\n   更新后的配置:")
            print(f"   {json.dumps(config, ensure_ascii=False, indent=4)}")
    else:
        print("\n❌ 更新审核规则失败")

def verify_setup(session):
    """验证设置"""
    print(f"\n{'='*80}")
    print("【步骤5】验证设置")
    print("="*80)
    
    # 验证角色
    role_query = text("""
        SELECT jiaose_ming, jiaose_bianma
        FROM jiaose
        WHERE is_deleted = 'N'
        ORDER BY created_at
    """)
    
    roles = session.execute(role_query).fetchall()
    print(f"\n角色列表 (共{len(roles)}个):")
    for role in roles:
        print(f"  - {role.jiaose_ming} ({role.jiaose_bianma})")
    
    # 验证用户
    user_query = text("""
        SELECT y.yonghu_ming, y.xingming, j.jiaose_ming
        FROM yonghu y
        LEFT JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id AND yj.is_deleted = 'N'
        LEFT JOIN jiaose j ON yj.jiaose_id = j.id AND j.is_deleted = 'N'
        WHERE y.is_deleted = 'N'
        ORDER BY y.created_at
    """)
    
    users = session.execute(user_query).fetchall()
    print(f"\n用户列表 (共{len(users)}个):")
    for user in users:
        print(f"  - {user.xingming} ({user.yonghu_ming}) - 角色: {user.jiaose_ming or '未分配'}")
    
    # 验证审核规则
    rule_query = text("""
        SELECT guize_mingcheng, shenhe_liucheng_peizhi
        FROM shenhe_guize
        WHERE id = '6218e1e3-0c1b-459f-8cfa-e7d27a735a4c'
        AND is_deleted = 'N'
    """)
    
    rule = session.execute(rule_query).fetchone()
    if rule:
        import json
        config = rule.shenhe_liucheng_peizhi
        approver_id = config.get('steps', [{}])[0].get('approver_user_id')
        
        print("\n审核规则:")
        print(f"  - 规则名称: {rule.guize_mingcheng}")
        print(f"  - 审核人ID: {approver_id}")
        
        if approver_id:
            print("  ✅ 审核人已配置")
        else:
            print("  ❌ 审核人未配置")

def main():
    print("\n" + "="*80)
    print("创建基础用户和角色")
    print("="*80 + "\n")
    
    session = SessionLocal()
    
    try:
        # 步骤1：创建角色
        roles = create_roles(session)
        
        # 步骤2：创建用户
        users = create_users(session, roles)
        
        # 步骤3：分配角色
        assign_roles(session, users, roles)
        
        # 步骤4：更新审核规则
        caiwu_user_id = users.get("caiwu")
        if caiwu_user_id:
            update_audit_rule(session, caiwu_user_id)
        
        # 步骤5：验证设置
        verify_setup(session)
        
        print(f"\n{'='*80}")
        print("✅ 所有操作完成！")
        print("="*80)
        
        print("\n登录信息:")
        print("  财务用户:")
        print("    用户名: caiwu001")
        print("    密码: caiwu123456")
        print("  业务员用户:")
        print("    用户名: yewu001")
        print("    密码: yewu123456")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()

