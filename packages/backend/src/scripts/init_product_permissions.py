"""
初始化产品管理相关权限的脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from core.config import settings


def init_product_permissions():
    """初始化产品管理相关权限"""
    print("开始初始化产品管理权限...")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # 产品管理权限数据
            permissions_sql = """
            INSERT INTO quanxian (
                id, quanxian_ming, quanxian_bianma, miaoshu,
                ziyuan_leixing, ziyuan_lujing, zhuangtai,
                created_by, created_at, updated_at, is_deleted
            ) VALUES
            -- 产品管理主权限
            (
                'perm_product_main', '产品管理', 'product_management', '产品管理模块主权限',
                'menu', '/product-management', 'active',
                'system', NOW(), NOW(), 'N'
            ),

            -- 产品分类管理权限
            (
                'perm_product_category', '产品分类管理', 'product_category', '产品分类管理权限',
                'menu', '/product-categories', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_category_read', '查看产品分类', 'product_category:read', '查看产品分类列表和详情',
                'api', '/api/v1/product-management/categories', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_category_create', '创建产品分类', 'product_category:create', '创建新的产品分类',
                'api', '/api/v1/product-management/categories', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_category_update', '更新产品分类', 'product_category:update', '更新产品分类信息',
                'api', '/api/v1/product-management/categories', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_category_delete', '删除产品分类', 'product_category:delete', '删除产品分类',
                'api', '/api/v1/product-management/categories', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            
            -- 产品项目管理权限
            (
                'perm_product', '产品项目管理', 'product', '产品项目管理权限',
                'menu', '/products', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_read', '查看产品项目', 'product:read', '查看产品项目列表和详情',
                'api', '/api/v1/product-management/products', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_create', '创建产品项目', 'product:create', '创建新的产品项目',
                'api', '/api/v1/product-management/products', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_update', '更新产品项目', 'product:update', '更新产品项目信息和步骤',
                'api', '/api/v1/product-management/products', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_delete', '删除产品项目', 'product:delete', '删除产品项目',
                'api', '/api/v1/product-management/products', 'active',
                'system', NOW(), NOW(), 'N'
            ),

            -- 产品步骤管理权限
            (
                'perm_product_step', '产品步骤管理', 'product_step', '产品步骤管理权限',
                'api', '/api/v1/product-management/steps', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_step_read', '查看产品步骤', 'product_step:read', '查看产品步骤列表和详情',
                'api', '/api/v1/product-management/steps', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_step_create', '创建产品步骤', 'product_step:create', '创建新的产品步骤',
                'api', '/api/v1/product-management/steps', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_step_update', '更新产品步骤', 'product_step:update', '更新产品步骤信息',
                'api', '/api/v1/product-management/steps', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'perm_product_step_delete', '删除产品步骤', 'product_step:delete', '删除产品步骤',
                'api', '/api/v1/product-management/steps', 'active',
                'system', NOW(), NOW(), 'N'
            )
            ON CONFLICT (id) DO NOTHING;
            """
            
            conn.execute(text(permissions_sql))
            conn.commit()
            
        print("✅ 产品管理权限初始化成功！")
        print("已创建权限：")
        print("  - 产品管理主权限")
        print("  - 产品分类管理权限 (4个操作权限)")
        print("  - 产品项目管理权限 (4个操作权限)")
        print("  - 产品步骤管理权限 (4个操作权限)")
        
    except Exception as e:
        print(f"❌ 初始化产品管理权限失败: {e}")
        return False
    
    return True


def assign_permissions_to_admin():
    """为管理员角色分配产品管理权限"""
    print("\n开始为管理员角色分配产品管理权限...")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # 查找管理员角色
            admin_role_result = conn.execute(text("""
                SELECT id FROM jiaose WHERE jiaose_bianma = 'admin' AND is_deleted = 'N'
            """)).fetchone()
            
            if not admin_role_result:
                print("⚠️  未找到管理员角色，跳过权限分配")
                return True
            
            admin_role_id = admin_role_result[0]
            
            # 为管理员角色分配所有产品管理权限
            role_permission_sql = """
            INSERT INTO jiaose_quanxian (id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted)
            SELECT
                'rp_product_' || substr(q.id, 6),
                :admin_role_id_1,
                q.id,
                'system',
                NOW(),
                NOW(),
                'N'
            FROM quanxian q
            WHERE q.quanxian_bianma LIKE 'product%%'
            AND q.is_deleted = 'N'
            AND NOT EXISTS (
                SELECT 1 FROM jiaose_quanxian jq
                WHERE jq.jiaose_id = :admin_role_id_2 AND jq.quanxian_id = q.id AND jq.is_deleted = 'N'
            );
            """
            
            conn.execute(text(role_permission_sql), {"admin_role_id_1": admin_role_id, "admin_role_id_2": admin_role_id})
            conn.commit()
            
        print("✅ 管理员角色权限分配成功！")
        
    except Exception as e:
        print(f"❌ 分配管理员权限失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("产品管理权限初始化")
    print("=" * 50)
    
    # 初始化权限
    if not init_product_permissions():
        return
    
    # 为管理员分配权限
    if not assign_permissions_to_admin():
        return
    
    print("\n🎉 产品管理权限初始化完成！")
    print("\n接下来您可以：")
    print("1. 重新登录系统以获取最新权限")
    print("2. 在角色管理中为其他角色分配产品管理权限")
    print("3. 访问产品管理页面进行操作")


if __name__ == "__main__":
    main()
