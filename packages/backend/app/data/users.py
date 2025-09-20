"""
用户数据模块
"""
from typing import List, Dict, Optional


# 用户模拟数据
users_data: List[Dict] = [
    {
        "id": "user-1",
        "yonghu_ming": "admin",
        "xingming": "管理员",
        "youxiang": "admin@example.com",
        "shouji": "13800138000",
        "zhuangtai": "active",
        "zuihou_denglu": "2024-01-15T10:00:00Z",
        "denglu_cishu": 1,
        "created_at": "2024-01-01T08:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "created_by": "system"
    },
    {
        "id": "user-2", 
        "yonghu_ming": "operator",
        "xingming": "运营专员",
        "youxiang": "operator@example.com",
        "shouji": "13800138001",
        "zhuangtai": "active",
        "zuihou_denglu": "2024-01-14T09:00:00Z",
        "denglu_cishu": 5,
        "created_at": "2024-01-02T08:00:00Z",
        "updated_at": "2024-01-14T09:00:00Z",
        "created_by": "admin"
    }
]


def find_user(user_id: str) -> Optional[Dict]:
    """查找用户"""
    for item in users_data:
        if item["id"] == user_id:
            return item
    return None
