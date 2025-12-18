#!/usr/bin/env python3
"""
修复审核流程模板数据
为缺少 steps 字段的工作流模板添加完整的步骤配置
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def fix_workflow_template_data():
    """修复工作流模板数据"""
    session = Session()
    
    try:
        # 查询所有 workflow_template 类型的配置
        result = session.execute(
            text("""
            SELECT id, guize_mingcheng, shenhe_liucheng_peizhi 
            FROM shenhe_guize 
            WHERE guize_leixing = 'workflow_template' 
            AND is_deleted = 'N'
            """)
        ).fetchall()
        
        print(f"找到 {len(result)} 个工作流模板配置")
        print("=" * 60)
        
        fixed_count = 0
        
        for row in result:
            workflow_id = row[0]
            workflow_name = row[1]
            config_json = row[2]
            
            print(f"\n检查配置: {workflow_name} ({workflow_id})")
            
            # 解析配置
            try:
                if isinstance(config_json, str):
                    config = json.loads(config_json)
                else:
                    config = config_json
            except:
                print("  ❌ 无法解析配置JSON")
                continue
            
            # 检查是否有 steps 字段
            if "steps" in config and isinstance(config["steps"], list) and len(config["steps"]) > 0:
                print(f"  ✅ 配置完整，包含 {len(config['steps'])} 个步骤")
                continue
            
            print("  ⚠️  配置不完整，缺少 steps 字段")
            print("  🔧 添加默认步骤配置...")
            
            # 添加默认的步骤配置
            config["steps"] = [
                {
                    "step_name": "管理员审核",
                    "step_order": 1,
                    "approver_role": "admin",
                    "description": "管理员审核合同金额修正",
                    "expected_time": 24,
                    "is_required": True
                }
            ]
            
            # 更新数据库
            session.execute(
                text("""
                UPDATE shenhe_guize 
                SET shenhe_liucheng_peizhi = :config,
                    updated_at = :updated_at
                WHERE id = :id
                """),
                {
                    "config": json.dumps(config),
                    "updated_at": datetime.now(),
                    "id": workflow_id
                }
            )
            
            fixed_count += 1
            print("  ✅ 已修复")
        
        session.commit()
        
        print("\n" + "=" * 60)
        print("✅ 修复完成！")
        print(f"   总计: {len(result)} 个配置")
        print(f"   修复: {fixed_count} 个配置")
        print(f"   完整: {len(result) - fixed_count} 个配置")
        
        # 验证修复结果
        print("\n" + "=" * 60)
        print("验证修复结果:")
        print("=" * 60)
        
        result = session.execute(
            text("""
            SELECT id, guize_mingcheng, shenhe_liucheng_peizhi 
            FROM shenhe_guize 
            WHERE guize_leixing = 'workflow_template' 
            AND is_deleted = 'N'
            """)
        ).fetchall()
        
        for row in result:
            workflow_id = row[0]
            workflow_name = row[1]
            config_json = row[2]
            
            if isinstance(config_json, str):
                config = json.loads(config_json)
            else:
                config = config_json
            
            steps_count = len(config.get("steps", []))
            print(f"\n{workflow_name}:")
            print(f"  ID: {workflow_id}")
            print(f"  步骤数: {steps_count}")
            
            if steps_count > 0:
                for i, step in enumerate(config["steps"], 1):
                    print(f"  步骤{i}: {step.get('step_name', '未命名')} - {step.get('approver_role', '未指定')}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("修复审核流程模板数据")
    print("=" * 60)
    
    success = fix_workflow_template_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 所有配置已修复！")
        print("=" * 60)
        print("\n现在可以访问审核流程配置页面：")
        print("http://localhost:5174/audit/workflow-config")
        print("\n应该能看到完整的配置信息，包括审核步骤。")
    else:
        print("\n" + "=" * 60)
        print("❌ 修复失败！")
        print("=" * 60)
        sys.exit(1)

