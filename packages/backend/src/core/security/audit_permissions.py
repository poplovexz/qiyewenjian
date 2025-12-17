"""
审核权限验证中间件
专门用于审核模块的权限验证和安全控制
"""
import json
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu, Jiaose, YonghuJiaose
from models.shenhe_guanli import ShenheGuize, ShenheJilu


class AuditPermissionChecker:
    """审核权限检查器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_audit_rule_permission(self, user: Yonghu, action: str, rule_id: str = None) -> bool:
        """
        检查审核规则权限
        
        Args:
            user: 当前用户
            action: 操作类型 (create, read, update, delete, test)
            rule_id: 规则ID（用于特定规则的权限检查）
            
        Returns:
            是否有权限
        """
        # 超级管理员拥有所有权限
        if user.yonghu_ming == 'admin':
            return True
        
        # 检查基础权限
        base_permission = f"audit_rule:{action}"
        if not self._has_permission(user, base_permission):
            return False
        
        # 如果是特定规则操作，检查规则级别权限
        if rule_id and action in ['update', 'delete']:
            rule = self.db.query(ShenheGuize).filter(ShenheGuize.id == rule_id).first()
            if rule:
                # 检查是否是规则创建者或有管理权限
                if rule.chuangjian_ren != user.id and not self._has_permission(user, "audit_rule:admin"):
                    return False
        
        return True
    
    def check_audit_workflow_permission(self, user: Yonghu, action: str, workflow_id: str = None) -> bool:
        """
        检查审核工作流权限
        
        Args:
            user: 当前用户
            action: 操作类型
            workflow_id: 工作流ID
            
        Returns:
            是否有权限
        """
        # 超级管理员拥有所有权限
        if user.yonghu_ming == 'admin':
            return True
        
        # 检查基础权限
        base_permission = f"audit_workflow:{action}"
        return self._has_permission(user, base_permission)
    
    def check_audit_record_permission(self, user: Yonghu, action: str, record_id: str = None) -> bool:
        """
        检查审核记录权限
        
        Args:
            user: 当前用户
            action: 操作类型
            record_id: 记录ID
            
        Returns:
            是否有权限
        """
        # 超级管理员拥有所有权限
        if user.yonghu_ming == 'admin':
            return True
        
        # 检查基础权限
        base_permission = f"audit_record:{action}"
        if not self._has_permission(user, base_permission):
            return False
        
        # 如果是特定记录操作，检查记录级别权限
        if record_id and action in ['read', 'update']:
            record = self.db.query(ShenheJilu).filter(ShenheJilu.id == record_id).first()
            if record:
                # 检查是否是申请人、审批人或有管理权限
                if (record.shenqing_ren != user.id and 
                    record.dangqian_shenpi_ren != user.id and 
                    not self._has_permission(user, "audit_record:admin")):
                    return False
        
        return True
    
    def check_approval_permission(self, user: Yonghu, record_id: str) -> bool:
        """
        检查审批权限
        
        Args:
            user: 当前用户
            record_id: 审核记录ID
            
        Returns:
            是否有权限
        """
        # 获取审核记录
        record = self.db.query(ShenheJilu).filter(ShenheJilu.id == record_id).first()
        if not record:
            return False
        
        # 检查是否是当前审批人
        if record.dangqian_shenpi_ren != user.id:
            return False
        
        # 检查审批状态
        if record.shenhe_zhuangtai not in ['pending', 'in_progress']:
            return False
        
        return True
    
    def check_amount_approval_authority(self, user: Yonghu, amount: float, rule_type: str) -> bool:
        """
        检查金额审批权限
        
        Args:
            user: 当前用户
            amount: 金额
            rule_type: 规则类型
            
        Returns:
            是否有权限
        """
        # 获取用户角色的审批权限
        user_roles = self.db.query(Jiaose).join(YonghuJiaose).filter(
            YonghuJiaose.yonghu_id == user.id,
            Jiaose.is_deleted == "N"
        ).all()
        
        # 检查每个角色的审批权限
        for role in user_roles:
            authority = self._get_role_approval_authority(role.jiaose_bianma, rule_type)
            max_amount = authority.get("max_amount", 0)
            
            if amount <= max_amount or max_amount == float('inf'):
                return True
        
        return False
    
    def _has_permission(self, user: Yonghu, permission: str) -> bool:
        """检查用户是否有指定权限"""
        # 这里简化处理，实际项目中应该查询用户权限表
        # 可以通过角色权限或直接分配的权限来判断
        
        # 获取用户角色
        user_roles = self.db.query(Jiaose).join(YonghuJiaose).filter(
            YonghuJiaose.yonghu_id == user.id,
            Jiaose.is_deleted == "N"
        ).all()
        
        # 检查角色权限
        for role in user_roles:
            if self._role_has_permission(role.jiaose_bianma, permission):
                return True
        
        return False
    
    def _role_has_permission(self, role_code: str, permission: str) -> bool:
        """检查角色是否有指定权限"""
        # 角色权限映射
        role_permissions = {
            "admin": ["*"],  # 管理员拥有所有权限
            "audit_admin": [
                "audit_rule:*", "audit_workflow:*", "audit_record:*"
            ],
            "audit_manager": [
                "audit_rule:read", "audit_rule:create", "audit_rule:update",
                "audit_workflow:read", "audit_workflow:create",
                "audit_record:read", "audit_record:update"
            ],
            "approver": [
                "audit_record:read", "audit_record:approve"
            ],
            "supervisor": [
                "audit_rule:read", "audit_workflow:read", "audit_record:read"
            ]
        }
        
        permissions = role_permissions.get(role_code, [])
        
        # 检查通配符权限
        if "*" in permissions:
            return True
        
        # 检查具体权限
        if permission in permissions:
            return True
        
        # 检查模块通配符权限
        module = permission.split(":")[0]
        if f"{module}:*" in permissions:
            return True
        
        return False
    
    def _get_role_approval_authority(self, role_code: str, rule_type: str) -> Dict[str, Any]:
        """获取角色在特定规则类型下的审批权限"""
        # 角色审批权限配置
        approval_authorities = {
            "supervisor": {
                "hetong_jine_xiuzheng": {"max_amount": 50000},
                "baojia_shenhe": {"max_amount": 30000},
                "zhifu_shenhe": {"max_amount": 20000}
            },
            "manager": {
                "hetong_jine_xiuzheng": {"max_amount": 200000},
                "baojia_shenhe": {"max_amount": 100000},
                "zhifu_shenhe": {"max_amount": 100000}
            },
            "director": {
                "hetong_jine_xiuzheng": {"max_amount": 1000000},
                "baojia_shenhe": {"max_amount": 500000},
                "zhifu_shenhe": {"max_amount": 500000}
            },
            "ceo": {
                "hetong_jine_xiuzheng": {"max_amount": float('inf')},
                "baojia_shenhe": {"max_amount": float('inf')},
                "zhifu_shenhe": {"max_amount": float('inf')}
            }
        }
        
        role_authority = approval_authorities.get(role_code, {})
        return role_authority.get(rule_type, {"max_amount": 0})


def require_audit_permission(permission: str, resource_id_param: str = None):
    """
    审核权限验证装饰器
    
    Args:
        permission: 权限字符串，格式：模块:操作
        resource_id_param: 资源ID参数名（用于资源级别权限检查）
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取依赖注入的参数
            db = None
            current_user = None
            
            # 从kwargs中提取依赖
            for key, value in kwargs.items():
                if isinstance(value, Session):
                    db = value
                elif isinstance(value, Yonghu):
                    current_user = value
            
            if not db or not current_user:
                raise HTTPException(status_code=500, detail="权限验证失败：缺少必要参数")
            
            # 创建权限检查器
            checker = AuditPermissionChecker(db)
            
            # 获取资源ID
            resource_id = kwargs.get(resource_id_param) if resource_id_param else None
            
            # 根据权限类型进行检查
            module, action = permission.split(":", 1)
            
            has_permission = False
            if module == "audit_rule":
                has_permission = checker.check_audit_rule_permission(current_user, action, resource_id)
            elif module == "audit_workflow":
                has_permission = checker.check_audit_workflow_permission(current_user, action, resource_id)
            elif module == "audit_record":
                has_permission = checker.check_audit_record_permission(current_user, action, resource_id)
            elif module == "approval":
                has_permission = checker.check_approval_permission(current_user, resource_id)
            
            if not has_permission:
                raise HTTPException(
                    status_code=403, 
                    detail=f"权限不足：需要 {permission} 权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_amount_approval_authority(rule_type: str, amount_param: str = "amount"):
    """
    金额审批权限验证装饰器
    
    Args:
        rule_type: 规则类型
        amount_param: 金额参数名
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取依赖注入的参数
            db = None
            current_user = None
            
            for key, value in kwargs.items():
                if isinstance(value, Session):
                    db = value
                elif isinstance(value, Yonghu):
                    current_user = value
            
            if not db or not current_user:
                raise HTTPException(status_code=500, detail="权限验证失败：缺少必要参数")
            
            # 获取金额
            amount = kwargs.get(amount_param, 0)
            if hasattr(amount, 'amount'):  # 如果是请求对象
                amount = getattr(amount, 'amount', 0)
            
            # 创建权限检查器
            checker = AuditPermissionChecker(db)
            
            # 检查金额审批权限
            if not checker.check_amount_approval_authority(current_user, amount, rule_type):
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足：您没有审批 {amount} 金额的权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
