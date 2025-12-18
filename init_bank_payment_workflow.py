#!/usr/bin/env python3
"""
初始化银行转账支付审批流程
1. 创建角色（业务员、财务）
2. 创建用户
3. 创建审批流程配置
"""

import sys
import uuid
sys.path.insert(0, '/var/www/packages/backend/src')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_roles(db):
    """创建角色"""
    print("\n" + "="*60)
    print("1. 创建角色")
    print("="*60)
    
    roles = [
        {
            'id': str(uuid.uuid4()),
            'jiaose_mingcheng': '业务员',
            'jiaose_miaoshu': '负责客户对接和汇款单据上传',
            'jiaose_daima': 'salesperson',
            'zhuangtai': 'active'
        },
        {
            'id': str(uuid.uuid4()),
            'jiaose_mingcheng': '财务',
            'jiaose_miaoshu': '负责审核汇款单据和确认到账',
            'jiaose_daima': 'finance',
            'zhuangtai': 'active'
        }
    ]
    
    for role in roles:
        # 检查角色是否已存在
        result = db.execute(
            text("SELECT id FROM jiaose WHERE jiaose_daima = :code AND is_deleted = 'N'"),
            {'code': role['jiaose_daima']}
        ).fetchone()
        
        if result:
            print(f"  ✓ 角色已存在: {role['jiaose_mingcheng']} ({role['jiaose_daima']})")
            role['id'] = result[0]
        else:
            db.execute(
                text("""
                    INSERT INTO jiaose (id, jiaose_mingcheng, jiaose_miaoshu, jiaose_daima, zhuangtai, 
                                       created_at, updated_at, is_deleted)
                    VALUES (:id, :name, :desc, :code, :status, NOW(), NOW(), 'N')
                """),
                {
                    'id': role['id'],
                    'name': role['jiaose_mingcheng'],
                    'desc': role['jiaose_miaoshu'],
                    'code': role['jiaose_daima'],
                    'status': role['zhuangtai']
                }
            )
            print(f"  ✓ 创建角色: {role['jiaose_mingcheng']} ({role['jiaose_daima']})")
    
    db.commit()
    return roles

def create_users(db, roles):
    """创建测试用户"""
    print("\n" + "="*60)
    print("2. 创建测试用户")
    print("="*60)
    
    # 获取角色ID (PTC-W0063: 使用 next() 的默认值防止 StopIteration)
    salesperson_role = next((r for r in roles if r['jiaose_daima'] == 'salesperson'), None)
    finance_role = next((r for r in roles if r['jiaose_daima'] == 'finance'), None)

    if not salesperson_role or not finance_role:
        raise ValueError("缺少必要的角色: salesperson 或 finance")
    
    users = [
        {
            'id': str(uuid.uuid4()),
            'yonghu_ming': 'salesperson1',
            'mima': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7K6W',  # password: 123456
            'xingming': '张业务',
            'youxiang': 'salesperson1@example.com',
            'shouji': '13800138001',
            'zhuangtai': 'active',
            'role_id': salesperson_role['id']
        },
        {
            'id': str(uuid.uuid4()),
            'yonghu_ming': 'finance1',
            'mima': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7K6W',  # password: 123456
            'xingming': '李财务',
            'youxiang': 'finance1@example.com',
            'shouji': '13800138002',
            'zhuangtai': 'active',
            'role_id': finance_role['id']
        }
    ]
    
    for user in users:
        # 检查用户是否已存在
        result = db.execute(
            text("SELECT id FROM yonghu WHERE yonghu_ming = :username AND is_deleted = 'N'"),
            {'username': user['yonghu_ming']}
        ).fetchone()
        
        if result:
            print(f"  ✓ 用户已存在: {user['xingming']} ({user['yonghu_ming']})")
            user['id'] = result[0]
        else:
            db.execute(
                text("""
                    INSERT INTO yonghu (id, yonghu_ming, mima, xingming, youxiang, shouji, zhuangtai,
                                       created_at, updated_at, is_deleted)
                    VALUES (:id, :username, :password, :name, :email, :phone, :status, NOW(), NOW(), 'N')
                """),
                {
                    'id': user['id'],
                    'username': user['yonghu_ming'],
                    'password': user['mima'],
                    'name': user['xingming'],
                    'email': user['youxiang'],
                    'phone': user['shouji'],
                    'status': user['zhuangtai']
                }
            )
            
            # 分配角色
            db.execute(
                text("""
                    INSERT INTO yonghu_jiaose (id, yonghu_id, jiaose_id, created_at, updated_at, is_deleted)
                    VALUES (:id, :user_id, :role_id, NOW(), NOW(), 'N')
                """),
                {
                    'id': str(uuid.uuid4()),
                    'user_id': user['id'],
                    'role_id': user['role_id']
                }
            )
            print(f"  ✓ 创建用户: {user['xingming']} ({user['yonghu_ming']}) - 密码: 123456")
    
    db.commit()
    return users

