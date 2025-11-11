#!/usr/bin/env python3
"""
修复办公管理模块中的权限装饰器使用问题
将 @require_permission 装饰器改为 Depends(require_permission(...))
"""
import re
import sys
from pathlib import Path

def fix_permission_decorator(file_path):
    """修复单个文件中的权限装饰器"""
    print(f"处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 匹配模式：@require_permission("xxx") 后面跟着 async def 函数定义
    # 需要将装饰器移到函数参数中
    pattern = r'# @require_permission\("([^"]+)"\)\s*\n\s*async def (\w+)\((.*?)\):'
    
    def replace_func(match):
        permission = match.group(1)
        func_name = match.group(2)
        params = match.group(3)
        
        # 解析参数
        param_lines = [p.strip() for p in params.split(',') if p.strip()]
        
        # 找到 current_user 和 db 参数的位置
        new_params = []
        has_current_user = False
        has_db = False
        
        for param in param_lines:
            if 'current_user' in param:
                # 替换 current_user 参数
                new_params.append(f'current_user: Yonghu = Depends(require_permission("{permission}"))')
                has_current_user = True
            elif 'db:' in param or 'db =' in param:
                # db 参数保持不变，但要确保在 current_user 之前
                if not has_current_user:
                    new_params.append(param)
                    has_db = True
                else:
                    # db 应该在 current_user 之前
                    new_params.insert(-1, param)
                    has_db = True
            else:
                new_params.append(param)
        
        # 如果没有 current_user，添加它
        if not has_current_user:
            new_params.append(f'current_user: Yonghu = Depends(require_permission("{permission}"))')
        
        # 重新组合参数
        new_params_str = ',\n    '.join(new_params)
        
        return f'async def {func_name}(\n    {new_params_str}\n):'
    
    # 执行替换
    content = re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已修复: {file_path}")
        return True
    else:
        print(f"- 无需修复: {file_path}")
        return False

def main():
    # 要处理的文件列表
    base_dir = Path(__file__).parent / "src/api/api_v1/endpoints/bangong_guanli"
    files = [
        base_dir / "qingjia.py",
        base_dir / "duiwai_fukuan.py",
        base_dir / "caigou.py",
        base_dir / "gongzuo_jiaojie.py"
    ]
    
    fixed_count = 0
    for file_path in files:
        if file_path.exists():
            if fix_permission_decorator(file_path):
                fixed_count += 1
        else:
            print(f"✗ 文件不存在: {file_path}")
    
    print(f"\n总计修复 {fixed_count} 个文件")

if __name__ == "__main__":
    main()

