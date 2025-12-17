#!/usr/bin/env python3
"""
检查用户权限脚本
"""

import sys
import os

# 添加后端源码路径
backend_src = os.path.join(os.path.dirname(__file__), 'packages/backend/src')
sys.path.insert(0, backend_src)

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from core.database import SessionLocal
from models.yonghu_guanli import Yonghu, Jiaose, Quanxian, YonghuJiaose, JiaoseQuanxian

def check_user_permissions():
    """检查用户权限"""
    db: Session = SessionLocal()
    
    try:
        # 查找admin用户
        admin_user = db.query(Yonghu).filter(Yonghu.yonghu_ming == "admin").first()
        if not admin_user:
            print("❌ 未找到admin用户")
            return False
        
        print(f"✅ 找到用户: {admin_user.yonghu_ming} (ID: {admin_user.id})")
        
        # 查找用户的角色
        user_roles = db.query(Jiaose).join(YonghuJiaose).filter(
            YonghuJiaose.yonghu_id == admin_user.id
        ).all()
        
        print(f"📋 用户角色数量: {len(user_roles)}")
        for role in user_roles:
            print(f"  - {role.jiaose_ming} ({role.jiaose_bianma})")
        
        # 查找客户管理和服务记录相关权限
        customer_permissions = db.query(Quanxian).filter(
            or_(
                Quanxian.quanxian_bianma.like("customer%"),
                Quanxian.quanxian_bianma.like("service_record%")
            )
        ).all()

        print(f"\n🔑 客户管理和服务记录权限数量: {len(customer_permissions)}")
        for perm in customer_permissions:
            print(f"  - {perm.quanxian_ming} ({perm.quanxian_bianma})")

        # 检查用户是否有客户管理权限
        user_permissions = []
        for role in user_roles:
            role_permissions = db.query(Quanxian).join(JiaoseQuanxian).filter(
                JiaoseQuanxian.jiaose_id == role.id
            ).all()
            user_permissions.extend(role_permissions)

        customer_user_permissions = [p for p in user_permissions if
                                   p.quanxian_bianma.startswith("customer") or
                                   p.quanxian_bianma.startswith("service_record")]

        print(f"\n✅ 用户拥有的客户管理和服务记录权限数量: {len(customer_user_permissions)}")
        for perm in customer_user_permissions:
            print(f"  - {perm.quanxian_ming} ({perm.quanxian_bianma})")
        
        if len(customer_user_permissions) == 0:
            print("\n⚠️ 用户没有客户管理权限，需要分配权限")
            
            # 尝试给admin角色分配所有客户管理权限
            admin_role = db.query(Jiaose).filter(Jiaose.jiaose_bianma == "admin").first()
            if admin_role:
                print(f"🔧 正在给 {admin_role.jiaose_ming} 角色分配客户管理权限...")
                
                for perm in customer_permissions:
                    # 检查是否已经有这个权限
                    existing = db.query(JiaoseQuanxian).filter(
                        JiaoseQuanxian.jiaose_id == admin_role.id,
                        JiaoseQuanxian.quanxian_id == perm.id
                    ).first()
                    
                    if not existing:
                        role_permission = JiaoseQuanxian(
                            jiaose_id=admin_role.id,
                            quanxian_id=perm.id,
                            created_by="system"
                        )
                        db.add(role_permission)
                        print(f"  ✅ 添加权限: {perm.quanxian_ming}")
                    else:
                        print(f"  ⚪ 权限已存在: {perm.quanxian_ming}")
                
                db.commit()
                print("🎉 权限分配完成！")
            else:
                print("❌ 未找到admin角色")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查权限时发生错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("🔍 检查用户权限...")
    print("=" * 50)
    
    success = check_user_permissions()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 权限检查完成")
    else:
        print("❌ 权限检查失败")
    
    return success

if __name__ == "__main__":
    main()
