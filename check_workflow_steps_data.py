#!/usr/bin/env python3
"""
检查审核流程步骤数据结构
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from core.config import settings
import json

def check_workflow_steps():
    """检查审核流程步骤数据"""
    print("="*60)
    print("检查审核流程步骤数据结构")
    print("="*60)

    # 转换 Pydantic URL 为字符串
    db_url = str(settings.DATABASE_URL)
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # 查询工作流模板
        result = conn.execute(text("""
            SELECT 
                id,
                guize_mingcheng,
                guize_leixing,
                shenhe_liucheng_peizhi,
                created_at
            FROM shenhe_guize
            WHERE guize_leixing = 'workflow_template'
              AND is_deleted = 'N'
            ORDER BY created_at DESC
            LIMIT 5
        """))
        
        workflows = result.fetchall()
        
        if not workflows:
            print("\n❌ 没有找到工作流模板数据")
            return
        
        print(f"\n✅ 找到 {len(workflows)} 个工作流模板\n")
        
        for idx, workflow in enumerate(workflows, 1):
            print(f"{'='*60}")
            print(f"工作流 {idx}")
            print(f"{'='*60}")
            print(f"ID: {workflow[0]}")
            print(f"名称: {workflow[1]}")
            print(f"类型: {workflow[2]}")
            print(f"创建时间: {workflow[4]}")
            
            # 解析步骤配置
            try:
                steps_config = json.loads(workflow[3])
                steps = steps_config.get('steps', [])
                
                print(f"\n步骤配置 (共 {len(steps)} 个步骤):")
                print("-" * 60)
                
                for step_idx, step in enumerate(steps, 1):
                    print(f"\n步骤 {step_idx}:")
                    print(f"  字段结构:")
                    for key, value in step.items():
                        print(f"    - {key}: {value}")
                    
                    # 检查字段名
                    has_name = 'name' in step
                    has_step_name = 'step_name' in step
                    has_role = 'role' in step
                    has_approver_role = 'approver_role' in step
                    
                    print(f"\n  字段检查:")
                    print(f"    ✅ 'name' 字段: {'存在' if has_name else '❌ 不存在'}")
                    print(f"    {'✅' if has_step_name else '  '} 'step_name' 字段: {'存在' if has_step_name else '不存在'}")
                    print(f"    ✅ 'role' 字段: {'存在' if has_role else '❌ 不存在'}")
                    print(f"    {'✅' if has_approver_role else '  '} 'approver_role' 字段: {'存在' if has_approver_role else '不存在'}")
                    
                    # 给出建议
                    if has_name and has_role:
                        print(f"\n  ✅ 数据格式正确（使用 name 和 role）")
                    elif has_step_name and has_approver_role:
                        print(f"\n  ⚠️  数据格式使用旧字段名（step_name 和 approver_role）")
                    else:
                        print(f"\n  ❌ 数据格式异常，字段不完整")
                
            except json.JSONDecodeError as e:
                print(f"\n❌ 解析步骤配置失败: {e}")
            except Exception as e:
                print(f"\n❌ 处理步骤配置时出错: {e}")
            
            print()
    
    print("="*60)
    print("检查完成")
    print("="*60)
    print("\n📋 说明:")
    print("  - 后端存储使用: 'name' 和 'role'")
    print("  - 前端期望: 'step_name' 和 'approver_role'")
    print("  - 修复方案: 前端兼容两种字段名")
    print("\n🔧 如果看到字段不存在的情况:")
    print("  1. 前端已修复为兼容模式")
    print("  2. 清除浏览器缓存")
    print("  3. 重新测试编辑功能")

if __name__ == "__main__":
    try:
        check_workflow_steps()
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

