"""
用户管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from uuid import uuid4

from ..data.users import users_data, find_user
from ..utils import _paginate, _now_iso

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get("/")
async def list_users(
    page: int = 1,
    size: int = 20,
    yonghu_ming: Optional[str] = None,
    xingming: Optional[str] = None,
    zhuangtai: Optional[str] = None
):
    """获取用户列表"""
    users = users_data

    if yonghu_ming:
        users = [u for u in users if yonghu_ming.lower() in u.get("yonghu_ming", "").lower()]

    if xingming:
        users = [u for u in users if xingming.lower() in u.get("xingming", "").lower()]

    if zhuangtai:
        users = [u for u in users if u.get("zhuangtai") == zhuangtai]

    return _paginate(users, page, size)


@router.get("/{user_id}")
async def get_user_detail(user_id: str):
    """获取用户详情"""
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/")
async def create_user(payload: Dict):
    """创建用户"""
    if not payload.get("yonghu_ming") or not payload.get("xingming"):
        raise HTTPException(status_code=400, detail="用户名和姓名不能为空")

    new_user = {
        "id": str(uuid4()),
        "yonghu_ming": payload.get("yonghu_ming"),
        "xingming": payload.get("xingming"),
        "youxiang": payload.get("youxiang"),
        "shouji": payload.get("shouji"),
        "zhuangtai": payload.get("zhuangtai", "active"),
        "zuihou_denglu": None,
        "denglu_cishu": 0,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    users_data.append(new_user)
    return new_user


@router.put("/{user_id}")
async def update_user(user_id: str, payload: Dict):
    """更新用户"""
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    for field in ["yonghu_ming", "xingming", "youxiang", "shouji", "zhuangtai"]:
        if field in payload and payload[field] is not None:
            user[field] = payload[field]

    user["updated_at"] = _now_iso()
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """删除用户"""
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    users_data.remove(user)
    return {"message": "用户删除成功"}
