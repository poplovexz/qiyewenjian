#!/usr/bin/env python3
"""
审核流程配置数据迁移脚本
将审核人从角色（approver_role）迁移到用户（approver_user_id）

使用方法：
1. 查看需要迁移的数据：python3 migrate_workflow_approver_to_user.py --dry-run
2. 执行迁移：python3 migrate_workflow_approver_to_user.py
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 角色到用户的映射
# 这里需要根据实际情况配置
ROLE_TO_USER_MAP = {
    "admin": None,  # 将在运行时查询管理员用户
    "manager": None,
    "supervisor": None,
}

def get_admin_user_id(session):
    """获取管理员用户ID"""
    result = session.execute(
        text("""
        SELECT y.id, y.yonghu_ming, y.xingming
        FROM yonghu y
        JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
        JOIN jiaose j ON yj.jiaose_id = j.id
        WHERE j.jiaose_bianma = 'admin'
        AND y.is_deleted = 'N'
        AND j.is_deleted = 'N'
        LIMIT 1
        """)
    ).fetchone()
    
    if result:
        return result[0], result[1], result[2]
    return None, None, None

def migrate_workflow_templates(session, dry_run=False):
    """迁移工作流模板配置"""
    print("\n" + "=" * 60)
    print("审核流程配置数据迁移")
    print("=" * 60)
    
    # 获取管理员用户
    admin_id, admin_username, admin_name = get_admin_user_id(session)
    if admin_id:
        print(f"\n✅ 找到管理员用户: {admin_name}（{admin_username}）- ID: {admin_id}")
        ROLE_TO_USER_MAP["admin"] = admin_id
    else:
        print("\n⚠️  警告：未找到管理员用户，admin 角色将无法迁移")
    
    # 查询所有工作流模板
    result = session.execute(
        text("""
        SELECT id, guize_mingcheng, shenhe_liucheng_peizhi 
        FROM shenhe_guize 
        WHERE guize_leixing = 'workflow_template' 
        AND is_deleted = 'N'
        """)
    ).fetchall()
    
    print(f"\n找到 {len(result)} 个工作流模板配置")
    print("=" * 60)
    
    migrated_count = 0
    skipped_count = 0
    
    for row in result:
        workflow_id = row[0]
        workflow_name = row[1]
        config_json = row[2]
        
        print(f"\n处理配置: {workflow_name}")
        print(f"  ID: {workflow_id}")
        
        # 解析配置
        try:
            if isinstance(config_json, str):
                config = json.loads(config_json)
            else:
                config = config_json
        except Exception as e:
            print(f"  ❌ 无法解析配置JSON: {e}")
            skipped_count += 1
            continue
        
        # 检查是否有 steps
        if "steps" not in config or not isinstance(config["steps"], list):
            print(f"  ⏭️  跳过：配置中没有 steps 字段")
            skipped_count += 1
            continue
        
        # 检查是否需要迁移
        needs_migration = False
        for step in config["steps"]:
            if "approver_role" in step and "approver_user_id" not in step:
                needs_migration = True
                break
        
        if not needs_migration:
            print(f"  ✅ 已是新格式，无需迁移")
            skipped_count += 1
            continue
        
        print(f"  🔧 需要迁移，共 {len(config['steps'])} 个步骤")
        
        # 迁移每个步骤
        migrated_steps = 0
        for i, step in enumerate(config["steps"], 1):
            approver_role = step.get("approver_role") or step.get("role")
            
            if not approver_role:
                print(f"    步骤{i}: ⏭️  跳过（没有审核人角色）")
                continue
            
            # 如果已经有 approver_user_id，跳过
            if "approver_user_id" in step and step["approver_user_id"]:
                print(f"    步骤{i}: ✅ 已有用户ID")
                continue
            
            # 查找对应的用户ID
            user_id = ROLE_TO_USER_MAP.get(approver_role)
            
            if user_id:
                step["approver_user_id"] = user_id
                print(f"    步骤{i}: ✅ {approver_role} -> {admin_name}（{admin_username}）")
                migrated_steps += 1
            else:
                print(f"    步骤{i}: ⚠️  角色 '{approver_role}' 没有对应的用户映射")
                # 保留 approver_role 字段作为兼容
        
        if migrated_steps > 0:
            if dry_run:
                print(f"  🔍 [试运行] 将更新配置（实际未执行）")
            else:
                # 更新数据库
                try:
                    session.execute(
                        text("""
                        UPDATE shenhe_guize 
                        SET shenhe_liucheng_peizhi = :config,
                            updated_at = :updated_at
                        WHERE id = :id
                        """),
                        {
                            "config": json.dumps(config, ensure_ascii=False),
                            "updated_at": datetime.now(),
                            "id": workflow_id
                        }
                    )
                    print(f"  ✅ 已更新配置")
                    migrated_count += 1
                except Exception as e:
                    print(f"  ❌ 更新失败: {e}")
                    skipped_count += 1
        else:
            print(f"  ⏭️  没有步骤需要迁移")
            skipped_count += 1
    
    if not dry_run:
        session.commit()
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)
    print(f"  总计: {len(result)} 个配置")
    print(f"  已迁移: {migrated_count} 个配置")
    print(f"  跳过: {skipped_count} 个配置")
    
    if dry_run:
        print("\n⚠️  这是试运行模式，实际数据未修改")
        print("   要执行实际迁移，请运行: python3 migrate_workflow_approver_to_user.py")
    
    return migrated_count > 0

def verify_migration(session):
    """验证迁移结果"""
    print("\n" + "=" * 60)
    print("验证迁移结果")
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
        
        print(f"\n{workflow_name}:")
        print(f"  ID: {workflow_id}")
        
        if isinstance(config_json, str):
            config = json.loads(config_json)
        else:
            config = config_json
        
        if "steps" in config:
            for i, step in enumerate(config["steps"], 1):
                approver_user_id = step.get("approver_user_id")
                approver_role = step.get("approver_role") or step.get("role")
                
                if approver_user_id:
                    print(f"  步骤{i}: ✅ 用户ID: {approver_user_id}")
                elif approver_role:
                    print(f"  步骤{i}: ⚠️  仅有角色: {approver_role}")
                else:
                    print(f"  步骤{i}: ❌ 没有审核人信息")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='迁移审核流程配置的审核人字段')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不实际修改数据')
    parser.add_argument('--verify', action='store_true', help='验证迁移结果')
    args = parser.parse_args()
    
    session = Session()
    
    try:
        if args.verify:
            verify_migration(session)
        else:
            success = migrate_workflow_templates(session, dry_run=args.dry_run)
            
            if success and not args.dry_run:
                print("\n" + "=" * 60)
                verify_migration(session)
    except Exception as e:
        session.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)

