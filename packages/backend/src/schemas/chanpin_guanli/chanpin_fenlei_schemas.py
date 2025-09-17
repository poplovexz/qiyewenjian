"""
产品分类数据验证模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChanpinFenleiBase(BaseModel):
    """产品分类基础模式"""
    fenlei_mingcheng: str = Field(..., min_length=1, max_length=100, description="分类名称")
    fenlei_bianma: str = Field(..., min_length=1, max_length=50, description="分类编码")
    chanpin_leixing: str = Field(..., description="产品类型：zengzhi(增值产品)、daili_jizhang(代理记账产品)")
    miaoshu: Optional[str] = Field(None, max_length=1000, description="分类描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")


class ChanpinFenleiCreate(ChanpinFenleiBase):
    """创建产品分类模式"""
    pass


class ChanpinFenleiUpdate(BaseModel):
    """更新产品分类模式"""
    fenlei_mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    fenlei_bianma: Optional[str] = Field(None, min_length=1, max_length=50, description="分类编码")
    chanpin_leixing: Optional[str] = Field(None, description="产品类型")
    miaoshu: Optional[str] = Field(None, max_length=1000, description="分类描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")


class ChanpinFenleiResponse(ChanpinFenleiBase):
    """产品分类响应模式"""
    id: str
    created_at: datetime
    updated_at: datetime
    xiangmu_count: int = Field(0, description="项目数量")
    
    class Config:
        from_attributes = True


class ChanpinFenleiListItem(BaseModel):
    """产品分类列表项模式"""
    id: str
    fenlei_mingcheng: str
    fenlei_bianma: str
    chanpin_leixing: str
    miaoshu: Optional[str]
    paixu: int
    zhuangtai: str
    created_at: datetime
    updated_at: datetime
    xiangmu_count: int = 0
    
    class Config:
        from_attributes = True


class ChanpinFenleiListParams(BaseModel):
    """产品分类列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    chanpin_leixing: Optional[str] = Field(None, description="产品类型筛选")
    zhuangtai: Optional[str] = Field(None, description="状态筛选")


class ChanpinFenleiListResponse(BaseModel):
    """产品分类列表响应模式"""
    items: List[ChanpinFenleiListItem]
    total: int
    page: int
    size: int
    pages: int


class ChanpinFenleiOption(BaseModel):
    """产品分类选项模式（用于下拉选择）"""
    id: str
    fenlei_mingcheng: str
    fenlei_bianma: str
    chanpin_leixing: str

    class Config:
        from_attributes = True
