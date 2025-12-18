#!/usr/bin/env python3
"""
修复admin角色问题
1. 创建admin角色（如果不存在）
2. 将admin用户分配到admin角色
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def fix_admin_role():
    """修复admin角色"""
    session = Session()
    
    try:
        print("\n" + "=" * 60)
        print("修复 Admin 角色配置")
        print("=" * 60)
        
        # 1. 查找admin用户
        admin_user = session.execute(
            text("""
            SELECT id, yonghu_ming, xingming 
            FROM yonghu 
            WHERE yonghu_ming = 'admin' 
            AND is_deleted = 'N'
            """)
        ).fetchone()
        
        if not admin_user:
            print("\n❌ 错误：未找到admin用户")
            return False
        
        admin_user_id = admin_user[0]
        print(f"\n✅ 找到admin用户: {admin_user[2]}（{admin_user[1]}）")
        print(f"   用户ID: {admin_user_id}")
        
        # 2. 检查admin角色是否存在
        admin_role = session.execute(
            text("""
            SELECT id, jiaose_bianma, jiaose_ming 
            FROM jiaose 
            WHERE jiaose_bianma = 'admin' 
            AND is_deleted = 'N'
            """)
        ).fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            print(f"\n✅ admin角色已存在: {admin_role[2]}（{admin_role[1]}）")
            print(f"   角色ID: {admin_role_id}")
        else:
            # 创建admin角色
            admin_role_id = str(uuid.uuid4())
            session.execute(
                text("""
                INSERT INTO jiaose (
                    id, jiaose_bianma, jiaose_ming, miaoshu, zhuangtai,
                    is_deleted, created_at, updated_at
                ) VALUES (
                    :id, 'admin', '系统管理员', '系统管理员角色', 'active',
                    'N', :created_at, :updated_at
                )
                """),
                {
                    "id": admin_role_id,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
            print("\n✅ 已创建admin角色")
            print(f"   角色ID: {admin_role_id}")
        
        # 3. 检查用户角色关联是否存在
        user_role = session.execute(
            text("""
            SELECT id 
            FROM yonghu_jiaose 
            WHERE yonghu_id = :yonghu_id 
            AND jiaose_id = :jiaose_id 
            AND is_deleted = 'N'
            """),
            {
                "yonghu_id": admin_user_id,
                "jiaose_id": admin_role_id
            }
        ).fetchone()
        
        if user_role:
            print("\n✅ admin用户已关联admin角色")
        else:
            # 创建用户角色关联
            user_role_id = str(uuid.uuid4())
            session.execute(
                text("""
                INSERT INTO yonghu_jiaose (
                    id, yonghu_id, jiaose_id,
                    is_deleted, created_at, updated_at
                ) VALUES (
                    :id, :yonghu_id, :jiaose_id,
                    'N', :created_at, :updated_at
                )
                """),
                {
                    "id": user_role_id,
                    "yonghu_id": admin_user_id,
                    "jiaose_id": admin_role_id,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
            print("\n✅ 已将admin用户关联到admin角色")
        
        session.commit()
        
        # 4. 验证
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)
        
        result = session.execute(
            text("""
            SELECT y.yonghu_ming, y.xingming, j.jiaose_bianma, j.jiaose_ming
            FROM yonghu y
            JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
            JOIN jiaose j ON yj.jiaose_id = j.id
            WHERE y.yonghu_ming = 'admin'
            AND y.is_deleted = 'N'
            AND j.is_deleted = 'N'
            AND yj.is_deleted = 'N'
            """)
        ).fetchall()
        
        if result:
            print("\n✅ admin用户的角色：")
            for row in result:
                print(f"   - {row[3]}（{row[2]}）")
        else:
            print("\n❌ 验证失败：admin用户没有角色")
            return False
        
        print("\n" + "=" * 60)
        print("✅ 修复完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = fix_admin_role()
    sys.exit(0 if success else 1)

