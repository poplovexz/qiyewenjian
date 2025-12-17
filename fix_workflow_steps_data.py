#!/usr/bin/env python3
"""
修复工作流步骤数据
将旧格式的工作流配置更新为新格式（包含steps）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from core.config import settings
import json
from datetime import datetime

def fix_workflow_steps():
    """修复工作流步骤数据"""
    print("="*60)
    print("修复工作流步骤数据")
    print("="*60)
    
    # 转换 Pydantic URL 为字符串
    db_url = str(settings.DATABASE_URL)
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        # 查找所有工作流模板
        result = conn.execute(text('''
            SELECT 
                id,
                guize_mingcheng,
                shenhe_liucheng_peizhi,
                chufa_tiaojian
            FROM shenhe_guize
            WHERE guize_leixing = 'workflow_template'
              AND is_deleted = 'N'
        '''))
        
        rows = result.fetchall()
        print(f'\n找到 {len(rows)} 个工作流模板需要检查\n')
        
        fixed_count = 0
        
        for row in rows:
            workflow_id = row[0]
            workflow_name = row[1]
            config_str = row[2]
            trigger_str = row[3]
            
            print(f'检查工作流: {workflow_name}')
            print(f'  ID: {workflow_id}')
            
            # 解析配置
            try:
                config = json.loads(config_str) if config_str else {}
                steps = config.get('steps', [])
                
                if not steps:
                    print(f'  ⚠️  没有步骤数据，需要修复')
                    
                    # 解析触发条件获取审核类型
                    try:
                        trigger_config = json.loads(trigger_str) if trigger_str else {}
                        audit_type = trigger_config.get('audit_type', 'contract')
                    except:
                        audit_type = 'contract'
                    
                    # 根据审核类型创建默认步骤
                    if audit_type == 'contract':
                        default_steps = [
                            {
                                "step": 1,
                                "name": "财务审核",
                                "role": "财务经理",
                                "description": "审核合同金额变更的合理性",
                                "expected_time": 24,
                                "is_required": True
                            },
                            {
                                "step": 2,
                                "name": "总经理审批",
                                "role": "总经理",
                                "description": "最终审批合同金额变更",
                                "expected_time": 48,
                                "is_required": True
                            }
                        ]
                    else:
                        default_steps = [
                            {
                                "step": 1,
                                "name": "主管审核",
                                "role": "部门主管",
                                "description": "初步审核",
                                "expected_time": 24,
                                "is_required": True
                            }
                        ]
                    
                    # 创建新的配置
                    new_config = {
                        "steps": default_steps
                    }
                    
                    # 更新数据库
                    conn.execute(
                        text('''
                            UPDATE shenhe_guize
                            SET shenhe_liucheng_peizhi = :config,
                                updated_at = :updated_at
                            WHERE id = :id
                        '''),
                        {
                            'config': json.dumps(new_config, ensure_ascii=False),
                            'updated_at': datetime.now(),
                            'id': workflow_id
                        }
                    )
                    
                    print(f'  ✅ 已添加 {len(default_steps)} 个默认步骤')
                    for step in default_steps:
                        print(f'     步骤{step["step"]}: {step["name"]} ({step["role"]})')
                    
                    fixed_count += 1
                else:
                    print(f'  ✅ 已有 {len(steps)} 个步骤，无需修复')
                
            except Exception as e:
                print(f'  ❌ 处理失败: {e}')
                import traceback
                traceback.print_exc()
            
            print()
        
        print("="*60)
        print(f'修复完成: 共修复 {fixed_count} 个工作流')
        print("="*60)

if __name__ == "__main__":
    try:
        fix_workflow_steps()
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()

