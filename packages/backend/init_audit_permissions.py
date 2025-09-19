#!/usr/bin/env python3
"""
初始化审核管理模块权限
"""
import sys
import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import settings

def init_audit_permissions():
    """初始化审核管理模块权限"""

    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 开始初始化审核管理模块权限...")
        
        # 定义审核管理权限
        audit_permissions = [
            # 菜单权限
            ("审核管理菜单", "audit_menu", "访问审核管理菜单的权限", "menu", "/audit"),
            
            # 审核任务权限
            ("审核任务管理", "audit_manage", "管理审核任务的权限", "menu", "/audit/tasks"),
            ("查看审核任务", "audit:read", "查看审核任务列表和详情的权限", "api", "/api/v1/audit/tasks"),
            ("处理审核任务", "audit:process", "处理审核任务的权限", "api", "/api/v1/audit/process"),
            ("审核任务统计", "audit:statistics", "查看审核任务统计的权限", "api", "/api/v1/audit/statistics"),
            
            # 审核流程配置权限
            ("审核流程配置", "audit_config", "配置审核流程的权限", "menu", "/audit/workflow-config"),
            ("查看审核流程", "audit_workflow:read", "查看审核流程配置的权限", "api", "/api/v1/audit/workflows"),
            ("创建审核流程", "audit_workflow:create", "创建审核流程的权限", "api", "/api/v1/audit/workflows"),
            ("编辑审核流程", "audit_workflow:update", "编辑审核流程的权限", "api", "/api/v1/audit/workflows"),
            ("删除审核流程", "audit_workflow:delete", "删除审核流程的权限", "api", "/api/v1/audit/workflows"),
            
            # 审核规则配置权限
            ("审核规则配置", "audit_rule_config", "配置审核规则的权限", "menu", "/audit/rule-config"),
            ("查看审核规则", "audit_rule:read", "查看审核规则配置的权限", "api", "/api/v1/audit/rules"),
            ("创建审核规则", "audit_rule:create", "创建审核规则的权限", "api", "/api/v1/audit/rules"),
            ("编辑审核规则", "audit_rule:update", "编辑审核规则的权限", "api", "/api/v1/audit/rules"),
            ("删除审核规则", "audit_rule:delete", "删除审核规则的权限", "api", "/api/v1/audit/rules"),
            
            # 合同审核权限
            ("合同审核", "contract_audit", "审核合同的权限", "api", "/api/v1/contracts/audit"),
            ("合同审核历史", "contract_audit_history", "查看合同审核历史的权限", "api", "/api/v1/contracts/audit-history"),
            
            # 报价审核权限
            ("报价审核", "quote_audit", "审核报价的权限", "api", "/api/v1/quotes/audit"),
            ("报价审核历史", "quote_audit_history", "查看报价审核历史的权限", "api", "/api/v1/quotes/audit-history"),
            
            # 审核记录权限
            ("审核记录查看", "audit_record:read", "查看审核记录的权限", "api", "/api/v1/audit/records"),
            ("审核记录创建", "audit_record:create", "创建审核记录的权限", "api", "/api/v1/audit/records"),
            ("审核记录更新", "audit_record:update", "更新审核记录的权限", "api", "/api/v1/audit/records"),
            
            # 按钮权限
            ("审核通过按钮", "audit:approve_button", "显示审核通过按钮的权限", "button", "audit-approve-btn"),
            ("审核拒绝按钮", "audit:reject_button", "显示审核拒绝按钮的权限", "button", "audit-reject-btn"),
            ("审核转派按钮", "audit:transfer_button", "显示审核转派按钮的权限", "button", "audit-transfer-btn"),
            ("新建流程按钮", "audit_workflow:create_button", "显示新建审核流程按钮的权限", "button", "workflow-create-btn"),
            ("新建规则按钮", "audit_rule:create_button", "显示新建审核规则按钮的权限", "button", "rule-create-btn"),
        ]
        
        # 检查并创建权限
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
        
        db.commit()
        print("\n✅ 审核管理模块权限初始化完成！")
        
        # 为管理员角色分配所有审核权限
        print("\n🔧 为管理员角色分配审核管理权限...")

        # 获取管理员角色ID
        admin_role = db.execute(text(
            "SELECT id FROM jiaose WHERE jiaose_ming = '系统管理员' OR jiaose_ming = 'admin' OR jiaose_bianma = 'admin'"
        )).fetchone()

        if admin_role:
            admin_role_id = admin_role[0]
            
            # 获取所有审核管理权限
            audit_perms = db.execute(text("""
                SELECT id, quanxian_ming FROM quanxian
                WHERE (quanxian_bianma LIKE 'audit%' OR quanxian_bianma LIKE '%audit%') 
                AND zhuangtai = 'active'
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
                    print(f"  ✅ 为管理员分配权限: {perm_name}")
                else:
                    print(f"  ⚪ 管理员已有权限: {perm_name}")
            
            db.commit()
            print("🎉 管理员审核权限分配完成！")
        else:
            print("❌ 未找到管理员角色")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化权限失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def update_permissions_to_chinese():
    """将现有权限更新为中文标识"""

    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n🔄 开始更新权限为中文标识...")
        
        # 定义权限映射（英文编码 -> 中文名称）
        permission_mappings = {
            # 用户管理
            "user:read": "查看用户",
            "user:create": "创建用户", 
            "user:update": "编辑用户",
            "user:delete": "删除用户",
            "role:read": "查看角色",
            "role:create": "创建角色",
            "role:update": "编辑角色", 
            "role:delete": "删除角色",
            
            # 客户管理
            "customer:read": "查看客户",
            "customer:create": "创建客户",
            "customer:update": "编辑客户",
            "customer:delete": "删除客户",
            "customer_manage": "客户管理",
            
            # 线索管理
            "xiansuo:read": "查看线索",
            "xiansuo:create": "创建线索",
            "xiansuo:update": "编辑线索",
            "xiansuo:delete": "删除线索",
            "xiansuo:assign": "分配线索",
            "xiansuo:followup": "线索跟进",
            
            # 合同管理
            "contract_manage": "合同管理",
            "contract:read": "查看合同",
            "contract:create": "创建合同",
            "contract:update": "编辑合同",
            "contract:delete": "删除合同",
            "contract_template_manage": "合同模板管理",
            
            # 产品管理
            "product:read": "查看产品",
            "product:create": "创建产品",
            "product:update": "编辑产品",
            "product:delete": "删除产品",
            
            # 财务管理
            "finance_manage": "财务管理",
            "payment:read": "查看支付",
            "payment:create": "创建支付",
            "payment:update": "编辑支付",
        }
        
        # 更新现有权限名称
        for code, chinese_name in permission_mappings.items():
            result = db.execute(text("""
                UPDATE quanxian 
                SET quanxian_ming = :chinese_name, updated_at = NOW()
                WHERE quanxian_bianma = :code
            """), {"chinese_name": chinese_name, "code": code})
            
            if result.rowcount > 0:
                print(f"  ✅ 更新权限: {code} -> {chinese_name}")
        
        db.commit()
        print("🎉 权限中文化更新完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新权限失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化审核权限和更新权限中文化...")
    
    # 初始化审核权限
    if init_audit_permissions():
        print("✅ 审核权限初始化成功")
    else:
        print("❌ 审核权限初始化失败")
        sys.exit(1)
    
    # 更新权限为中文
    if update_permissions_to_chinese():
        print("✅ 权限中文化更新成功")
    else:
        print("❌ 权限中文化更新失败")
        sys.exit(1)
    
    print("\n🎉 所有权限配置完成！")
