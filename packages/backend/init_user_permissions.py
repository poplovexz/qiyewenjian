"""
初始化用户管理模块权限
"""
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_user_permissions():
    """初始化用户管理模块权限"""
    db = SessionLocal()
    
    try:
        # 用户管理权限列表
        user_permissions = [
            # 用户管理权限
            ("用户管理菜单", "user:menu", "访问用户管理菜单的权限", "menu", "/users"),
            ("查看用户", "user:read", "查看用户信息的权限", "api", "/api/v1/users/*"),
            ("创建用户", "user:create", "创建新用户的权限", "api", "/api/v1/users/"),
            ("编辑用户", "user:update", "编辑用户信息的权限", "api", "/api/v1/users/*"),
            ("删除用户", "user:delete", "删除用户的权限", "api", "/api/v1/users/*"),
            ("重置密码", "user:reset_password", "重置用户密码的权限", "api", "/api/v1/users/*/reset-password"),
            ("用户状态管理", "user:status_manage", "管理用户状态的权限", "api", "/api/v1/users/*/status"),
            
            # 角色管理权限
            ("角色管理菜单", "role:menu", "访问角色管理菜单的权限", "menu", "/roles"),
            ("查看角色", "role:read", "查看角色信息的权限", "api", "/api/v1/roles/*"),
            ("创建角色", "role:create", "创建新角色的权限", "api", "/api/v1/roles/"),
            ("编辑角色", "role:update", "编辑角色信息的权限", "api", "/api/v1/roles/*"),
            ("删除角色", "role:delete", "删除角色的权限", "api", "/api/v1/roles/*"),
            ("角色权限管理", "role:permission_manage", "管理角色权限的权限", "api", "/api/v1/roles/*/permissions"),
            
            # 权限管理权限
            ("权限管理菜单", "permission:menu", "访问权限管理菜单的权限", "menu", "/permissions"),
            ("查看权限", "permission:read", "查看权限信息的权限", "api", "/api/v1/permissions/*"),
            ("创建权限", "permission:create", "创建新权限的权限", "api", "/api/v1/permissions/"),
            ("编辑权限", "permission:update", "编辑权限信息的权限", "api", "/api/v1/permissions/*"),
            ("删除权限", "permission:delete", "删除权限的权限", "api", "/api/v1/permissions/*"),
            
            # 按钮权限
            ("新增用户按钮", "user:create_button", "显示新增用户按钮的权限", "button", "user-create-btn"),
            ("编辑用户按钮", "user:edit_button", "显示编辑用户按钮的权限", "button", "user-edit-btn"),
            ("删除用户按钮", "user:delete_button", "显示删除用户按钮的权限", "button", "user-delete-btn"),
            ("重置密码按钮", "user:reset_password_button", "显示重置密码按钮的权限", "button", "user-reset-password-btn"),
            
            ("新增角色按钮", "role:create_button", "显示新增角色按钮的权限", "button", "role-create-btn"),
            ("编辑角色按钮", "role:edit_button", "显示编辑角色按钮的权限", "button", "role-edit-btn"),
            ("删除角色按钮", "role:delete_button", "显示删除角色按钮的权限", "button", "role-delete-btn"),
            ("权限管理按钮", "role:permission_manage_button", "显示权限管理按钮的权限", "button", "role-permission-btn"),
            
            ("新增权限按钮", "permission:create_button", "显示新增权限按钮的权限", "button", "permission-create-btn"),
            ("编辑权限按钮", "permission:edit_button", "显示编辑权限按钮的权限", "button", "permission-edit-btn"),
            ("删除权限按钮", "permission:delete_button", "显示删除权限按钮的权限", "button", "permission-delete-btn"),
        ]
        
        # 检查并创建权限
        for perm_data in user_permissions:
            quanxian_ming, quanxian_bianma, miaoshu, ziyuan_leixing, ziyuan_lujing = perm_data
            
            # 检查权限是否已存在
            result = db.execute(text(
                "SELECT id FROM quanxian WHERE quanxian_bianma = :code"
            ), {"code": quanxian_bianma}).fetchone()
            
            if not result:
                # 创建新权限
                permission_id = str(uuid.uuid4())
                db.execute(text("""
                    INSERT INTO quanxian (
                        id, quanxian_ming, quanxian_bianma, miaoshu, 
                        ziyuan_leixing, ziyuan_lujing, zhuangtai, 
                        created_by, created_at, updated_at, is_deleted
                    ) VALUES (
                        :id, :ming, :bianma, :miaoshu, 
                        :leixing, :lujing, 'active', 
                        'system', NOW(), NOW(), 'N'
                    )
                """), {
                    "id": permission_id,
                    "ming": quanxian_ming,
                    "bianma": quanxian_bianma,
                    "miaoshu": miaoshu,
                    "leixing": ziyuan_leixing,
                    "lujing": ziyuan_lujing
                })
                print(f"创建权限: {quanxian_ming} ({quanxian_bianma})")
            else:
                print(f"权限已存在: {quanxian_ming} ({quanxian_bianma})")
        
        db.commit()
        print("用户管理模块权限初始化完成！")
        
        # 为管理员角色分配所有用户管理权限
        print("\n为管理员角色分配用户管理权限...")
        
        # 获取管理员角色ID
        admin_role = db.execute(text(
            "SELECT id FROM jiaose WHERE jiaose_ming = '系统管理员'"
        )).fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            
            # 获取所有用户管理权限
            user_perms = db.execute(text("""
                SELECT id, quanxian_ming FROM quanxian 
                WHERE quanxian_bianma LIKE 'user:%' 
                   OR quanxian_bianma LIKE 'role:%'
                   OR quanxian_bianma LIKE 'permission:%'
            """)).fetchall()
            
            for perm in user_perms:
                perm_id, perm_name = perm
                
                # 检查是否已分配
                existing = db.execute(text("""
                    SELECT id FROM jiaose_quanxian 
                    WHERE jiaose_id = :role_id AND quanxian_id = :perm_id
                """), {"role_id": admin_role_id, "perm_id": perm_id}).fetchone()
                
                if not existing:
                    # 分配权限
                    db.execute(text("""
                        INSERT INTO jiaose_quanxian (
                            id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted
                        ) VALUES (
                            :id, :role_id, :perm_id, 'system', NOW(), NOW(), 'N'
                        )
                    """), {
                        "id": str(uuid.uuid4()),
                        "role_id": admin_role_id,
                        "perm_id": perm_id
                    })
                    print(f"为管理员分配权限: {perm_name}")
                else:
                    print(f"管理员已有权限: {perm_name}")
            
            db.commit()
            print("管理员用户管理权限分配完成！")
        else:
            print("未找到管理员角色")
        
    except Exception as e:
        db.rollback()
        print(f"权限初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_user_permissions()
