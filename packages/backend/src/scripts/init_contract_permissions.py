#!/usr/bin/env python3
"""
初始化合同模板管理权限
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.yonghu_guanli import Quanxian, Jiaose, JiaoseQuanxian


def init_contract_permissions():
    """初始化合同模板管理权限"""
    db: Session = SessionLocal()
    
    try:
        # 合同模板管理权限列表
        contract_permissions = [
            # 合同模板基础权限
            {
                "quanxian_bianma": "contract_template:read",
                "quanxian_ming": "查看合同模板",
                "miaoshu": "查看合同模板列表和详情",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:create",
                "quanxian_ming": "创建合同模板",
                "miaoshu": "创建新的合同模板",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:update",
                "quanxian_ming": "编辑合同模板",
                "miaoshu": "编辑和更新合同模板信息",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:delete",
                "quanxian_ming": "删除合同模板",
                "miaoshu": "删除合同模板",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            
            # 合同模板功能权限
            {
                "quanxian_bianma": "contract_template:preview",
                "quanxian_ming": "预览合同模板",
                "miaoshu": "预览合同模板内容",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:export",
                "quanxian_ming": "导出合同模板",
                "miaoshu": "导出合同模板文件",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:approve",
                "quanxian_ming": "审批合同模板",
                "miaoshu": "审批合同模板的启用和修改",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            },
            
            # 合同模板界面权限
            {
                "quanxian_bianma": "contract_template:menu",
                "quanxian_ming": "合同模板菜单",
                "miaoshu": "访问合同模板管理菜单",
                "ziyuan_leixing": "menu",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:create_button",
                "quanxian_ming": "新建模板按钮",
                "miaoshu": "显示新建合同模板按钮",
                "ziyuan_leixing": "button",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:edit_button",
                "quanxian_ming": "编辑模板按钮",
                "miaoshu": "显示编辑合同模板按钮",
                "ziyuan_leixing": "button",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:delete_button",
                "quanxian_ming": "删除模板按钮",
                "miaoshu": "显示删除合同模板按钮",
                "ziyuan_leixing": "button",
                "zhuangtai": "active"
            },
            {
                "quanxian_bianma": "contract_template:status_button",
                "quanxian_ming": "合同模板状态管理按钮",
                "miaoshu": "显示合同模板状态管理按钮",
                "ziyuan_leixing": "button",
                "zhuangtai": "active"
            },
            
            # 合同模板管理权限
            {
                "quanxian_bianma": "contract_template_manage",
                "quanxian_ming": "合同模板管理",
                "miaoshu": "合同模板管理模块总权限",
                "ziyuan_leixing": "api",
                "zhuangtai": "active"
            }
        ]
        
        print("开始初始化合同模板管理权限...")
        
        # 创建权限
        created_permissions = []
        for perm_data in contract_permissions:
            # 检查权限是否已存在
            existing_permission = db.query(Quanxian).filter(
                Quanxian.quanxian_bianma == perm_data["quanxian_bianma"]
            ).first()
            
            if not existing_permission:
                permission = Quanxian(**perm_data)
                db.add(permission)
                created_permissions.append(perm_data["quanxian_bianma"])
                print(f"创建权限: {perm_data['quanxian_ming']} ({perm_data['quanxian_bianma']})")
            else:
                print(f"权限已存在: {perm_data['quanxian_ming']} ({perm_data['quanxian_bianma']})")
        
        db.commit()
        
        # 为管理员角色分配权限
        admin_role = db.query(Jiaose).filter(Jiaose.jiaose_bianma == "admin").first()
        if admin_role:
            print("\n为管理员角色分配合同模板管理权限...")
            
            # 获取所有合同模板相关权限
            contract_permissions_db = db.query(Quanxian).filter(
                Quanxian.quanxian_bianma.like("contract_template%")
            ).all()
            
            for permission in contract_permissions_db:
                # 检查角色权限关联是否已存在
                existing_role_permission = db.query(JiaoseQuanxian).filter(
                    JiaoseQuanxian.jiaose_id == admin_role.id,
                    JiaoseQuanxian.quanxian_id == permission.id
                ).first()
                
                if not existing_role_permission:
                    role_permission = JiaoseQuanxian(
                        jiaose_id=admin_role.id,
                        quanxian_id=permission.id
                    )
                    db.add(role_permission)
                    print(f"  分配权限: {permission.quanxian_ming}")
                else:
                    print(f"  权限已分配: {permission.quanxian_ming}")
            
            db.commit()
        else:
            print("警告: 未找到管理员角色")
        
        print("\n合同模板管理权限初始化完成!")
        print(f"新创建权限数量: {len(created_permissions)}")
        print(f"总权限数量: {len(contract_permissions)}")
        
    except Exception as e:
        print(f"初始化权限时发生错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_contract_permissions()
