"""
角色数据模块
"""
from typing import List, Dict, Optional


# 角色模拟数据
roles_data: List[Dict] = [
    {
        "id": "role-admin",
        "jiaose_ming": "系统管理员",
        "jiaose_bianma": "admin",
        "miaoshu": "拥有系统所有权限",
        "zhuangtai": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "system",
        "updated_by": "system",
        "users": []
    },
    {
        "id": "role-ops",
        "jiaose_ming": "运营专员",
        "jiaose_bianma": "ops",
        "miaoshu": "负责日常运营与数据维护",
        "zhuangtai": "active",
        "created_at": "2024-01-02T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "created_by": "system",
        "updated_by": "system",
        "users": []
    }
]


# 角色权限映射
role_permissions_map: Dict[str, List[str]] = {
    "role-admin": ["perm-1", "perm-2", "perm-3", "perm-4", "perm-5"],
    "role-ops": ["perm-1", "perm-3", "perm-5"]
}


def find_role(role_id: str) -> Optional[Dict]:
    """查找角色"""
    for item in roles_data:
        if item["id"] == role_id:
            return item
    return None
