"""
线索状态相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class XiansuoZhuangtaiBase(BaseModel):
    """线索状态基础模式"""
    zhuangtai_mingcheng: str = Field(..., min_length=1, max_length=50, description="状态名称")
    zhuangtai_bianma: str = Field(..., min_length=1, max_length=50, description="状态编码")
    zhuangtai_leixing: str = Field(..., description="状态类型：initial-初始，processing-处理中，success-成功，failed-失败")
    shangyige_zhuangtai: Optional[str] = Field(None, max_length=50, description="上一个状态编码")
    xiayige_zhuangtai: Optional[str] = Field(None, max_length=500, description="下一个状态编码（多个用逗号分隔）")
    yanse_bianma: Optional[str] = Field("#409EFF", max_length=20, description="颜色编码")
    tubiao_mingcheng: Optional[str] = Field(None, max_length=50, description="图标名称")
    shi_zhongzhong_zhuangtai: Optional[str] = Field("N", description="是否终止状态 Y/N")
    shi_chenggong_zhuangtai: Optional[str] = Field("N", description="是否成功状态 Y/N")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field("active", description="状态：active-启用，inactive-停用")
    miaoshu: Optional[str] = Field(None, max_length=500, description="描述")


class XiansuoZhuangtaiCreate(XiansuoZhuangtaiBase):
    """创建线索状态模式"""
    pass


class XiansuoZhuangtaiUpdate(BaseModel):
    """更新线索状态模式"""
    zhuangtai_mingcheng: Optional[str] = Field(None, min_length=1, max_length=50, description="状态名称")
    zhuangtai_bianma: Optional[str] = Field(None, min_length=1, max_length=50, description="状态编码")
    zhuangtai_leixing: Optional[str] = Field(None, description="状态类型")
    shangyige_zhuangtai: Optional[str] = Field(None, max_length=50, description="上一个状态编码")
    xiayige_zhuangtai: Optional[str] = Field(None, max_length=500, description="下一个状态编码")
    yanse_bianma: Optional[str] = Field(None, max_length=20, description="颜色编码")
    tubiao_mingcheng: Optional[str] = Field(None, max_length=50, description="图标名称")
    shi_zhongzhong_zhuangtai: Optional[str] = Field(None, description="是否终止状态 Y/N")
    shi_chenggong_zhuangtai: Optional[str] = Field(None, description="是否成功状态 Y/N")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    zhuangtai: Optional[str] = Field(None, description="状态")
    miaoshu: Optional[str] = Field(None, max_length=500, description="描述")


class XiansuoZhuangtaiResponse(XiansuoZhuangtaiBase):
    """线索状态响应模式"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class XiansuoZhuangtaiListItem(BaseModel):
    """线索状态列表项模式"""
    id: str
    zhuangtai_mingcheng: str
    zhuangtai_bianma: str
    zhuangtai_leixing: str
    yanse_bianma: str
    tubiao_mingcheng: Optional[str]
    shi_zhongzhong_zhuangtai: str
    shi_chenggong_zhuangtai: str
    paixu: int
    zhuangtai: str
    
    class Config:
        from_attributes = True


class XiansuoZhuangtaiListResponse(BaseModel):
    """线索状态列表响应模式"""
    items: List[XiansuoZhuangtaiResponse]
    total: int
    page: int
    size: int
