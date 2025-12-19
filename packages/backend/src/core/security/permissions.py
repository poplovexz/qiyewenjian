"""
权限检查装饰器和工具函数
"""
from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from .jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu, Jiaose, Quanxian, JiaoseQuanxian

def check_permission(permission_code: str):
    """
    权限检查装饰器
    
    Args:
        permission_code: 权限编码，如 'customer:read', 'customer:write' 等
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入中获取当前用户和数据库会话
            current_user = None
            db = None
            
            # 查找函数参数中的 current_user 和 db
            for arg in args:
                if isinstance(arg, Yonghu):
                    current_user = arg
                elif isinstance(arg, Session):
                    db = arg
            
            # 从 kwargs 中查找
            if not current_user:
                current_user = kwargs.get('current_user')
            if not db:
                db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="权限检查失败：缺少必要参数"
                )
            
            # 检查用户权限
            if not has_permission(db, current_user, permission_code):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足：需要 {permission_code} 权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(db: Session, user: Yonghu, permission_code: str) -> bool:
    """
    检查用户是否具有指定权限
    
    Args:
        db: 数据库会话
        user: 用户对象
        permission_code: 权限编码
        
    Returns:
        bool: 是否具有权限
    """
    # 超级管理员拥有所有权限
    if user.yonghu_ming == "admin":
        return True
    
    # 查询用户的所有角色
    from models.yonghu_guanli import YonghuJiaose
    user_roles = db.query(Jiaose).join(
        YonghuJiaose, YonghuJiaose.jiaose_id == Jiaose.id
    ).filter(
        YonghuJiaose.yonghu_id == user.id,
        Jiaose.zhuangtai == "active"
    ).all()
    
    # 查询角色的所有权限
    for role in user_roles:
        role_permissions = db.query(Quanxian).join(
            JiaoseQuanxian
        ).filter(
            JiaoseQuanxian.jiaose_id == role.id,
            Quanxian.quanxian_bianma == permission_code,
            Quanxian.zhuangtai == "active"
        ).first()
        
        if role_permissions:
            return True
    
    return False

def get_user_permissions(db: Session, user: Yonghu) -> List[str]:
    """
    获取用户的所有权限编码列表
    
    Args:
        db: 数据库会话
        user: 用户对象
        
    Returns:
        List[str]: 权限编码列表
    """
    # 超级管理员拥有所有权限
    if user.yonghu_ming == "admin":
        all_permissions = db.query(Quanxian).filter(
            Quanxian.zhuangtai == "active"
        ).all()
        return [perm.quanxian_bianma for perm in all_permissions]
    
    # 查询用户的所有权限
    permissions = db.query(Quanxian).join(
        JiaoseQuanxian
    ).join(
        Jiaose
    ).join(
        Jiaose.yonghu_liebiao
    ).filter(
        Yonghu.id == user.id,
        Jiaose.zhuangtai == "active",
        Quanxian.zhuangtai == "active"
    ).distinct().all()
    
    return [perm.quanxian_bianma for perm in permissions]

def require_permission(permission_code: str):
    """
    FastAPI 依赖注入形式的权限检查
    
    Args:
        permission_code: 权限编码
        
    Returns:
        依赖函数
    """
    def permission_dependency(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not has_permission(db, current_user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {permission_code} 权限"
            )
        return current_user
    
    return permission_dependency

def require_any_permission(permission_codes: List[str]):
    """
    要求用户具有任意一个权限
    
    Args:
        permission_codes: 权限编码列表
        
    Returns:
        依赖函数
    """
    def permission_dependency(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        for permission_code in permission_codes:
            if has_permission(db, current_user, permission_code):
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足：需要以下任意权限之一：{', '.join(permission_codes)}"
        )
    
    return permission_dependency

def require_all_permissions(permission_codes: List[str]):
    """
    要求用户具有所有权限
    
    Args:
        permission_codes: 权限编码列表
        
    Returns:
        依赖函数
    """
    def permission_dependency(
        current_user: Yonghu = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        for permission_code in permission_codes:
            if not has_permission(db, current_user, permission_code):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足：需要 {permission_code} 权限"
                )
        return current_user
    
    return permission_dependency
