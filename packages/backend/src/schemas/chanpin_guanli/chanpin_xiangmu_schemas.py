"""
产品项目数据验证模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal

from .chanpin_buzou_schemas import ChanpinBuzouResponse

class ChanpinXiangmuBase(BaseModel):
    """产品项目基础模式"""
    xiangmu_mingcheng: str = Field(..., min_length=1, max_length=200, description="项目名称")
    xiangmu_bianma: str = Field(..., min_length=1, max_length=100, description="项目编码")
    fenlei_id: str = Field(..., description="所属分类ID")
    yewu_baojia: Decimal = Field(..., ge=0, description="业务报价")
    baojia_danwei: Optional[str] = Field("yuan", description="报价单位")
    banshi_tianshu: Optional[int] = Field(0, ge=0, description="办事天数")
    xiangmu_beizhu: Optional[str] = Field(None, max_length=2000, description="项目备注")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class ChanpinXiangmuCreate(BaseModel):
    """创建产品项目模式"""
    xiangmu_mingcheng: str = Field(..., min_length=1, max_length=200, description="项目名称")
    xiangmu_bianma: Optional[str] = Field(None, min_length=1, max_length=100, description="项目编码（可选，不提供则自动生成）")
    fenlei_id: str = Field(..., description="所属分类ID")
    yewu_baojia: Decimal = Field(..., ge=0, description="业务报价")
    baojia_danwei: Optional[str] = Field("yuan", description="报价单位")
    banshi_tianshu: Optional[int] = Field(0, ge=0, description="办事天数")
    xiangmu_beizhu: Optional[str] = Field(None, max_length=2000, description="项目备注")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class ChanpinXiangmuUpdate(BaseModel):
    """更新产品项目模式"""
    xiangmu_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    xiangmu_bianma: Optional[str] = Field(None, min_length=1, max_length=100, description="项目编码")
    fenlei_id: Optional[str] = Field(None, description="所属分类ID")
    yewu_baojia: Optional[Decimal] = Field(None, ge=0, description="业务报价")
    baojia_danwei: Optional[str] = Field(None, description="报价单位")
    banshi_tianshu: Optional[int] = Field(None, ge=0, description="办事天数")
    xiangmu_beizhu: Optional[str] = Field(None, max_length=2000, description="项目备注")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")

class ChanpinXiangmuResponse(ChanpinXiangmuBase):
    """产品项目响应模式"""
    id: str
    created_at: datetime
    updated_at: datetime
    fenlei_mingcheng: Optional[str] = Field(None, description="分类名称")
    buzou_count: int = Field(0, description="步骤数量")
    
    class Config:
        from_attributes = True

class ChanpinXiangmuListItem(BaseModel):
    """产品项目列表项模式"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    xiangmu_mingcheng: str
    xiangmu_bianma: str
    fenlei_id: str
    fenlei_mingcheng: str
    fenlei_bianma: Optional[str] = None
    chanpin_leixing: Optional[str] = None
    yewu_baojia: Decimal
    baojia_danwei: str
    banshi_tianshu: int
    paixu: int
    zhuangtai: str
    created_at: datetime
    updated_at: datetime
    buzou_count: int = 0

class ChanpinXiangmuListParams(BaseModel):
    """产品项目列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    fenlei_id: Optional[str] = Field(None, description="分类ID筛选")
    zhuangtai: Optional[str] = Field(None, description="状态筛选")

class ChanpinXiangmuListResponse(BaseModel):
    """产品项目列表响应模式"""
    model_config = ConfigDict(from_attributes=True)

    items: List[ChanpinXiangmuListItem]
    total: int
    page: int
    size: int
    pages: int

class ChanpinXiangmuDetailResponse(ChanpinXiangmuResponse):
    """产品项目详情响应模式"""
    buzou_list: List[ChanpinBuzouResponse] = Field(default_factory=list, description="步骤列表")
    
    class Config:
        from_attributes = True
