"""
线索来源相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

class XiansuoLaiyuanBase(BaseModel):
    """线索来源基础模式"""
    laiyuan_mingcheng: str = Field(..., min_length=1, max_length=100, description="来源名称")
    laiyuan_bianma: str = Field(..., min_length=1, max_length=50, description="来源编码")
    laiyuan_leixing: str = Field(..., description="来源类型：online-线上，offline-线下，referral-推荐")
    huoqu_chengben: Optional[Decimal] = Field(0.00, ge=0, description="获取成本（元）")
    zhuangtai: Optional[str] = Field("active", description="状态：active-启用，inactive-停用")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    miaoshu: Optional[str] = Field(None, max_length=500, description="描述")

class XiansuoLaiyuanCreate(XiansuoLaiyuanBase):
    """创建线索来源模式"""
    pass

class XiansuoLaiyuanUpdate(BaseModel):
    """更新线索来源模式"""
    laiyuan_mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="来源名称")
    laiyuan_bianma: Optional[str] = Field(None, min_length=1, max_length=50, description="来源编码")
    laiyuan_leixing: Optional[str] = Field(None, description="来源类型")
    huoqu_chengben: Optional[Decimal] = Field(None, ge=0, description="获取成本（元）")
    zhuangtai: Optional[str] = Field(None, description="状态")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    miaoshu: Optional[str] = Field(None, max_length=500, description="描述")

class XiansuoLaiyuanResponse(XiansuoLaiyuanBase):
    """线索来源响应模式"""
    id: str
    xiansuo_shuliang: int = Field(default=0, description="线索数量")
    zhuanhua_shuliang: int = Field(default=0, description="转化数量")
    zhuanhua_lv: Decimal = Field(default=0.00, description="转化率（%）")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class XiansuoLaiyuanListItem(BaseModel):
    """线索来源列表项模式"""
    id: str
    laiyuan_mingcheng: str
    laiyuan_bianma: str
    laiyuan_leixing: str
    huoqu_chengben: Decimal
    xiansuo_shuliang: int
    zhuanhua_shuliang: int
    zhuanhua_lv: Decimal
    zhuangtai: str
    paixu: int
    
    class Config:
        from_attributes = True

class XiansuoLaiyuanListResponse(BaseModel):
    """线索来源列表响应模式"""
    items: List[XiansuoLaiyuanResponse]
    total: int
    page: int
    size: int
