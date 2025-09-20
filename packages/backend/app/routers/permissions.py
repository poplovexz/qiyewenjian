"""
权限管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from uuid import uuid4

from ..data.permissions import permissions_data, find_permission
from ..data.roles import role_permissions_map
from ..utils import _paginate, _now_iso

router = APIRouter(prefix="/api/v1/user-management/permissions", tags=["权限管理"])


@router.get("/")
async def list_permissions(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    ziyuan_leixing: Optional[str] = None,
    zhuangtai: Optional[str] = None
):
    """获取权限列表（带筛选与分页）"""
    filtered = permissions_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item["quanxian_ming"].lower()
            or keyword in item["quanxian_bianma"].lower()
            or keyword in (item.get("miaoshu") or "").lower()
        ]

    if ziyuan_leixing:
        filtered = [item for item in filtered if item["ziyuan_leixing"] == ziyuan_leixing]

    if zhuangtai:
        filtered = [item for item in filtered if item["zhuangtai"] == zhuangtai]

    return _paginate(filtered, page, size)


@router.get("/{permission_id}")
async def get_permission_detail(permission_id: str):
    """获取权限详情"""
    permission = find_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission


@router.post("/")
async def create_permission(payload: Dict):
    """创建权限（模拟）"""
    new_permission = {
        "id": str(uuid4()),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin"),
        "updated_by": payload.get("created_by", "admin"),
        **{k: payload.get(k) for k in [
            "quanxian_ming",
            "quanxian_bianma",
            "miaoshu",
            "ziyuan_leixing",
            "ziyuan_lujing",
            "zhuangtai"
        ]}
    }

    # 简单校验
    if not new_permission.get("quanxian_ming") or not new_permission.get("quanxian_bianma"):
        raise HTTPException(status_code=400, detail="权限名称和编码不能为空")

    permissions_data.append(new_permission)
    return new_permission


@router.put("/{permission_id}")
async def update_permission(permission_id: str, payload: Dict):
    """更新权限（模拟）"""
    permission = find_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")

    for field in ["quanxian_ming", "quanxian_bianma", "miaoshu", "ziyuan_leixing", "ziyuan_lujing", "zhuangtai"]:
        if field in payload and payload[field] is not None:
            permission[field] = payload[field]

    permission["updated_at"] = _now_iso()
    permission["updated_by"] = payload.get("updated_by", "admin")
    return permission


@router.delete("/{permission_id}")
async def delete_permission(permission_id: str):
    """删除权限（模拟）"""
    permission = find_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    permissions_data.remove(permission)

    # 同步移除角色关联
    for _, ids in role_permissions_map.items():
        if permission_id in ids:
            ids.remove(permission_id)

    return {"message": "权限删除成功"}


@router.get("/tree")
async def get_permission_tree(zhuangtai: Optional[str] = "active"):
    """获取权限树（简单分组）"""
    filtered = permissions_data
    if zhuangtai:
        filtered = [item for item in filtered if item["zhuangtai"] == zhuangtai]

    tree: List[Dict] = []
    group_map: Dict[str, Dict] = {}

    for item in filtered:
        group = item["ziyuan_leixing"]
        if group not in group_map:
            node = {
                "id": f"group-{group}",
                "label": group,
                "is_permission": False,
                "children": []
            }
            group_map[group] = node
            tree.append(node)

        group_map[group]["children"].append({
            "id": item["id"],
            "label": item["quanxian_ming"],
            "quanxian_bianma": item["quanxian_bianma"],
            "ziyuan_leixing": item["ziyuan_leixing"],
            "is_permission": True
        })

    return tree


@router.get("/by-resource-type/{resource_type}")
async def get_permissions_by_resource(resource_type: str, zhuangtai: Optional[str] = None):
    """按资源类型获取权限"""
    filtered = [item for item in permissions_data if item["ziyuan_leixing"] == resource_type]
    if zhuangtai:
        filtered = [item for item in filtered if item["zhuangtai"] == zhuangtai]
    return filtered


@router.get("/statistics/summary")
async def get_permission_statistics():
    """返回权限统计信息"""
    total_permissions = len(permissions_data)
    return {
        "total_permissions": total_permissions,
        "menu_permissions": len([p for p in permissions_data if p["ziyuan_leixing"] == "menu"]),
        "button_permissions": len([p for p in permissions_data if p["ziyuan_leixing"] == "button"]),
        "api_permissions": len([p for p in permissions_data if p["ziyuan_leixing"] == "api"]),
        "active_permissions": len([p for p in permissions_data if p["zhuangtai"] == "active"]),
        "inactive_permissions": len([p for p in permissions_data if p["zhuangtai"] == "inactive"]),
        "permissions_with_roles": len({pid for ids in role_permissions_map.values() for pid in ids})
    }
