#!/usr/bin/env python3
"""Git commit helper"""
import subprocess
import sys
import os

os.chdir('/var/www')

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='/var/www', check=False)
    return result.stdout + result.stderr

# Add all changes
print("Adding changes...")
out = run_cmd(['git', 'add', '-A'])
if out.strip():
    print(out)

# Show status
print("\nStatus:")
status = run_cmd(['git', 'status', '--short'])
print(status if status.strip() else "No changes")

# Show diff names
print("\nChanged files:")
diff = run_cmd(['git', 'diff', '--cached', '--name-only'])
print(diff if diff.strip() else "No staged changes")

# Commit
if diff.strip():
    print("\nCommitting...")
    commit_msg = """fix: 修复 DeepSource Bug Risk 问题 (第二轮)

Bug Risk 修复:
- PYL-W0404: 修复重复导入 (jiaose_quanxian.py, yonghu_jiaose.py)
- FLK-E722: 修复裸except (audit_workflow_service.py, shenhe_guize_service.py, verify_customer_management_complete.py)
- PTC-W0063: 修复 next() 缺少默认值 (check_quotes.py, test_hetong_stage2.py, test_contract_workflow.py)
- FLK-F402: 修复循环变量覆盖导入 (xiansuo_baojia_service.py)
- PYL-E0602: 修复未定义变量 YonghuJiaose (approval_matrix.py)"""

    result = run_cmd(['git', 'commit', '-m', commit_msg])
    print(result)

    # Push
    print("\nPushing...")
    result = run_cmd(['git', 'push', 'origin', 'main'])
    print(result)
else:
    print("\nNo changes to commit")

