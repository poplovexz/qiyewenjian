#!/usr/bin/env python3
"""提交 git 修改"""
import subprocess
import os

os.chdir('/var/www')

# 获取 git status
result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
if result.stdout.strip():
    print("=== 未提交的修改 ===")
    print(result.stdout)

    # 添加所有修改
    subprocess.run(['git', 'add', '-A'], check=True)

    # 提交
    commit_msg = """fix: 修复 DeepSource 漏洞风险和反模式问题

Bug Risk 修复:
- PYL-E0602: 修复未定义变量名 (kaipiao.py, hetong_qianshu.py)
- PYL-R1722: exit() 改为 sys.exit() (9个文件)
- PYL-W1510: subprocess.run 添加 check=False (12个位置)
- PTC-W0063: next() 添加默认值防止 StopIteration (9个位置)

Anti-pattern 修复:
- FLK-E722: 裸 except 指定异常类型 (7个文件)
- PYL-W0404: 修复重复导入 (test_yonghu_service.py)"""

    result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
    print("=== 提交结果 ===")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # 推送
    result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
    print("=== 推送结果 ===")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
else:
    print("没有未提交的修改")

# 获取最近的提交
result2 = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
print("\n=== 最近5次提交 ===")
print(result2.stdout)

