#!/usr/bin/env python3
"""
修复所有Python文件中的导入路径
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """修复单个文件中的导入"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复 from src.xxx import 为 from xxx import
        content = re.sub(r'from src\.', 'from ', content)
        
        # 修复 from .....xxx import 为 from xxx import (5个点)
        content = re.sub(r'from \.\.\.\.\.([a-zA-Z_][a-zA-Z0-9_]*)', r'from \1', content)

        # 修复 from ....xxx import 为 from xxx import (4个点)
        content = re.sub(r'from \.\.\.\.([a-zA-Z_][a-zA-Z0-9_]*)', r'from \1', content)

        # 修复 from ...xxx import 为 from xxx import (3个点)
        content = re.sub(r'from \.\.\.([a-zA-Z_][a-zA-Z0-9_]*)', r'from \1', content)
        
        # 修复 from ..xxx import 为 from xxx import (2个点，但要小心处理)
        # 只修复那些明显是跨包导入的
        content = re.sub(r'from \.\.config import', 'from core.config import', content)
        content = re.sub(r'from \.\.database import', 'from core.database import', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复了 {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    src_dir = Path("src")
    
    if not src_dir.exists():
        print("❌ src 目录不存在")
        return
    
    fixed_count = 0
    total_count = 0
    
    # 遍历所有Python文件
    for py_file in src_dir.rglob("*.py"):
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print("\n📊 修复完成:")
    print(f"  - 总文件数: {total_count}")
    print(f"  - 修复文件数: {fixed_count}")
    print(f"  - 未修改文件数: {total_count - fixed_count}")

if __name__ == "__main__":
    main()
