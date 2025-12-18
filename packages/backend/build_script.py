#!/usr/bin/env python3
"""
后端构建脚本
"""
import subprocess
import sys
import shlex
from typing import List

def run_command(command: str) -> int:
    """运行命令并返回退出码（安全方式，不使用 shell=True）"""
    print(f"运行: {command}")
    # 安全修复：使用 shlex.split 解析命令，避免 shell=True
    args: List[str] = shlex.split(command)
    # PYL-W1510: 这里故意不使用 check=True，因为需要返回退出码给调用者判断
    result = subprocess.run(args, check=False)
    return result.returncode

def main():
    """主构建函数"""
    print("开始构建后端...")
    
    # 检查 Python 语法
    exit_code = run_command("python -m py_compile src/main.py")
    if exit_code != 0:
        print("Python 语法检查失败")
        return exit_code
    
    # 运行类型检查
    exit_code = run_command("mypy src/ --ignore-missing-imports")
    if exit_code != 0:
        print("类型检查失败")
        return exit_code
    
    # 运行代码格式检查
    exit_code = run_command("black --check src/")
    if exit_code != 0:
        print("代码格式检查失败，运行 'black src/' 来修复")
        return exit_code
    
    print("后端构建成功！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
