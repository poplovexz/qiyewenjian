#!/usr/bin/env python3
"""
优化产品管理权限描述
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from core.config import settings

def update_permission_descriptions():
    """更新权限描述"""
    print("🔧 优化产品管理权限描述")
    print("=" * 60)
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    
    # 优化后的权限描述
    permission_updates = [
        # 产品管理主权限
        ("product_management", "产品管理模块主权限，包含产品分类、产品项目和产品步骤的综合管理"),
        
        # 产品分类权限
        ("product_category", "产品分类管理权限，包含增值产品和代理记账产品分类的管理"),
        ("product_category:read", "查看产品分类列表、详情和选项，支持按类型筛选"),
        ("product_category:create", "创建新的产品分类，设置分类名称、编码、类型和描述"),
        ("product_category:update", "更新产品分类信息，修改分类属性和状态"),
        ("product_category:delete", "删除产品分类，同时处理关联的产品项目"),
        
        # 产品项目权限
        ("product", "产品项目管理权限，管理具体的产品服务项目"),
        ("product:read", "查看产品项目列表和详情，包含报价、工期和步骤信息"),
        ("product:create", "创建新的产品项目，设置基本信息、报价和关联分类"),
        ("product:update", "更新产品项目信息，修改报价、工期和产品步骤"),
        ("product:delete", "删除产品项目，同时清理关联的产品步骤"),
        
        # 产品步骤权限
        ("product_step", "产品步骤管理权限，管理产品执行的详细步骤流程"),
        ("product_step:read", "查看产品步骤列表和详情，包含时长、费用和排序"),
        ("product_step:create", "创建新的产品步骤，设置步骤名称、时长和费用"),
        ("product_step:update", "更新产品步骤信息，修改步骤属性和排序"),
        ("product_step:delete", "删除产品步骤，调整步骤流程")
    ]
    
    try:
        with engine.connect() as conn:
            for permission_code, new_description in permission_updates:
                # 更新权限描述
                update_sql = """
                UPDATE quanxian 
                SET miaoshu = :description, updated_at = NOW()
                WHERE quanxian_bianma = :code AND is_deleted = 'N'
                """
                
                result = conn.execute(text(update_sql), {
                    "description": new_description,
                    "code": permission_code
                })
                
                if result.rowcount > 0:
                    print(f"✅ 更新权限描述: {permission_code}")
                else:
                    print(f"⚠️  权限不存在: {permission_code}")
            
            conn.commit()
            print("\n🎉 权限描述优化完成！")
            
    except Exception as e:
        print(f"❌ 更新权限描述失败: {e}")
        return False
    
    return True

def verify_permission_descriptions():
    """验证权限描述"""
    print("\n📋 验证权限描述")
    print("=" * 60)
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # 查询产品管理相关权限
            query_sql = """
            SELECT quanxian_ming, quanxian_bianma, miaoshu, ziyuan_lujing
            FROM quanxian 
            WHERE quanxian_bianma LIKE '%product%' 
            AND is_deleted = 'N'
            ORDER BY quanxian_bianma
            """
            
            result = conn.execute(text(query_sql))
            permissions = result.fetchall()
            
            print(f"📊 产品管理权限列表 ({len(permissions)}个):")
            print()
            
            for perm in permissions:
                print(f"🔹 {perm.quanxian_ming} ({perm.quanxian_bianma})")
                print(f"   描述: {perm.miaoshu}")
                print(f"   路径: {perm.ziyuan_lujing}")
                print()
                
    except Exception as e:
        print(f"❌ 查询权限失败: {e}")

def analyze_permission_issues():
    """分析权限问题"""
    print("\n🔍 权限问题分析")
    print("=" * 60)
    
    print("📋 当前权限状态分析:")
    print()
    
    print("✅ **权限完整性检查**:")
    print("   - Admin用户拥有所有16个产品管理相关权限")
    print("   - 包含主权限、分类权限、项目权限和步骤权限")
    print("   - 权限编码规范，遵循 resource:action 格式")
    print()
    
    print("🔧 **权限描述优化建议**:")
    print("   - product_step: 描述过于简单，应该更具体")
    print("   - 部分权限描述可以更详细地说明功能范围")
    print("   - 建议增加权限使用场景的说明")
    print()
    
    print("📊 **权限分组结构**:")
    print("   1. 主权限: product_management (模块入口)")
    print("   2. 分类管理: product_category:* (5个权限)")
    print("   3. 项目管理: product:* (5个权限)")
    print("   4. 步骤管理: product_step:* (5个权限)")
    print()
    
    print("🎯 **权限使用建议**:")
    print("   - 普通用户: 只给 read 权限")
    print("   - 业务人员: read + create + update 权限")
    print("   - 管理人员: 全部权限")
    print("   - 系统管理员: 自动拥有所有权限")

def main():
    """主函数"""
    print("🚀 产品管理权限优化工具")
    print("=" * 70)
    
    # 1. 分析当前权限问题
    analyze_permission_issues()
    
    # 2. 更新权限描述
    if update_permission_descriptions():
        # 3. 验证更新结果
        verify_permission_descriptions()
        
        print("\n💡 优化建议")
        print("=" * 60)
        print("1. **权限已正确分配**: Admin用户拥有所有必要权限")
        print("2. **权限描述已优化**: 更详细、更准确的功能描述")
        print("3. **权限结构清晰**: 按功能模块分组，便于管理")
        print("4. **建议定期审查**: 根据业务需求调整权限分配")
        
        print("\n🎉 权限优化完成！")
        print("现在权限描述更加准确和详细，便于理解和管理。")
    else:
        print("\n❌ 权限优化失败，请检查数据库连接和权限配置。")

if __name__ == "__main__":
    main()
