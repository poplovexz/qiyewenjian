"""
初始化客户管理模块权限
"""
import sys
import os
import uuid
from sqlalchemy.orm import Session

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models.yonghu_guanli import Quanxian

def init_customer_permissions():
    """初始化客户管理模块权限"""
    db: Session = SessionLocal()
    
    try:
        # 客户管理权限列表
        customer_permissions = [
            # 菜单权限
            {
                "quanxian_ming": "客户管理菜单",
                "quanxian_bianma": "customer:menu",
                "miaoshu": "访问客户管理菜单的权限",
                "ziyuan_leixing": "menu",
                "ziyuan_lujing": "/customers",
                "zhuangtai": "active"
            },
            
            # 客户基础权限
            {
                "quanxian_ming": "查看客户",
                "quanxian_bianma": "customer:read",
                "miaoshu": "查看客户信息的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/customers/*",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "创建客户",
                "quanxian_bianma": "customer:create",
                "miaoshu": "创建新客户的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/customers/",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "编辑客户",
                "quanxian_bianma": "customer:update",
                "miaoshu": "编辑客户信息的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/customers/*",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "删除客户",
                "quanxian_bianma": "customer:delete",
                "miaoshu": "删除客户的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/customers/*",
                "zhuangtai": "active"
            },
            
            # 客户状态管理权限
            {
                "quanxian_ming": "管理客户状态",
                "quanxian_bianma": "customer:status_manage",
                "miaoshu": "管理客户状态（活跃、续约中、已终止）的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/customers/*/status",
                "zhuangtai": "active"
            },
            
            # 服务记录权限
            {
                "quanxian_ming": "查看服务记录",
                "quanxian_bianma": "service_record:read",
                "miaoshu": "查看客户服务记录的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/service-records/*",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "创建服务记录",
                "quanxian_bianma": "service_record:create",
                "miaoshu": "创建客户服务记录的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/service-records/",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "编辑服务记录",
                "quanxian_bianma": "service_record:update",
                "miaoshu": "编辑客户服务记录的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/service-records/*",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "删除服务记录",
                "quanxian_bianma": "service_record:delete",
                "miaoshu": "删除客户服务记录的权限",
                "ziyuan_leixing": "api",
                "ziyuan_lujing": "/api/v1/service-records/*",
                "zhuangtai": "active"
            },
            
            # 按钮权限
            {
                "quanxian_ming": "新增客户按钮",
                "quanxian_bianma": "customer:create_button",
                "miaoshu": "显示新增客户按钮的权限",
                "ziyuan_leixing": "button",
                "ziyuan_lujing": "customer-create-btn",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "编辑客户按钮",
                "quanxian_bianma": "customer:edit_button",
                "miaoshu": "显示编辑客户按钮的权限",
                "ziyuan_leixing": "button",
                "ziyuan_lujing": "customer-edit-btn",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "删除客户按钮",
                "quanxian_bianma": "customer:delete_button",
                "miaoshu": "显示删除客户按钮的权限",
                "ziyuan_leixing": "button",
                "ziyuan_lujing": "customer-delete-btn",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "状态管理按钮",
                "quanxian_bianma": "customer:status_button",
                "miaoshu": "显示客户状态管理按钮的权限",
                "ziyuan_leixing": "button",
                "ziyuan_lujing": "customer-status-btn",
                "zhuangtai": "active"
            },
            {
                "quanxian_ming": "服务记录按钮",
                "quanxian_bianma": "service_record:manage_button",
                "miaoshu": "显示服务记录管理按钮的权限",
                "ziyuan_leixing": "button",
                "ziyuan_lujing": "service-record-btn",
                "zhuangtai": "active"
            }
        ]
        
        # 检查并创建权限
        for perm_data in customer_permissions:
            # 检查权限是否已存在
            existing_permission = db.query(Quanxian).filter(
                Quanxian.quanxian_bianma == perm_data["quanxian_bianma"]
            ).first()
            
            if not existing_permission:
                # 创建新权限
                permission = Quanxian(
                    id=str(uuid.uuid4()),
                    created_by="system",
                    **perm_data
                )
                db.add(permission)
            else:
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_customer_permissions()
