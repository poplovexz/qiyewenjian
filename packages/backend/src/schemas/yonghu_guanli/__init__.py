"""
用户管理模块 Pydantic 模式
"""
from .auth_schemas import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserInfo,
    ChangePasswordRequest
)
from .yonghu_schemas import (
    YonghuCreate,
    YonghuUpdate,
    YonghuResponse,
    YonghuList
)

__all__ = [
    # 认证相关
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserInfo",
    "ChangePasswordRequest",

    # 用户管理
    "YonghuCreate",
    "YonghuUpdate",
    "YonghuResponse",
    "YonghuList"
]
