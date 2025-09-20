"""
权限数据模块
"""
from typing import List, Dict, Optional


# 权限模拟数据
permissions_data: List[Dict] = [
    {
        "id": "perm-1",
        "quanxian_ming": "用户管理",
        "quanxian_bianma": "user:manage",
        "miaoshu": "管理系统用户",
        "ziyuan_leixing": "menu",
        "ziyuan_lujing": "/user-management",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system"
    },
    {
        "id": "perm-2",
        "quanxian_ming": "角色管理",
        "quanxian_bianma": "role:manage",
        "miaoshu": "管理系统角色",
        "ziyuan_leixing": "menu",
        "ziyuan_lujing": "/role-management",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system"
    },
    {
        "id": "perm-3",
        "quanxian_ming": "权限管理",
        "quanxian_bianma": "permission:manage",
        "miaoshu": "管理系统权限",
        "ziyuan_leixing": "menu",
        "ziyuan_lujing": "/permission-management",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system"
    },
    {
        "id": "perm-4",
        "quanxian_ming": "创建用户",
        "quanxian_bianma": "user:create",
        "miaoshu": "创建新用户",
        "ziyuan_leixing": "button",
        "ziyuan_lujing": "/api/v1/users",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system"
    },
    {
        "id": "perm-5",
        "quanxian_ming": "删除用户",
        "quanxian_bianma": "user:delete",
        "miaoshu": "删除用户",
        "ziyuan_leixing": "button",
        "ziyuan_lujing": "/api/v1/users/*",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system"
    }
]


def find_permission(permission_id: str) -> Optional[Dict]:
    """查找权限"""
    for item in permissions_data:
        if item["id"] == permission_id:
            return item
    return None
