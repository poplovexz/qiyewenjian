"""
用户管理相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class YonghuBase(BaseModel):
    """用户基础模式"""
    yonghu_ming: str = Field(..., min_length=3, max_length=50, description="用户名")
    youxiang: Optional[EmailStr] = Field(None, description="邮箱")
    xingming: str = Field(..., min_length=1, max_length=50, description="姓名")
    shouji: Optional[str] = Field(None, max_length=20, description="手机号")
    zhuangtai: Optional[str] = Field("正常", max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class YonghuCreate(YonghuBase):
    """创建用户模式"""
    mima: str = Field(..., min_length=6, max_length=100, description="密码")


class YonghuUpdate(BaseModel):
    """更新用户模式"""
    yonghu_ming: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    mima: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")
    youxiang: Optional[EmailStr] = Field(None, description="邮箱")
    xingming: Optional[str] = Field(None, min_length=1, max_length=50, description="姓名")
    shouji: Optional[str] = Field(None, max_length=20, description="手机号")
    zhuangtai: Optional[str] = Field(None, max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class YonghuResponse(YonghuBase):
    """用户响应模式"""
    id: str
    denglu_cishu: int = Field(description="登录次数")
    zuihou_denglu: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class YonghuList(BaseModel):
    """用户列表响应模式"""
    items: List[YonghuResponse]
    total: int
    page: int
    size: int


# 角色相关模式
class JiaoseBase(BaseModel):
    """角色基础模式"""
    jiaose_ming: str = Field(..., min_length=1, max_length=50, description="角色名称")
    jiaose_bianma: Optional[str] = Field(None, max_length=50, description="角色编码")
    miaoshu: Optional[str] = Field(None, max_length=500, description="角色描述")
    zhuangtai: Optional[str] = Field("active", max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class JiaoseCreate(JiaoseBase):
    """创建角色模式"""
    pass


class JiaoseUpdate(BaseModel):
    """更新角色模式"""
    jiaose_ming: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    jiaose_bianma: Optional[str] = Field(None, max_length=50, description="角色编码")
    miaoshu: Optional[str] = Field(None, max_length=500, description="角色描述")
    zhuangtai: Optional[str] = Field(None, max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class JiaoseResponse(JiaoseBase):
    """角色响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JiaoseList(BaseModel):
    """角色列表响应模式"""
    items: List[JiaoseResponse]
    total: int
    page: int
    size: int


# 权限相关模式
class QuanxianBase(BaseModel):
    """权限基础模式"""
    quanxian_ming: str = Field(..., min_length=1, max_length=50, description="权限名称")
    quanxian_bianma: Optional[str] = Field(None, max_length=50, description="权限编码")
    miaoshu: Optional[str] = Field(None, max_length=500, description="权限描述")
    ziyuan_leixing: str = Field(..., max_length=20, description="资源类型")
    ziyuan_lujing: Optional[str] = Field(None, max_length=200, description="资源路径")
    zhuangtai: Optional[str] = Field("active", max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class QuanxianCreate(QuanxianBase):
    """创建权限模式"""
    pass


class QuanxianUpdate(BaseModel):
    """更新权限模式"""
    quanxian_ming: Optional[str] = Field(None, min_length=1, max_length=50, description="权限名称")
    quanxian_bianma: Optional[str] = Field(None, max_length=50, description="权限编码")
    miaoshu: Optional[str] = Field(None, max_length=500, description="权限描述")
    ziyuan_leixing: Optional[str] = Field(None, max_length=20, description="资源类型")
    ziyuan_lujing: Optional[str] = Field(None, max_length=200, description="资源路径")
    zhuangtai: Optional[str] = Field(None, max_length=20, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class QuanxianResponse(QuanxianBase):
    """权限响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuanxianList(BaseModel):
    """权限列表响应模式"""
    items: List[QuanxianResponse]
    total: int
    page: int
    size: int


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
