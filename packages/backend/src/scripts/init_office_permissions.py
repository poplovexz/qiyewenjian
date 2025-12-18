#!/usr/bin/env python3
"""
初始化办公管理模块权限
"""
import sys
import uuid
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from core.config import settings


def init_office_permissions():
    """初始化办公管理模块权限"""
    try:
        # 创建数据库引擎
        engine = create_engine(str(settings.DATABASE_URL))
        
        with engine.connect() as db:
            print("=" * 60)
            print("办公管理模块权限初始化")
            print("=" * 60)
            
            # 定义办公管理权限
            office_permissions = [
                # 办公管理主菜单
                ("办公管理", "office_menu", "访问办公管理菜单的权限", "menu", "/office"),
                
                # 报销申请模块
                ("报销申请菜单", "office:baoxiao:menu", "访问报销申请菜单的权限", "menu", "/office/reimbursement"),
                ("查看报销申请", "office:baoxiao:read", "查看报销申请列表和详情的权限", "api", "/api/v1/office/reimbursement"),
                ("创建报销申请", "office:baoxiao:create", "创建报销申请的权限", "api", "/api/v1/office/reimbursement"),
                ("编辑报销申请", "office:baoxiao:update", "编辑报销申请的权限", "api", "/api/v1/office/reimbursement"),
                ("删除报销申请", "office:baoxiao:delete", "删除报销申请的权限", "api", "/api/v1/office/reimbursement"),
                ("提交报销审批", "office:baoxiao:submit", "提交报销申请审批的权限", "api", "/api/v1/office/reimbursement/submit"),
                ("审批报销申请", "office:baoxiao:approve", "审批报销申请的权限", "api", "/api/v1/office/reimbursement/approve"),
                
                # 请假申请模块
                ("请假申请菜单", "office:qingjia:menu", "访问请假申请菜单的权限", "menu", "/office/leave"),
                ("查看请假申请", "office:qingjia:read", "查看请假申请列表和详情的权限", "api", "/api/v1/office/leave"),
                ("创建请假申请", "office:qingjia:create", "创建请假申请的权限", "api", "/api/v1/office/leave"),
                ("编辑请假申请", "office:qingjia:update", "编辑请假申请的权限", "api", "/api/v1/office/leave"),
                ("删除请假申请", "office:qingjia:delete", "删除请假申请的权限", "api", "/api/v1/office/leave"),
                ("提交请假审批", "office:qingjia:submit", "提交请假申请审批的权限", "api", "/api/v1/office/leave/submit"),
                ("审批请假申请", "office:qingjia:approve", "审批请假申请的权限", "api", "/api/v1/office/leave/approve"),
                
                # 对外付款申请模块
                ("对外付款菜单", "office:fukuan:menu", "访问对外付款菜单的权限", "menu", "/office/payment"),
                ("查看付款申请", "office:fukuan:read", "查看对外付款申请列表和详情的权限", "api", "/api/v1/office/payment"),
                ("创建付款申请", "office:fukuan:create", "创建对外付款申请的权限", "api", "/api/v1/office/payment"),
                ("编辑付款申请", "office:fukuan:update", "编辑对外付款申请的权限", "api", "/api/v1/office/payment"),
                ("删除付款申请", "office:fukuan:delete", "删除对外付款申请的权限", "api", "/api/v1/office/payment"),
                ("提交付款审批", "office:fukuan:submit", "提交对外付款申请审批的权限", "api", "/api/v1/office/payment/submit"),
                ("审批付款申请", "office:fukuan:approve", "审批对外付款申请的权限", "api", "/api/v1/office/payment/approve"),
                ("确认付款", "office:fukuan:confirm", "确认对外付款的权限", "api", "/api/v1/office/payment/confirm"),
                
                # 采购申请模块
                ("采购申请菜单", "office:caigou:menu", "访问采购申请菜单的权限", "menu", "/office/procurement"),
                ("查看采购申请", "office:caigou:read", "查看采购申请列表和详情的权限", "api", "/api/v1/office/procurement"),
                ("创建采购申请", "office:caigou:create", "创建采购申请的权限", "api", "/api/v1/office/procurement"),
                ("编辑采购申请", "office:caigou:update", "编辑采购申请的权限", "api", "/api/v1/office/procurement"),
                ("删除采购申请", "office:caigou:delete", "删除采购申请的权限", "api", "/api/v1/office/procurement"),
                ("提交采购审批", "office:caigou:submit", "提交采购申请审批的权限", "api", "/api/v1/office/procurement/submit"),
                ("审批采购申请", "office:caigou:approve", "审批采购申请的权限", "api", "/api/v1/office/procurement/approve"),
                ("更新采购状态", "office:caigou:status", "更新采购状态的权限", "api", "/api/v1/office/procurement/status"),
                
                # 工作交接模块
                ("工作交接菜单", "office:jiaojie:menu", "访问工作交接菜单的权限", "menu", "/office/handover"),
                ("查看工作交接", "office:jiaojie:read", "查看工作交接列表和详情的权限", "api", "/api/v1/office/handover"),
                ("创建工作交接", "office:jiaojie:create", "创建工作交接的权限", "api", "/api/v1/office/handover"),
                ("编辑工作交接", "office:jiaojie:update", "编辑工作交接的权限", "api", "/api/v1/office/handover"),
                ("删除工作交接", "office:jiaojie:delete", "删除工作交接的权限", "api", "/api/v1/office/handover"),
                ("确认工作交接", "office:jiaojie:confirm", "确认工作交接的权限", "api", "/api/v1/office/handover/confirm"),
            ]
            
            # 检查并创建权限
            created_count = 0
            existing_count = 0
            
            for perm_data in office_permissions:
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
                    created_count += 1
                    print(f"✅ 创建权限: {quanxian_ming} ({quanxian_bianma})")
                else:
                    existing_count += 1
                    print(f"⚪ 权限已存在: {quanxian_ming} ({quanxian_bianma})")
            
            db.commit()
            print("\n📊 权限创建统计:")
            print(f"  - 新创建: {created_count} 个")
            print(f"  - 已存在: {existing_count} 个")
            print(f"  - 总计: {len(office_permissions)} 个")
            
            # 为管理员角色分配所有办公管理权限
            print("\n🔧 为管理员角色分配办公管理权限...")

            # 获取管理员角色ID
            admin_role = db.execute(text(
                "SELECT id FROM jiaose WHERE jiaose_ming = '系统管理员' OR jiaose_ming = 'admin' OR jiaose_bianma = 'admin'"
            )).fetchone()

            if admin_role:
                admin_role_id = admin_role[0]
                
                # 获取所有办公管理权限
                office_perms = db.execute(text("""
                    SELECT id, quanxian_ming FROM quanxian
                    WHERE (quanxian_bianma LIKE 'office%' OR quanxian_bianma = 'office_menu') 
                    AND zhuangtai = 'active'
                """)).fetchall()
                
                assigned_count = 0
                existing_assign_count = 0
                
                for perm in office_perms:
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
                        assigned_count += 1
                        print(f"  ✅ 为管理员分配权限: {perm_name}")
                    else:
                        existing_assign_count += 1
                        print(f"  ⚪ 管理员已有权限: {perm_name}")
                
                db.commit()
                print("\n📊 权限分配统计:")
                print(f"  - 新分配: {assigned_count} 个")
                print(f"  - 已分配: {existing_assign_count} 个")
                print("🎉 管理员办公管理权限分配完成！")
            else:
                print("❌ 未找到管理员角色")
            
            print("\n" + "=" * 60)
            print("✅ 办公管理模块权限初始化完成！")
            print("=" * 60)
            return True
        
    except Exception as e:
        print(f"❌ 初始化权限失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    success = init_office_permissions()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

