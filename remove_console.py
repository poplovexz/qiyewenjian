#!/usr/bin/env python3
import re
from pathlib import Path

def remove_console_calls(file_path):
    """Remove console.error/warn/log calls and clean up empty lines"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove console.error/warn/log lines
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if not re.match(r'^\s*console\.(error|warn|log)\(', line):
            new_lines.append(line)

    # Remove consecutive empty lines (keep max 1)
    final_lines = []
    prev_empty = False
    for line in new_lines:
        is_empty = line.strip() == ''
        if is_empty and prev_empty:
            continue
        final_lines.append(line)
        prev_empty = is_empty

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))

def remove_print_calls(file_path):
    """Remove print() calls and clean up empty lines"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if not re.match(r'^\s*print\(', line):
            new_lines.append(line)

    # Remove consecutive empty lines
    final_lines = []
    prev_empty = False
    for line in new_lines:
        is_empty = line.strip() == ''
        if is_empty and prev_empty:
            continue
        final_lines.append(line)
        prev_empty = is_empty

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))

# Process frontend
for file_path in Path('packages/frontend/src').rglob('*.vue'):
    if 'node_modules' not in str(file_path):
        remove_console_calls(file_path)

for file_path in Path('packages/frontend/src').rglob('*.ts'):
    if 'node_modules' not in str(file_path):
        remove_console_calls(file_path)

# Process backend
for file_path in Path('packages/backend/src').rglob('*.py'):
    remove_print_calls(file_path)

print("Done!")

