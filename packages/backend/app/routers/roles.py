"""
角色管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from uuid import uuid4

from ..data.roles import roles_data, find_role, role_permissions_map
from ..data.permissions import find_permission
from ..utils import _paginate, _now_iso

router = APIRouter(prefix="/api/v1/user-management/roles", tags=["角色管理"])


@router.get("/")
async def list_roles(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    zhuangtai: Optional[str] = None
):
    """获取角色列表（带筛选与分页）"""
    filtered = roles_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item["jiaose_ming"].lower()
            or keyword in item["jiaose_bianma"].lower()
            or keyword in (item.get("miaoshu") or "").lower()
        ]

    if zhuangtai:
        filtered = [item for item in filtered if item["zhuangtai"] == zhuangtai]

    return _paginate(filtered, page, size)


@router.get("/{role_id}")
async def get_role_detail(role_id: str):
    """获取角色详情"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


@router.post("/")
async def create_role(payload: Dict):
    """创建角色（模拟）"""
    new_role = {
        "id": str(uuid4()),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin"),
        "updated_by": payload.get("created_by", "admin"),
        "users": [],
        **{k: payload.get(k) for k in [
            "jiaose_ming",
            "jiaose_bianma",
            "miaoshu",
            "zhuangtai"
        ]}
    }

    # 简单校验
    if not new_role.get("jiaose_ming") or not new_role.get("jiaose_bianma"):
        raise HTTPException(status_code=400, detail="角色名称和编码不能为空")

    roles_data.append(new_role)
    return new_role


@router.put("/{role_id}")
async def update_role(role_id: str, payload: Dict):
    """更新角色（模拟）"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    for field in ["jiaose_ming", "jiaose_bianma", "miaoshu", "zhuangtai"]:
        if field in payload and payload[field] is not None:
            role[field] = payload[field]

    role["updated_at"] = _now_iso()
    role["updated_by"] = payload.get("updated_by", "admin")
    return role


@router.delete("/{role_id}")
async def delete_role(role_id: str):
    """删除角色（模拟）"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    roles_data.remove(role)

    # 移除权限映射
    if role_id in role_permissions_map:
        del role_permissions_map[role_id]

    return {"message": "角色删除成功"}


@router.get("/{role_id}/permissions")
async def get_role_permissions(role_id: str):
    """获取角色的权限列表"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    permission_ids = role_permissions_map.get(role_id, [])
    permissions = []
    for pid in permission_ids:
        perm = find_permission(pid)
        if perm:
            permissions.append(perm)

    return permissions


@router.post("/{role_id}/permissions")
async def assign_role_permissions(role_id: str, permission_ids: List[str]):
    """为角色分配权限（模拟）"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 验证权限是否存在
    for pid in permission_ids:
        if not find_permission(pid):
            raise HTTPException(status_code=400, detail=f"权限 {pid} 不存在")

    role_permissions_map[role_id] = permission_ids
    return {"message": "权限分配成功"}


@router.post("/{role_id}/users")
async def assign_role_users(role_id: str, user_ids: List[str]):
    """为角色分配用户（模拟）"""
    role = find_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 简单记录：将用户追加到角色的用户列表中
    for other_role in roles_data:
        # 移除原有关联
        other_role["users"] = [u for u in other_role.get("users", []) if u.get("id") not in user_ids]

    for user_id in user_ids:
        role.setdefault("users", []).append({
            "id": user_id,
            "yonghu_ming": f"user_{user_id}",
            "xing_ming": f"用户{user_id}",
            "zhuangtai": "active"
        })

    return {"message": "用户分配成功"}
