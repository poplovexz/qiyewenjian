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
from .jiaose_schemas import (
    JiaoseCreate,
    JiaoseUpdate,
    JiaoseResponse,
    JiaoseListResponse,
    JiaoseListItem,
    JiaoseStatusUpdate,
    JiaosePermissionUpdate,
    JiaoseStatistics
)
from .quanxian_schemas import (
    QuanxianCreate,
    QuanxianUpdate,
    QuanxianResponse,
    QuanxianListResponse,
    QuanxianListItem,
    QuanxianTreeResponse,
    QuanxianStatistics
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
    "YonghuList",

    # 角色管理
    "JiaoseCreate",
    "JiaoseUpdate",
    "JiaoseResponse",
    "JiaoseListResponse",
    "JiaoseListItem",
    "JiaoseStatusUpdate",
    "JiaosePermissionUpdate",
    "JiaoseStatistics",

    # 权限管理
    "QuanxianCreate",
    "QuanxianUpdate",
    "QuanxianResponse",
    "QuanxianListResponse",
    "QuanxianListItem",
    "QuanxianTreeResponse",
    "QuanxianStatistics"
]