def create_workflow_tables(db):
    """创建审批流程相关表（如果不存在）"""
    print("\n" + "="*60)
    print("3. 创建审批流程表")
    print("="*60)

    # 创建审批流程步骤表
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS shenhe_liucheng_buzou (
            id VARCHAR(36) PRIMARY KEY,
            liucheng_id VARCHAR(36) NOT NULL,
            buzou_mingcheng VARCHAR(100) NOT NULL,
            buzou_shunxu INTEGER NOT NULL,
            shenhe_jiaose_id VARCHAR(36),
            buzou_leixing VARCHAR(50),
            buzou_zhuangtai VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted VARCHAR(1) DEFAULT 'N',
            FOREIGN KEY (liucheng_id) REFERENCES shenhe_liucheng(id)
        )
    """))
    print("  ✓ 审批流程步骤表已就绪")
    db.commit()

def create_workflow(db, roles):
    """创建审批流程配置"""
    print("\n" + "="*60)
    print("4. 创建审批流程配置")
    print("="*60)

    # 获取角色ID (PTC-W0063: 使用 next() 的默认值防止 StopIteration)
    salesperson_role = next((r for r in roles if r['jiaose_daima'] == 'salesperson'), None)
    finance_role = next((r for r in roles if r['jiaose_daima'] == 'finance'), None)

    if not salesperson_role or not finance_role:
        raise ValueError("缺少必要的角色: salesperson 或 finance")

    # 检查流程是否已存在
    result = db.execute(
        text("SELECT id FROM shenhe_liucheng WHERE liucheng_daima = 'bank_payment_approval' AND is_deleted = 'N'")
    ).fetchone()

    if result:
        print("  ✓ 审批流程已存在: 银行转账支付审批")
        workflow_id = result[0]
    else:
        workflow_id = str(uuid.uuid4())

        # 创建审批流程
        db.execute(
            text("""
                INSERT INTO shenhe_liucheng (
                    id, liucheng_mingcheng, liucheng_daima, liucheng_miaoshu,
                    shiyong_fanwei, liucheng_zhuangtai, created_at, updated_at, is_deleted
                )
                VALUES (
                    :id, :name, :code, :desc, :scope, :status, NOW(), NOW(), 'N'
                )
            """),
            {
                'id': workflow_id,
                'name': '银行转账支付审批',
                'code': 'bank_payment_approval',
                'desc': '客户选择银行转账后，业务员上传汇款单据，财务审核确认',
                'scope': 'payment',
                'status': 'active'
            }
        )

        # 创建审批步骤
        steps = [
            {
                'id': str(uuid.uuid4()),
                'liucheng_id': workflow_id,
                'buzou_mingcheng': '业务员上传汇款单据',
                'buzou_shunxu': 1,
                'shenhe_jiaose_id': salesperson_role['id'],
                'buzou_leixing': 'upload',
                'buzou_zhuangtai': 'active'
            },
            {
                'id': str(uuid.uuid4()),
                'liucheng_id': workflow_id,
                'buzou_mingcheng': '财务审核确认',
                'buzou_shunxu': 2,
                'shenhe_jiaose_id': finance_role['id'],
                'buzou_leixing': 'approval',
                'buzou_zhuangtai': 'active'
            }
        ]

        for step in steps:
            db.execute(
                text("""
                    INSERT INTO shenhe_liucheng_buzou (
                        id, liucheng_id, buzou_mingcheng, buzou_shunxu, shenhe_jiaose_id,
                        buzou_leixing, buzou_zhuangtai, created_at, updated_at, is_deleted
                    )
                    VALUES (
                        :id, :workflow_id, :name, :order, :role_id, :type, :status, NOW(), NOW(), 'N'
                    )
                """),
                {
                    'id': step['id'],
                    'workflow_id': step['liucheng_id'],
                    'name': step['buzou_mingcheng'],
                    'order': step['buzou_shunxu'],
                    'role_id': step['shenhe_jiaose_id'],
                    'type': step['buzou_leixing'],
                    'status': step['buzou_zhuangtai']
                }
            )

        print("  ✓ 创建审批流程: 银行转账支付审批")
        print("    - 步骤1: 业务员上传汇款单据")
        print("    - 步骤2: 财务审核确认")

    db.commit()
    return workflow_id

def main():
    """主函数"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("初始化银行转账支付审批流程")
        print("="*60)
        
        # 1. 创建角色
        roles = create_roles(db)

        # 2. 创建用户
        users = create_users(db, roles)

        # 3. 创建审批流程表
        create_workflow_tables(db)

        # 4. 创建审批流程
        workflow_id = create_workflow(db, roles)
        
        print("\n" + "="*60)
        print("✅ 初始化完成！")
        print("="*60)
        print("\n测试账号:")
        print("  业务员: salesperson1 / 123456")
        print("  财务:   finance1 / 123456")
        print("\n审批流程:")
        print("  1. 客户选择银行转账")
        print("  2. 业务员上传汇款单据")
        print("  3. 财务审核确认")
        print("  4. 系统自动更新支付状态")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

