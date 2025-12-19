#!/usr/bin/env python3
"""
确保admin用户拥有完整的系统管理员权限

这个脚本会：
1. 检查并创建系统管理员角色（如果不存在）
2. 检查并创建admin用户（如果不存在）
3. 确保admin用户被分配了系统管理员角色
4. 确保系统管理员角色拥有所有权限

这个脚本应该在每次部署后运行，以确保admin用户始终有正确的权限。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.security import get_password_hash
import uuid

def ensure_admin_role(session):
    """确保系统管理员角色存在"""
    
    # 检查角色是否存在
    result = session.execute(text("""
        SELECT id, jiaose_ming, jiaose_bianma 
        FROM jiaose 
        WHERE jiaose_bianma = 'admin' 
        AND is_deleted = 'N'
    """)).fetchone()
    
    if result:
        admin_role_id = result[0]
        return admin_role_id
    else:
        # 创建系统管理员角色
        admin_role_id = str(uuid.uuid4()).replace('-', '')
        session.execute(text("""
            INSERT INTO jiaose (
                id, jiaose_bianma, jiaose_ming, miaoshu, zhuangtai,
                is_deleted, created_at, updated_at, created_by
            ) VALUES (
                :id, 'admin', '系统管理员', '系统最高权限管理员', 'active',
                'N', NOW(), NOW(), 'system'
            )
        """), {"id": admin_role_id})
        
        session.commit()
        return admin_role_id

def ensure_admin_user(session, admin_role_id):
    """确保admin用户存在并分配了管理员角色"""
    
    # 检查用户是否存在
    result = session.execute(text("""
        SELECT id, yonghu_ming, xingming 
        FROM yonghu 
        WHERE yonghu_ming = 'admin' 
        AND is_deleted = 'N'
    """)).fetchone()
    
    if result:
        admin_user_id = result[0]
    else:
        # 创建admin用户
        admin_user_id = str(uuid.uuid4()).replace('-', '')
        hashed_password = get_password_hash("admin123")
        
        session.execute(text("""
            INSERT INTO yonghu (
                id, yonghu_ming, mima, youxiang, xingming, shouji, 
                zhuangtai, denglu_cishu, created_by, created_at, updated_at, is_deleted
            ) VALUES (
                :id, 'admin', :password, 'admin@example.com', '系统管理员', '13800138000',
                'active', '0', 'system', NOW(), NOW(), 'N'
            )
        """), {
            "id": admin_user_id,
            "password": hashed_password
        })
        
        session.commit()
    
    # 检查是否已分配角色
    
    result = session.execute(text("""
        SELECT id FROM yonghu_jiaose
        WHERE yonghu_id = :user_id 
        AND jiaose_id = :role_id 
        AND is_deleted = 'N'
    """), {"user_id": admin_user_id, "role_id": admin_role_id}).fetchone()
    
    if result:
    else:
        # 分配角色
        relation_id = str(uuid.uuid4()).replace('-', '')
        session.execute(text("""
            INSERT INTO yonghu_jiaose (
                id, yonghu_id, jiaose_id, created_by, created_at, updated_at, is_deleted
            ) VALUES (
                :id, :user_id, :role_id, 'system', NOW(), NOW(), 'N'
            )
        """), {
            "id": relation_id,
            "user_id": admin_user_id,
            "role_id": admin_role_id
        })
        
        session.commit()
    
    return admin_user_id

def assign_all_permissions_to_admin_role(session, admin_role_id):
    """为系统管理员角色分配所有权限"""
    
    # 获取所有活动权限
    all_permissions = session.execute(text("""
        SELECT id, quanxian_ming, quanxian_bianma 
        FROM quanxian 
        WHERE zhuangtai = 'active' 
        AND is_deleted = 'N'
        ORDER BY quanxian_bianma
    """)).fetchall()
    
    if not all_permissions:
        return
    
    assigned_count = 0
    existing_count = 0
    
    for perm in all_permissions:
        perm_id, perm_name, perm_code = perm
        
        # 检查是否已分配
        result = session.execute(text("""
            SELECT id FROM jiaose_quanxian 
            WHERE jiaose_id = :role_id 
            AND quanxian_id = :perm_id 
            AND is_deleted = 'N'
        """), {"role_id": admin_role_id, "perm_id": perm_id}).fetchone()
        
        if not result:
            # 分配权限
            relation_id = str(uuid.uuid4()).replace('-', '')
            session.execute(text("""
                INSERT INTO jiaose_quanxian (
                    id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted
                ) VALUES (
                    :id, :role_id, :perm_id, 'system', NOW(), NOW(), 'N'
                )
            """), {
                "id": relation_id,
                "role_id": admin_role_id,
                "perm_id": perm_id
            })
            assigned_count += 1
        else:
            existing_count += 1
    
    session.commit()
    
def verify_admin_permissions(session, admin_user_id):
    """验证admin用户的权限"""
    
    # 获取admin用户的所有权限
    permissions = session.execute(text("""
        SELECT DISTINCT p.quanxian_bianma, p.quanxian_ming 
        FROM quanxian p
        JOIN jiaose_quanxian rp ON p.id = rp.quanxian_id
        JOIN jiaose r ON rp.jiaose_id = r.id
        JOIN yonghu_jiaose ur ON r.id = ur.jiaose_id
        WHERE ur.yonghu_id = :user_id
        AND p.is_deleted = 'N'
        AND r.is_deleted = 'N'
        AND ur.is_deleted = 'N'
        AND rp.is_deleted = 'N'
        ORDER BY p.quanxian_bianma
    """), {"user_id": admin_user_id}).fetchall()
    
    if permissions:
        
        # 按模块分组显示
        modules = {}
        for perm_code, perm_name in permissions:
            module = perm_code.split(':')[0] if ':' in perm_code else 'other'
            if module not in modules:
                modules[module] = []
            modules[module].append((perm_code, perm_name))
        
        for module, perms in sorted(modules.items()):
    else:
        return False
    
    return True

def main():
    """主函数"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 步骤1：确保系统管理员角色存在
        admin_role_id = ensure_admin_role(session)
        
        # 步骤2：确保admin用户存在并分配了角色
        admin_user_id = ensure_admin_user(session, admin_role_id)
        
        # 步骤3：为系统管理员角色分配所有权限
        assign_all_permissions_to_admin_role(session, admin_role_id)
        
        # 步骤4：验证admin用户权限
        success = verify_admin_permissions(session, admin_user_id)
        
        if success:
        else:
            return False
        
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
