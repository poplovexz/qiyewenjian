"""
初始化客户管理模块权限
"""
import uuid
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_customer_permissions():
    """初始化客户管理模块权限"""
    from sqlalchemy import text
    
    db = SessionLocal()
    
    try:
        # 客户管理权限列表
        customer_permissions = [
            # 菜单权限
            ("客户管理菜单", "customer:menu", "访问客户管理菜单的权限", "menu", "/customers"),
            
            # 客户基础权限
            ("查看客户", "customer:read", "查看客户信息的权限", "api", "/api/v1/customers/*"),
            ("创建客户", "customer:create", "创建新客户的权限", "api", "/api/v1/customers/"),
            ("编辑客户", "customer:update", "编辑客户信息的权限", "api", "/api/v1/customers/*"),
            ("删除客户", "customer:delete", "删除客户的权限", "api", "/api/v1/customers/*"),
            
            # 客户状态管理权限
            ("管理客户状态", "customer:status_manage", "管理客户状态（活跃、续约中、已终止）的权限", "api", "/api/v1/customers/*/status"),
            
            # 服务记录权限
            ("查看服务记录", "service_record:read", "查看客户服务记录的权限", "api", "/api/v1/service-records/*"),
            ("创建服务记录", "service_record:create", "创建客户服务记录的权限", "api", "/api/v1/service-records/"),
            ("编辑服务记录", "service_record:update", "编辑客户服务记录的权限", "api", "/api/v1/service-records/*"),
            ("删除服务记录", "service_record:delete", "删除客户服务记录的权限", "api", "/api/v1/service-records/*"),
            
            # 按钮权限
            ("新增客户按钮", "customer:create_button", "显示新增客户按钮的权限", "button", "customer-create-btn"),
            ("编辑客户按钮", "customer:edit_button", "显示编辑客户按钮的权限", "button", "customer-edit-btn"),
            ("删除客户按钮", "customer:delete_button", "显示删除客户按钮的权限", "button", "customer-delete-btn"),
            ("状态管理按钮", "customer:status_button", "显示客户状态管理按钮的权限", "button", "customer-status-btn"),
            ("服务记录按钮", "service_record:manage_button", "显示服务记录管理按钮的权限", "button", "service-record-btn")
        ]
        
        # 检查并创建权限
        for perm_data in customer_permissions:
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
        print("客户管理模块权限初始化完成！")
        
        # 为管理员角色分配所有客户管理权限
        print("\n为管理员角色分配客户管理权限...")
        
        # 获取管理员角色ID
        admin_role = db.execute(text(
            "SELECT id FROM jiaose WHERE jiaose_ming = '管理员'"
        )).fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            
            # 获取所有客户管理权限
            customer_perms = db.execute(text("""
                SELECT id, quanxian_ming FROM quanxian 
                WHERE quanxian_bianma LIKE 'customer:%' 
                   OR quanxian_bianma LIKE 'service_record:%'
            """)).fetchall()
            
            for perm in customer_perms:
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
            print("管理员权限分配完成！")
        else:
            print("未找到管理员角色")
        
    except Exception as e:
        db.rollback()
        print(f"权限初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_customer_permissions()
