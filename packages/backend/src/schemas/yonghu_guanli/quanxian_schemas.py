"""
权限管理相关的Pydantic模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class QuanxianBase(BaseModel):
    """权限基础模型"""
    quanxian_ming: str = Field(..., min_length=2, max_length=50, description="权限名称")
    quanxian_bianma: str = Field(..., min_length=2, max_length=100, description="权限编码")
    miaoshu: Optional[str] = Field(None, max_length=200, description="权限描述")
    ziyuan_leixing: str = Field(..., description="资源类型：menu-菜单，button-按钮，api-接口")
    ziyuan_lujing: str = Field(..., max_length=200, description="资源路径")
    zhuangtai: str = Field("active", description="权限状态：active-启用，inactive-禁用")

    @validator('quanxian_bianma')
    def validate_quanxian_bianma(cls, v):
        """验证权限编码格式"""
        if not v.replace(':', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('权限编码只能包含字母、数字、冒号、下划线和连字符')
        return v.lower()

    @validator('ziyuan_leixing')
    def validate_ziyuan_leixing(cls, v):
        """验证资源类型"""
        valid_types = ['menu', 'button', 'api']
        if v not in valid_types:
            raise ValueError(f'资源类型只能是: {", ".join(valid_types)}')
        return v

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        """验证状态值"""
        if v not in ['active', 'inactive']:
            raise ValueError('状态只能是 active 或 inactive')
        return v

class QuanxianCreate(QuanxianBase):
    """创建权限请求模型"""
    pass

class QuanxianUpdate(BaseModel):
    """更新权限请求模型"""
    quanxian_ming: Optional[str] = Field(None, min_length=2, max_length=50, description="权限名称")
    quanxian_bianma: Optional[str] = Field(None, min_length=2, max_length=100, description="权限编码")
    miaoshu: Optional[str] = Field(None, max_length=200, description="权限描述")
    ziyuan_leixing: Optional[str] = Field(None, description="资源类型")
    ziyuan_lujing: Optional[str] = Field(None, max_length=200, description="资源路径")
    zhuangtai: Optional[str] = Field(None, description="权限状态")

    @validator('quanxian_bianma')
    def validate_quanxian_bianma(cls, v):
        """验证权限编码格式"""
        if v is not None and not v.replace(':', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('权限编码只能包含字母、数字、冒号、下划线和连字符')
        return v.lower() if v else v

    @validator('ziyuan_leixing')
    def validate_ziyuan_leixing(cls, v):
        """验证资源类型"""
        if v is not None:
            valid_types = ['menu', 'button', 'api']
            if v not in valid_types:
                raise ValueError(f'资源类型只能是: {", ".join(valid_types)}')
        return v

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        """验证状态值"""
        if v is not None and v not in ['active', 'inactive']:
            raise ValueError('状态只能是 active 或 inactive')
        return v

class QuanxianResponse(QuanxianBase):
    """权限响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class QuanxianListItem(BaseModel):
    """权限列表项模型"""
    id: str
    quanxian_ming: str
    quanxian_bianma: str
    miaoshu: Optional[str]
    ziyuan_leixing: str
    ziyuan_lujing: str
    zhuangtai: str
    created_at: datetime
    updated_at: datetime
    role_count: int = 0

    class Config:
        from_attributes = True

class QuanxianListResponse(BaseModel):
    """权限列表响应模型"""
    items: List[QuanxianListItem]
    total: int
    page: int
    size: int
    pages: int

class QuanxianTreeNode(BaseModel):
    """权限树节点模型"""
    id: str
    label: str
    quanxian_bianma: Optional[str] = None
    ziyuan_leixing: Optional[str] = None
    children: Optional[List['QuanxianTreeNode']] = []
    is_permission: bool = False  # 是否是权限节点（叶子节点）

    class Config:
        from_attributes = True

class QuanxianTreeResponse(QuanxianTreeNode):
    """权限树响应模型"""
    pass

class QuanxianStatistics(BaseModel):
    """权限统计信息模型"""
    total_permissions: int = 0
    menu_permissions: int = 0
    button_permissions: int = 0
    api_permissions: int = 0
    active_permissions: int = 0
    inactive_permissions: int = 0
    permissions_with_roles: int = 0

class QuanxianGroupByModule(BaseModel):
    """按模块分组的权限模型"""
    module_name: str
    module_code: str
    permissions: List[QuanxianResponse]
    permission_count: int

# 更新前向引用
QuanxianTreeNode.model_rebuild()
