"""
认证相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class LoginRequest(BaseModel):
    """登录请求模式"""
    yonghu_ming: str = Field(..., alias="username", description="用户名")
    mima: str = Field(..., alias="password", description="密码")

    class Config:
        populate_by_name = True  # 允许使用字段名或别名
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }

class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str

class UserInfo(BaseModel):
    """用户信息模式"""
    id: str
    yonghu_ming: str
    youxiang: str
    xingming: str
    shouji: Optional[str] = None
    zhuangtai: str
    zuihou_denglu: Optional[datetime] = None
    denglu_cishu: str
    roles: List[str] = []
    permissions: List[str] = []
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """登录响应模式"""
    message: str
    user: UserInfo
    token: TokenResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "登录成功",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "yonghu_ming": "admin",
                    "youxiang": "admin@example.com",
                    "xingming": "管理员",
                    "shouji": "13800138000",
                    "zhuangtai": "active",
                    "zuihou_denglu": "2024-03-15T10:30:00",
                    "denglu_cishu": "10",
                    "roles": ["admin"],
                    "permissions": ["user_manage", "customer_manage"]
                },
                "token": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }

class ChangePasswordRequest(BaseModel):
    """修改密码请求模式"""
    old_password: str
    new_password: str
    confirm_password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }
