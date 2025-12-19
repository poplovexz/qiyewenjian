"""
财务设置相关的Pydantic模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== 收付款渠道 ====================
class ShoufukuanQudaoBase(BaseModel):
    """收付款渠道基础模式"""
    mingcheng: str = Field(..., min_length=1, max_length=100, description="渠道名称")
    leixing: str = Field(..., description="渠道类型：shoukuan(收款)、fukuan(付款)、shoufukuan(收付款)")
    zhanghu_mingcheng: Optional[str] = Field(None, max_length=200, description="账户名称")
    zhanghu_haoma: Optional[str] = Field(None, max_length=100, description="账户号码")
    kaihuhang: Optional[str] = Field(None, max_length=200, description="开户行")
    lianhanghao: Optional[str] = Field(None, max_length=50, description="联行号")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class ShoufukuanQudaoCreate(ShoufukuanQudaoBase):
    """创建收付款渠道模式"""
    pass

class ShoufukuanQudaoUpdate(BaseModel):
    """更新收付款渠道模式"""
    mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="渠道名称")
    leixing: Optional[str] = Field(None, description="渠道类型")
    zhanghu_mingcheng: Optional[str] = Field(None, max_length=200, description="账户名称")
    zhanghu_haoma: Optional[str] = Field(None, max_length=100, description="账户号码")
    kaihuhang: Optional[str] = Field(None, max_length=200, description="开户行")
    lianhanghao: Optional[str] = Field(None, max_length=50, description="联行号")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")

class ShoufukuanQudaoResponse(ShoufukuanQudaoBase):
    """收付款渠道响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ShoufukuanQudaoListResponse(BaseModel):
    """收付款渠道列表响应"""
    items: List[ShoufukuanQudaoResponse]
    total: int
    page: int
    size: int
    pages: int

# ==================== 收入类别 ====================
class ShouruLeibieBase(BaseModel):
    """收入类别基础模式"""
    mingcheng: str = Field(..., min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class ShouruLeibieCreate(ShouruLeibieBase):
    """创建收入类别模式"""
    pass

class ShouruLeibieUpdate(BaseModel):
    """更新收入类别模式"""
    mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")

class ShouruLeibieResponse(ShouruLeibieBase):
    """收入类别响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ShouruLeibieListResponse(BaseModel):
    """收入类别列表响应"""
    items: List[ShouruLeibieResponse]
    total: int
    page: int
    size: int
    pages: int

# ==================== 报销类别 ====================
class BaoxiaoLeibieBase(BaseModel):
    """报销类别基础模式"""
    mingcheng: str = Field(..., min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class BaoxiaoLeibieCreate(BaoxiaoLeibieBase):
    """创建报销类别模式"""
    pass

class BaoxiaoLeibieUpdate(BaseModel):
    """更新报销类别模式"""
    mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")

class BaoxiaoLeibieResponse(BaoxiaoLeibieBase):
    """报销类别响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BaoxiaoLeibieListResponse(BaseModel):
    """报销类别列表响应"""
    items: List[BaoxiaoLeibieResponse]
    total: int
    page: int
    size: int
    pages: int

# ==================== 支出类别 ====================
class ZhichuLeibieBase(BaseModel):
    """支出类别基础模式"""
    mingcheng: str = Field(..., min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    fenlei: Optional[str] = Field(None, max_length=100, description="分类（一级分类）")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态")

class ZhichuLeibieCreate(ZhichuLeibieBase):
    """创建支出类别模式"""
    pass

class ZhichuLeibieUpdate(BaseModel):
    """更新支出类别模式"""
    mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="类别名称")
    bianma: Optional[str] = Field(None, max_length=50, description="类别编码")
    fenlei: Optional[str] = Field(None, max_length=100, description="分类（一级分类）")
    miaoshu: Optional[str] = Field(None, description="描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")

class ZhichuLeibieResponse(ZhichuLeibieBase):
    """支出类别响应模式"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ZhichuLeibieListResponse(BaseModel):
    """支出类别列表响应"""
    items: List[ZhichuLeibieResponse]
    total: int
    page: int
    size: int
    pages: int
