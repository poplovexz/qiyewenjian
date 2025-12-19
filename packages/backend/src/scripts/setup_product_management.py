"""
产品管理模块一键初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from create_product_tables import create_product_tables, insert_sample_data
from init_product_permissions import init_product_permissions, assign_permissions_to_admin


def main():
    """主函数 - 一键初始化产品管理模块"""
    
    success_count = 0
    total_steps = 4
    
    # 步骤1: 创建数据表
    if create_product_tables():
        success_count += 1
    else:
    
    # 步骤2: 插入示例数据
    if insert_sample_data():
        success_count += 1
    else:
    
    # 步骤3: 初始化权限
    if init_product_permissions():
        success_count += 1
    else:
    
    # 步骤4: 分配管理员权限
    if assign_permissions_to_admin():
        success_count += 1
    else:
    
    # 总结
    
    if success_count == total_steps:
        
        
        
        
        
    else:
    


if __name__ == "__main__":
    main()
