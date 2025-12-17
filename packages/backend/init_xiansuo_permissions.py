#!/usr/bin/env python3
"""
线索管理模块权限初始化脚本
"""
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

def init_xiansuo_permissions():
    """初始化线索管理模块权限"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("==================================================")
    print("线索管理模块 - 权限初始化")
    print("==================================================")
    
    try:
        # 线索管理权限列表
        xiansuo_permissions = [
            # 菜单权限
            ("线索管理菜单", "xiansuo:menu", "访问线索管理菜单的权限", "menu", "/leads"),
            ("线索来源菜单", "xiansuo:source_menu", "访问线索来源菜单的权限", "menu", "/lead-sources"),
            ("线索状态菜单", "xiansuo:status_menu", "访问线索状态菜单的权限", "menu", "/lead-statuses"),
            
            # 线索基础权限
            ("查看线索", "xiansuo:read", "查看自己创建的线索信息的权限", "api", "/api/v1/leads/*"),
            ("查看所有线索", "xiansuo:read_all", "查看所有用户创建的线索（管理员权限）", "api", "/api/v1/leads/*"),
            ("创建线索", "xiansuo:create", "创建新线索的权限", "api", "/api/v1/leads/"),
            ("编辑线索", "xiansuo:update", "编辑自己创建的线索信息的权限", "api", "/api/v1/leads/*"),
            ("编辑所有线索", "xiansuo:update_all", "编辑所有用户的线索（管理员权限）", "api", "/api/v1/leads/*"),
            ("删除线索", "xiansuo:delete", "删除自己创建的线索的权限", "api", "/api/v1/leads/*"),
            ("删除所有线索", "xiansuo:delete_all", "删除所有用户的线索（管理员权限）", "api", "/api/v1/leads/*"),
            
            # 线索状态管理权限
            ("管理线索状态", "xiansuo:status_manage", "管理线索状态的权限", "api", "/api/v1/leads/*/status"),
            ("分配线索", "xiansuo:assign", "分配线索给销售人员的权限", "api", "/api/v1/leads/*/assign"),
            
            # 线索来源管理权限
            ("查看线索来源", "xiansuo:source_read", "查看自己创建的线索来源的权限", "api", "/api/v1/lead-sources/*"),
            ("查看所有线索来源", "xiansuo:source_read_all", "查看所有用户创建的线索来源（管理员权限）", "api", "/api/v1/lead-sources/*"),
            ("创建线索来源", "xiansuo:source_create", "创建线索来源的权限", "api", "/api/v1/lead-sources/"),
            ("编辑线索来源", "xiansuo:source_update", "编辑自己创建的线索来源的权限", "api", "/api/v1/lead-sources/*"),
            ("编辑所有线索来源", "xiansuo:source_update_all", "编辑所有用户的线索来源（管理员权限）", "api", "/api/v1/lead-sources/*"),
            ("删除线索来源", "xiansuo:source_delete", "删除自己创建的线索来源的权限", "api", "/api/v1/lead-sources/*"),
            ("删除所有线索来源", "xiansuo:source_delete_all", "删除所有用户的线索来源（管理员权限）", "api", "/api/v1/lead-sources/*"),
            
            # 线索状态管理权限
            ("查看线索状态", "xiansuo:status_read", "查看线索状态的权限", "api", "/api/v1/lead-statuses/*"),
            ("创建线索状态", "xiansuo:status_create", "创建线索状态的权限", "api", "/api/v1/lead-statuses/"),
            ("编辑线索状态", "xiansuo:status_update", "编辑线索状态的权限", "api", "/api/v1/lead-statuses/*"),
            ("删除线索状态", "xiansuo:status_delete", "删除线索状态的权限", "api", "/api/v1/lead-statuses/*"),
            
            # 线索跟进管理权限
            ("查看跟进记录", "xiansuo:followup_read", "查看线索跟进记录的权限", "api", "/api/v1/lead-followups/*"),
            ("创建跟进记录", "xiansuo:followup_create", "创建线索跟进记录的权限", "api", "/api/v1/lead-followups/"),
            ("编辑跟进记录", "xiansuo:followup_update", "编辑线索跟进记录的权限", "api", "/api/v1/lead-followups/*"),
            ("删除跟进记录", "xiansuo:followup_delete", "删除线索跟进记录的权限", "api", "/api/v1/lead-followups/*"),
            
            # 线索统计权限
            ("查看线索统计", "xiansuo:statistics", "查看线索统计数据的权限", "api", "/api/v1/leads/statistics"),
            
            # 按钮权限
            ("新增线索按钮", "xiansuo:create_button", "显示新增线索按钮的权限", "button", "xiansuo-create-btn"),
            ("编辑线索按钮", "xiansuo:edit_button", "显示编辑线索按钮的权限", "button", "xiansuo-edit-btn"),
            ("删除线索按钮", "xiansuo:delete_button", "显示删除线索按钮的权限", "button", "xiansuo-delete-btn"),
            ("分配线索按钮", "xiansuo:assign_button", "显示分配线索按钮的权限", "button", "xiansuo-assign-btn"),
            ("跟进记录按钮", "xiansuo:followup_button", "显示跟进记录按钮的权限", "button", "xiansuo-followup-btn")
        ]
        
        # 检查并创建权限
        for perm_data in xiansuo_permissions:
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
                print(f"✅ 创建权限: {quanxian_ming} ({quanxian_bianma})")
            else:
                print(f"⚠️ 权限已存在: {quanxian_ming} ({quanxian_bianma})")
        
        db.commit()
        print("\n✅ 线索管理模块权限初始化完成！")
        
        # 为管理员角色分配所有权限
        print("\n🔧 为管理员角色分配线索管理权限...")

        # 获取管理员角色ID
        admin_role = db.execute(text(
            "SELECT id FROM jiaose WHERE jiaose_ming = '系统管理员' OR jiaose_ming = 'admin'"
        )).fetchone()

        if admin_role:
            admin_role_id = admin_role[0]
            
            # 获取所有线索管理权限
            xiansuo_perms = db.execute(text("""
                SELECT id, quanxian_ming FROM quanxian
                WHERE quanxian_bianma LIKE 'xiansuo:%' AND zhuangtai = 'active'
            """)).fetchall()
            
            # 为管理员角色分配权限
            for perm in xiansuo_perms:
                perm_id = perm[0]
                perm_name = perm[1]
                
                # 检查是否已经分配
                existing = db.execute(text("""
                    SELECT id FROM jiaose_quanxian 
                    WHERE jiaose_id = :role_id AND quanxian_id = :perm_id
                """), {"role_id": admin_role_id, "perm_id": perm_id}).fetchone()
                
                if not existing:
                    # 分配权限
                    relation_id = str(uuid.uuid4())
                    db.execute(text("""
                        INSERT INTO jiaose_quanxian (id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted)
                        VALUES (:id, :role_id, :perm_id, 'system', NOW(), NOW(), 'N')
                    """), {
                        "id": relation_id,
                        "role_id": admin_role_id,
                        "perm_id": perm_id
                    })
                    print(f"✅ 分配权限: {perm_name}")
                else:
                    print(f"⚠️ 权限已分配: {perm_name}")
            
            db.commit()
            print("\n✅ 管理员角色权限分配完成！")
        else:
            print("⚠️ 未找到管理员角色，请先创建管理员角色")
        
        print("==================================================")
        print("✓ 线索管理模块权限初始化完成！")
        print("==================================================")
        
    except Exception as e:
        print(f"❌ 权限初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_xiansuo_permissions()
