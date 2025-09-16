"""
用户管理相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class YonghuBase(BaseModel):
    """用户基础模式"""
    yonghu_ming: str
    youxiang: EmailStr
    xingming: str
    shouji: Optional[str] = None


class YonghuCreate(YonghuBase):
    """创建用户模式"""
    mima: str
    role_ids: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "yonghu_ming": "zhangsan",
                "youxiang": "zhangsan@example.com",
                "xingming": "张三",
                "shouji": "13800138000",
                "mima": "password123",
                "role_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


class YonghuUpdate(BaseModel):
    """更新用户模式"""
    youxiang: Optional[EmailStr] = None
    xingming: Optional[str] = None
    shouji: Optional[str] = None
    zhuangtai: Optional[str] = None
    role_ids: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "youxiang": "newemail@example.com",
                "xingming": "新姓名",
                "shouji": "13900139000",
                "zhuangtai": "active",
                "role_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


class YonghuResponse(YonghuBase):
    """用户响应模式"""
    id: str
    zhuangtai: str
    zuihou_denglu: Optional[datetime] = None
    denglu_cishu: str
    created_at: datetime
    updated_at: datetime
    roles: List[dict] = []
    
    class Config:
        from_attributes = True


class YonghuList(BaseModel):
    """用户列表模式"""
    total: int
    items: List[YonghuResponse]
    page: int
    size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "yonghu_ming": "admin",
                        "youxiang": "admin@example.com",
                        "xingming": "管理员",
                        "shouji": "13800138000",
                        "zhuangtai": "active",
                        "zuihou_denglu": "2024-03-15T10:30:00",
                        "denglu_cishu": "10",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-03-15T10:30:00",
                        "roles": [
                            {
                                "id": "role-id-1",
                                "jiaose_ming": "管理员",
                                "jiaose_bianma": "admin"
                            }
                        ]
                    }
                ],
                "page": 1,
                "size": 10
            }
        }
