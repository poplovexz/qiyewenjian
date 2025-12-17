"""
角色管理相关的Pydantic模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class JiaoseBase(BaseModel):
    """角色基础模型"""
    jiaose_ming: str = Field(..., min_length=2, max_length=50, description="角色名称")
    jiaose_bianma: str = Field(..., min_length=2, max_length=50, description="角色编码")
    miaoshu: Optional[str] = Field(None, max_length=200, description="角色描述")
    zhuangtai: str = Field("active", description="角色状态：active-启用，inactive-禁用")

    @validator('jiaose_bianma')
    def validate_jiaose_bianma(cls, v):
        """验证角色编码格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('角色编码只能包含字母、数字、下划线和连字符')
        return v.lower()

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        """验证状态值"""
        if v not in ['active', 'inactive']:
            raise ValueError('状态只能是 active 或 inactive')
        return v


class JiaoseCreate(JiaoseBase):
    """创建角色请求模型"""
    pass


class JiaoseUpdate(BaseModel):
    """更新角色请求模型"""
    jiaose_ming: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    jiaose_bianma: Optional[str] = Field(None, min_length=2, max_length=50, description="角色编码")
    miaoshu: Optional[str] = Field(None, max_length=200, description="角色描述")
    zhuangtai: Optional[str] = Field(None, description="角色状态")

    @validator('jiaose_bianma')
    def validate_jiaose_bianma(cls, v):
        """验证角色编码格式"""
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('角色编码只能包含字母、数字、下划线和连字符')
        return v.lower() if v else v

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        """验证状态值"""
        if v is not None and v not in ['active', 'inactive']:
            raise ValueError('状态只能是 active 或 inactive')
        return v


class JiaoseStatusUpdate(BaseModel):
    """角色状态更新模型"""
    zhuangtai: str = Field(..., description="角色状态：active-启用，inactive-禁用")
    reason: Optional[str] = Field(None, max_length=200, description="状态变更原因")

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        """验证状态值"""
        if v not in ['active', 'inactive']:
            raise ValueError('状态只能是 active 或 inactive')
        return v


class JiaosePermissionUpdate(BaseModel):
    """角色权限更新模型"""
    permission_ids: List[str] = Field(..., description="权限ID列表")

    @validator('permission_ids')
    def validate_permission_ids(cls, v):
        """验证权限ID列表"""
        if not isinstance(v, list):
            raise ValueError('权限ID必须是列表格式')
        # 去重
        return list(set(v))


class QuanxianSimple(BaseModel):
    """权限简单信息模型"""
    id: str
    quanxian_ming: str
    quanxian_bianma: str
    ziyuan_leixing: str
    zhuangtai: str

    class Config:
        from_attributes = True


class YonghuSimple(BaseModel):
    """用户简单信息模型"""
    id: str
    yonghu_ming: str
    xing_ming: str
    zhuangtai: str

    class Config:
        from_attributes = True


class JiaoseResponse(JiaoseBase):
    """角色响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    permissions: Optional[List[QuanxianSimple]] = []
    users: Optional[List[YonghuSimple]] = []

    class Config:
        from_attributes = True


class JiaoseListItem(BaseModel):
    """角色列表项模型"""
    id: str
    jiaose_ming: str
    jiaose_bianma: str
    miaoshu: Optional[str]
    zhuangtai: str
    created_at: datetime
    updated_at: datetime
    permission_count: int = 0
    user_count: int = 0

    class Config:
        from_attributes = True


class JiaoseListResponse(BaseModel):
    """角色列表响应模型"""
    items: List[JiaoseListItem]
    total: int
    page: int
    size: int
    pages: int


class JiaoseStatistics(BaseModel):
    """角色统计信息模型"""
    total_roles: int = 0
    active_roles: int = 0
    inactive_roles: int = 0
    total_users: int = 0
    roles_with_permissions: int = 0
