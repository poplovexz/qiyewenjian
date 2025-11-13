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
import os
from pathlib import Path

# 添加src目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.security import get_password_hash
import uuid
from datetime import datetime


def ensure_admin_role(session):
    """确保系统管理员角色存在"""
    print("\n" + "=" * 60)
    print("【步骤1】检查系统管理员角色")
    print("=" * 60)
    
    # 检查角色是否存在
    result = session.execute(text("""
        SELECT id, jiaose_ming, jiaose_bianma 
        FROM jiaose 
        WHERE jiaose_bianma = 'admin' 
        AND is_deleted = 'N'
    """)).fetchone()
    
    if result:
        admin_role_id = result[0]
        print(f"✅ 系统管理员角色已存在: {result[1]} ({result[2]})")
        print(f"   角色ID: {admin_role_id}")
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
        print(f"✅ 已创建系统管理员角色")
        print(f"   角色ID: {admin_role_id}")
        return admin_role_id


def ensure_admin_user(session, admin_role_id):
    """确保admin用户存在并分配了管理员角色"""
    print("\n" + "=" * 60)
    print("【步骤2】检查admin用户")
    print("=" * 60)
    
    # 检查用户是否存在
    result = session.execute(text("""
        SELECT id, yonghu_ming, xingming 
        FROM yonghu 
        WHERE yonghu_ming = 'admin' 
        AND is_deleted = 'N'
    """)).fetchone()
    
    if result:
        admin_user_id = result[0]
        print(f"✅ admin用户已存在: {result[2]} ({result[1]})")
        print(f"   用户ID: {admin_user_id}")
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
        print(f"✅ 已创建admin用户")
        print(f"   用户ID: {admin_user_id}")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
    
    # 检查是否已分配角色
    print("\n" + "=" * 60)
    print("【步骤3】检查admin用户角色分配")
    print("=" * 60)
    
    result = session.execute(text("""
        SELECT id FROM yonghu_jiaose
        WHERE yonghu_id = :user_id 
        AND jiaose_id = :role_id 
        AND is_deleted = 'N'
    """), {"user_id": admin_user_id, "role_id": admin_role_id}).fetchone()
    
    if result:
        print("✅ admin用户已分配系统管理员角色")
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
        print("✅ 已为admin用户分配系统管理员角色")
    
    return admin_user_id


def assign_all_permissions_to_admin_role(session, admin_role_id):
    """为系统管理员角色分配所有权限"""
    print("\n" + "=" * 60)
    print("【步骤4】为系统管理员角色分配所有权限")
    print("=" * 60)
    
    # 获取所有活动权限
    all_permissions = session.execute(text("""
        SELECT id, quanxian_ming, quanxian_bianma 
        FROM quanxian 
        WHERE zhuangtai = 'active' 
        AND is_deleted = 'N'
        ORDER BY quanxian_bianma
    """)).fetchall()
    
    if not all_permissions:
        print("⚠️  系统中没有任何权限，请先运行权限初始化脚本")
        return
    
    print(f"📊 系统中共有 {len(all_permissions)} 个权限")
    
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
    
    print(f"\n📊 权限分配统计:")
    print(f"  - 新分配: {assigned_count} 个")
    print(f"  - 已存在: {existing_count} 个")
    print(f"  - 总计: {len(all_permissions)} 个")
    print(f"\n✅ 系统管理员角色现在拥有所有权限")


def verify_admin_permissions(session, admin_user_id):
    """验证admin用户的权限"""
    print("\n" + "=" * 60)
    print("【步骤5】验证admin用户权限")
    print("=" * 60)
    
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
        print(f"✅ admin用户拥有 {len(permissions)} 个权限")
        
        # 按模块分组显示
        modules = {}
        for perm_code, perm_name in permissions:
            module = perm_code.split(':')[0] if ':' in perm_code else 'other'
            if module not in modules:
                modules[module] = []
            modules[module].append((perm_code, perm_name))
        
        print(f"\n📋 权限模块统计:")
        for module, perms in sorted(modules.items()):
            print(f"  - {module}: {len(perms)} 个权限")
    else:
        print("❌ admin用户没有任何权限！")
        return False
    
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("确保admin用户拥有完整的系统管理员权限")
    print("=" * 60)
    
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
            print("\n" + "=" * 60)
            print("✅ admin用户权限配置完成！")
            print("=" * 60)
            print("\n登录信息:")
            print("  用户名: admin")
            print("  密码: admin123")
            print("\n⚠️  请在首次登录后立即修改密码！")
        else:
            print("\n" + "=" * 60)
            print("❌ admin用户权限配置失败！")
            print("=" * 60)
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

