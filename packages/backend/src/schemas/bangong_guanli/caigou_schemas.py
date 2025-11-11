"""
采购申请数据模式
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class CaigouShenqingBase(BaseModel):
    """采购申请基础模式"""
    caigou_leixing: str = Field(..., description="采购类型")
    caigou_mingcheng: str = Field(..., description="采购物品名称")
    caigou_shuliang: int = Field(..., description="采购数量")
    danwei: str = Field(..., description="单位")
    yugu_jine: Decimal = Field(..., description="预估金额")
    caigou_yuanyin: str = Field(..., description="采购原因")
    yaoqiu_shijian: Optional[datetime] = Field(None, description="要求到货时间")
    gongyingshang_xinxi: Optional[str] = Field(None, description="供应商信息")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class CaigouShenqingCreate(CaigouShenqingBase):
    """创建采购申请模式"""
    pass


class CaigouShenqingUpdate(BaseModel):
    """更新采购申请模式"""
    caigou_leixing: Optional[str] = Field(None, description="采购类型")
    caigou_mingcheng: Optional[str] = Field(None, description="采购物品名称")
    caigou_shuliang: Optional[int] = Field(None, description="采购数量")
    danwei: Optional[str] = Field(None, description="单位")
    yugu_jine: Optional[Decimal] = Field(None, description="预估金额")
    shiji_jine: Optional[Decimal] = Field(None, description="实际金额")
    caigou_yuanyin: Optional[str] = Field(None, description="采购原因")
    yaoqiu_shijian: Optional[datetime] = Field(None, description="要求到货时间")
    gongyingshang_xinxi: Optional[str] = Field(None, description="供应商信息")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    caigou_zhuangtai: Optional[str] = Field(None, description="采购状态")
    beizhu: Optional[str] = Field(None, description="备注")


class CaigouShenqingResponse(CaigouShenqingBase):
    """采购申请响应模式"""
    id: str
    shenqing_bianhao: str
    shenqing_ren_id: str
    shenhe_zhuangtai: str
    shenhe_liucheng_id: Optional[str]
    caigou_zhuangtai: str
    shiji_jine: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    shenqing_ren_xingming: Optional[str] = Field(None, description="申请人姓名")
    
    class Config:
        from_attributes = True


class CaigouShenqingListParams(BaseModel):
    """采购申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    caigou_zhuangtai: Optional[str] = Field(None, description="采购状态筛选")
    caigou_leixing: Optional[str] = Field(None, description="采购类型筛选")
    shenqing_ren_id: Optional[str] = Field(None, description="申请人ID筛选")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")

