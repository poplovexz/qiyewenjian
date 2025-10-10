"""
认证相关的 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models import Yonghu
from schemas.yonghu_guanli import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UserInfo
)
from services.yonghu_guanli import AuthService


router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    - **yonghu_ming**: 用户名
    - **mima**: 密码
    
    返回用户信息和访问令牌
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌接口
    
    - **refresh_token**: 刷新令牌
    
    返回新的访问令牌和刷新令牌
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_data.refresh_token)


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息
    
    需要有效的访问令牌
    """
    auth_service = AuthService(db)
    
    # 获取用户角色和权限
    from core.security import get_user_permissions
    user_roles = auth_service.get_user_roles(current_user)
    user_permissions = list(get_user_permissions(current_user, db))
    
    return UserInfo(
        id=str(current_user.id),
        yonghu_ming=current_user.yonghu_ming,
        youxiang=current_user.youxiang,
        xingming=current_user.xingming,
        shouji=current_user.shouji,
        zhuangtai=current_user.zhuangtai,
        zuihou_denglu=current_user.zuihou_denglu,
        denglu_cishu=current_user.denglu_cishu,
        roles=user_roles,
        permissions=user_permissions
    )


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码
    - **confirm_password**: 确认新密码
    
    需要有效的访问令牌
    """
    # 验证新密码确认
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码与确认密码不匹配"
        )
    
    auth_service = AuthService(db)
    auth_service.change_password(
        current_user,
        password_data.old_password,
        password_data.new_password
    )
    
    return {"message": "密码修改成功"}


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: Yonghu = Depends(get_current_user)
):
    """
    用户登出接口
    
    注意：由于 JWT 是无状态的，实际的令牌失效需要在客户端处理
    这个接口主要用于记录登出日志或清理服务端状态
    """
    return {"message": "登出成功"}
