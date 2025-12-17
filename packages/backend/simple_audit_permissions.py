#!/usr/bin/env python3
"""
简化版审核权限初始化脚本
"""
import sys
import os
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from src.core.config import settings
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        print("🚀 开始初始化审核权限...")
        
        # 创建数据库连接
        engine = create_engine(str(settings.DATABASE_URL))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 定义审核权限
        audit_permissions = [
            ("审核管理菜单", "audit_menu", "访问审核管理菜单的权限", "menu", "/audit"),
            ("审核任务管理", "audit_manage", "管理审核任务的权限", "menu", "/audit/tasks"),
            ("审核流程配置", "audit_config", "配置审核流程的权限", "menu", "/audit/workflow-config"),
            ("审核规则配置", "audit_rule_config", "配置审核规则的权限", "menu", "/audit/rule-config"),
            ("查看审核任务", "audit:read", "查看审核任务列表和详情的权限", "api", "/api/v1/audit/tasks"),
            ("处理审核任务", "audit:process", "处理审核任务的权限", "api", "/api/v1/audit/process"),
            ("合同审核", "contract_audit", "审核合同的权限", "api", "/api/v1/contracts/audit"),
            ("报价审核", "quote_audit", "审核报价的权限", "api", "/api/v1/quotes/audit"),
        ]
        
        # 创建权限
        for perm_data in audit_permissions:
            quanxian_ming, quanxian_bianma, miaoshu, ziyuan_leixing, ziyuan_lujing = perm_data
            
            # 检查权限是否已存在
            result = db.execute(text(
                "SELECT id FROM quanxian WHERE quanxian_bianma = :code"
            ), {"code": quanxian_bianma}).fetchone()
            
            if not result:
                # 创建新权限
                permission_id = str(uuid.uuid4())
                db.execute(text("""
                    INSERT INTO quanxian (
                        id, quanxian_ming, quanxian_bianma, miaoshu,
                        ziyuan_leixing, ziyuan_lujing, zhuangtai,
                        created_by, created_at, updated_at, is_deleted
                    ) VALUES (
                        :id, :ming, :bianma, :miaoshu,
                        :leixing, :lujing, 'active',
                        'system', NOW(), NOW(), 'N'
                    )
                """), {
                    "id": permission_id,
                    "ming": quanxian_ming,
                    "bianma": quanxian_bianma,
                    "miaoshu": miaoshu,
                    "leixing": ziyuan_leixing,
                    "lujing": ziyuan_lujing
                })
                print(f"✅ 创建权限: {quanxian_ming} ({quanxian_bianma})")
            else:
                print(f"⚪ 权限已存在: {quanxian_ming} ({quanxian_bianma})")
        
        # 为管理员角色分配权限
        print("\n🔧 为管理员角色分配审核权限...")
        
        # 查找管理员角色
        admin_role = db.execute(text("""
            SELECT id FROM jiaose 
            WHERE jiaose_ming IN ('系统管理员', 'admin') 
            OR jiaose_bianma = 'admin'
            LIMIT 1
        """)).fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            print(f"找到管理员角色ID: {admin_role_id}")
            
            # 获取所有审核权限
            audit_perms = db.execute(text("""
                SELECT id, quanxian_ming FROM quanxian
                WHERE quanxian_bianma LIKE '%audit%' AND zhuangtai = 'active'
            """)).fetchall()
            
            for perm in audit_perms:
                perm_id, perm_name = perm
                
                # 检查是否已分配
                existing = db.execute(text("""
                    SELECT id FROM jiaose_quanxian 
                    WHERE jiaose_id = :role_id AND quanxian_id = :perm_id
                """), {"role_id": admin_role_id, "perm_id": perm_id}).fetchone()
                
                if not existing:
                    # 分配权限
                    db.execute(text("""
                        INSERT INTO jiaose_quanxian (
                            id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted
                        ) VALUES (
                            :id, :role_id, :perm_id, 'system', NOW(), NOW(), 'N'
                        )
                    """), {
                        "id": str(uuid.uuid4()),
                        "role_id": admin_role_id,
                        "perm_id": perm_id
                    })
                    print(f"  ✅ 分配权限: {perm_name}")
                else:
                    print(f"  ⚪ 权限已存在: {perm_name}")
        else:
            print("❌ 未找到管理员角色")
        
        # 更新一些常用权限为中文名称
        print("\n🔄 更新权限为中文名称...")
        
        chinese_mappings = {
            "user:read": "查看用户",
            "user:create": "创建用户",
            "user:update": "编辑用户", 
            "user:delete": "删除用户",
            "customer:read": "查看客户",
            "customer:create": "创建客户",
            "customer:update": "编辑客户",
            "customer:delete": "删除客户",
            "contract_manage": "合同管理",
            "contract:read": "查看合同",
            "contract:create": "创建合同",
            "contract:update": "编辑合同",
            "xiansuo:read": "查看线索",
            "xiansuo:create": "创建线索",
            "xiansuo:update": "编辑线索",
            "product:read": "查看产品",
            "finance_manage": "财务管理",
        }
        
        for code, chinese_name in chinese_mappings.items():
            result = db.execute(text("""
                UPDATE quanxian 
                SET quanxian_ming = :chinese_name, updated_at = NOW()
                WHERE quanxian_bianma = :code
            """), {"chinese_name": chinese_name, "code": code})
            
            if result.rowcount > 0:
                print(f"  ✅ 更新: {code} -> {chinese_name}")
        
        db.commit()
        print("\n🎉 审核权限初始化完成！")
        
        # 显示当前所有权限
        print("\n📋 当前所有权限列表:")
        all_perms = db.execute(text("""
            SELECT quanxian_ming, quanxian_bianma, ziyuan_leixing 
            FROM quanxian 
            WHERE zhuangtai = 'active' 
            ORDER BY ziyuan_leixing, quanxian_ming
        """)).fetchall()
        
        current_type = None
        for perm in all_perms:
            perm_name, perm_code, resource_type = perm
            if resource_type != current_type:
                current_type = resource_type
                print(f"\n  📁 {resource_type.upper()}:")
            print(f"    - {perm_name} ({perm_code})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if main():
        print("\n✅ 脚本执行成功！")
    else:
        print("\n❌ 脚本执行失败！")
        sys.exit(1)
