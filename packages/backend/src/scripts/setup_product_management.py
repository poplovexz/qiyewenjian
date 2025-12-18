"""
产品管理模块一键初始化脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from create_product_tables import create_product_tables, insert_sample_data
from init_product_permissions import init_product_permissions, assign_permissions_to_admin


def main():
    """主函数 - 一键初始化产品管理模块"""
    print("🚀 产品管理模块一键初始化")
    print("=" * 60)
    
    success_count = 0
    total_steps = 4
    
    # 步骤1: 创建数据表
    print("\n📋 步骤 1/4: 创建产品管理数据表")
    print("-" * 40)
    if create_product_tables():
        success_count += 1
        print("✅ 数据表创建成功")
    else:
        print("❌ 数据表创建失败")
    
    # 步骤2: 插入示例数据
    print("\n📋 步骤 2/4: 插入示例数据")
    print("-" * 40)
    if insert_sample_data():
        success_count += 1
        print("✅ 示例数据插入成功")
    else:
        print("❌ 示例数据插入失败")
    
    # 步骤3: 初始化权限
    print("\n📋 步骤 3/4: 初始化产品管理权限")
    print("-" * 40)
    if init_product_permissions():
        success_count += 1
        print("✅ 权限初始化成功")
    else:
        print("❌ 权限初始化失败")
    
    # 步骤4: 分配管理员权限
    print("\n📋 步骤 4/4: 为管理员分配权限")
    print("-" * 40)
    if assign_permissions_to_admin():
        success_count += 1
        print("✅ 管理员权限分配成功")
    else:
        print("❌ 管理员权限分配失败")
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 初始化完成总结")
    print("=" * 60)
    print(f"✅ 成功完成: {success_count}/{total_steps} 个步骤")
    
    if success_count == total_steps:
        print("\n🎉 产品管理模块初始化完全成功！")
        print("\n📚 模块功能说明：")
        print("  • 产品分类管理：管理增值产品和代理记账产品的分类")
        print("  • 产品项目管理：管理具体的产品项目和报价")
        print("  • 产品步骤管理：管理产品执行的详细步骤和费用")
        
        print("\n🔗 访问路径：")
        print("  • 产品分类管理：/product-categories")
        print("  • 产品项目管理：/products")
        
        print("\n🔐 权限说明：")
        print("  • product_category:read/create/update/delete - 产品分类权限")
        print("  • product:read/create/update/delete - 产品项目权限")
        print("  • product_step:read/create/update/delete - 产品步骤权限")
        
        print("\n📝 下一步操作：")
        print("  1. 重启后端服务以加载新的API路由")
        print("  2. 重新登录前端系统以获取最新权限")
        print("  3. 在左侧菜单中找到'产品管理'模块")
        print("  4. 根据需要为其他角色分配产品管理权限")
        
        print("\n💡 使用建议：")
        print("  • 先创建产品分类，再创建具体产品项目")
        print("  • 为每个产品项目配置详细的执行步骤")
        print("  • 合理设置产品报价和预估工时")
        print("  • 定期维护产品信息以保持准确性")
        
    else:
        print("\n⚠️  部分步骤失败，请检查错误信息并重新运行")
        print("💡 您也可以单独运行失败的步骤：")
        print("  • python create_product_tables.py")
        print("  • python init_product_permissions.py")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
