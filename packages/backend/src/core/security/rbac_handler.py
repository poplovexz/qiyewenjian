"""
基于角色的访问控制 (RBAC) 处理器
"""
from typing import List, Set
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models import Yonghu, YonghuJiaose, JiaoseQuanxian, Quanxian
from .jwt_handler import get_current_user


def get_user_permissions(user: Yonghu, db: Session) -> Set[str]:
    """
    获取用户权限列表
    
    Args:
        user: 用户对象
        db: 数据库会话
        
    Returns:
        用户权限编码集合
    """
    permissions = set()
    
    # 查询用户的所有角色
    user_roles = db.query(YonghuJiaose).filter(
        YonghuJiaose.yonghu_id == user.id
    ).all()
    
    # 遍历每个角色，获取角色的权限
    for user_role in user_roles:
        role_permissions = db.query(JiaoseQuanxian).filter(
            JiaoseQuanxian.jiaose_id == user_role.jiaose_id
        ).all()
        
        # 获取权限详情
        for role_permission in role_permissions:
            permission = db.query(Quanxian).filter(
                Quanxian.id == role_permission.quanxian_id,
                Quanxian.zhuangtai == "active",
                Quanxian.is_deleted == "N"
            ).first()
            
            if permission:
                permissions.add(permission.quanxian_bianma)
    
    return permissions


def check_permission(required_permission: str):
    """
    权限检查装饰器
    
    Args:
        required_permission: 需要的权限编码
        
    Returns:
        装饰器函数
    """
    def permission_checker(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # 获取用户权限
        user_permissions = get_user_permissions(current_user, db)
        
        # 检查是否有所需权限
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {required_permission}"
            )
        
        return current_user
    
    return permission_checker


def check_multiple_permissions(required_permissions: List[str], require_all: bool = True):
    """
    多权限检查装饰器
    
    Args:
        required_permissions: 需要的权限编码列表
        require_all: 是否需要所有权限（True）还是任一权限（False）
        
    Returns:
        装饰器函数
    """
    def permission_checker(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # 获取用户权限
        user_permissions = get_user_permissions(current_user, db)
        
        if require_all:
            # 需要所有权限
            missing_permissions = set(required_permissions) - user_permissions
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，缺少权限: {', '.join(missing_permissions)}"
                )
        else:
            # 需要任一权限
            if not any(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要以下任一权限: {', '.join(required_permissions)}"
                )
        
        return current_user
    
    return permission_checker


def has_role(user: Yonghu, role_code: str, db: Session) -> bool:
    """
    检查用户是否有指定角色
    
    Args:
        user: 用户对象
        role_code: 角色编码
        db: 数据库会话
        
    Returns:
        是否有指定角色
    """
    from models import Jiaose
    
    user_role = db.query(YonghuJiaose).join(Jiaose).filter(
        YonghuJiaose.yonghu_id == user.id,
        Jiaose.jiaose_bianma == role_code,
        Jiaose.zhuangtai == "active",
        Jiaose.is_deleted == "N"
    ).first()
    
    return user_role is not None


def check_role(required_role: str):
    """
    角色检查装饰器
    
    Args:
        required_role: 需要的角色编码
        
    Returns:
        装饰器函数
    """
    def role_checker(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not has_role(current_user, required_role, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色权限不足，需要角色: {required_role}"
            )
        
        return current_user
    
    return role_checker
