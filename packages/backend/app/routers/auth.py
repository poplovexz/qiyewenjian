"""
认证相关路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict

from ..utils import _make_jwt_token

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login")
async def login(credentials: dict):
    """模拟登录"""
    if credentials.get("yonghu_ming") == "admin" and credentials.get("mima") == "admin123":
        return {
            "message": "登录成功",
            "user": {
                "id": "admin-id",
                "yonghu_ming": "admin",
                "xingming": "管理员",
                "youxiang": "admin@example.com",
                "shouji": "13800138000",
                "zhuangtai": "active",
                "zuihou_denglu": "2024-01-15T10:00:00Z",
                "denglu_cishu": 1,
                "roles": ["admin"],
                "permissions": ["all"]
            },
            "token": {
                "access_token": _make_jwt_token("admin-id", 3600),
                "refresh_token": _make_jwt_token("admin-id", 7200, {"type": "refresh"}),
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.post("/refresh")
async def refresh_token(payload: Dict):
    """模拟刷新令牌"""
    if not payload.get("refresh_token"):
        raise HTTPException(status_code=400, detail="缺少refresh_token")

    return {
        "access_token": _make_jwt_token("admin", 3600),
        "refresh_token": _make_jwt_token("admin", 7 * 24 * 3600, {"type": "refresh"}),
        "token_type": "bearer",
        "expires_in": 3600
    }
