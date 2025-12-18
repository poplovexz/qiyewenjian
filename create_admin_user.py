#!/usr/bin/env python3
"""
创建默认admin用户的脚本
"""
import sys
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加后端路径
sys.path.append('/var/www/packages/backend/src')

from core.security import get_password_hash

# 数据库配置
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"

def create_admin_user():
    """创建默认admin用户"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # 检查admin用户是否已存在
        result = db.execute(text(
            "SELECT id FROM yonghu WHERE yonghu_ming = 'admin' AND is_deleted = 'N'"
        )).fetchone()
        
        if result:
            print("Admin用户已存在")
            return True
        
        # 创建admin用户
        admin_id = str(uuid.uuid4())
        hashed_password = get_password_hash("admin123")
        
        db.execute(text("""
            INSERT INTO yonghu (
                id, yonghu_ming, mima, youxiang, xingming, shouji, 
                zhuangtai, denglu_cishu, created_by, created_at, updated_at, is_deleted
            ) VALUES (
                :id, 'admin', :password, 'admin@example.com', '系统管理员', '13800138000',
                'active', '0', 'system', NOW(), NOW(), 'N'
            )
        """), {
            "id": admin_id,
            "password": hashed_password
        })
        
        # 获取管理员角色ID
        admin_role = db.execute(text(
            "SELECT id FROM jiaose WHERE jiaose_ming = '系统管理员' OR jiaose_bianma = 'admin'"
        )).fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            
            # 为admin用户分配管理员角色
            db.execute(text("""
                INSERT INTO yonghu_jiaose (
                    id, yonghu_id, jiaose_id, created_by, created_at, updated_at, is_deleted
                ) VALUES (
                    :id, :user_id, :role_id, 'system', NOW(), NOW(), 'N'
                )
            """), {
                "id": str(uuid.uuid4()),
                "user_id": admin_id,
                "role_id": admin_role_id
            })
            print("为admin用户分配管理员角色成功")
        
        db.commit()
        print("✅ Admin用户创建成功")
        print("用户名: admin")
        print("密码: admin123")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建admin用户失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()