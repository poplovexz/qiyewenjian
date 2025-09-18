"""
合同支付数据模式
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class HetongZhifuBase(BaseModel):
    """合同支付基础模型"""
    hetong_id: str = Field(..., description="合同ID")
    zhifu_fangshi: str = Field(..., description="支付方式")
    zhifu_jine: Decimal = Field(..., description="支付金额")
    zhifu_beizhu: Optional[str] = Field(None, description="支付备注")


class HetongZhifuCreate(HetongZhifuBase):
    """创建合同支付模型"""
    pass


class HetongZhifuUpdate(BaseModel):
    """更新合同支付模型"""
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态")
    zhifu_liushui_hao: Optional[str] = Field(None, description="支付流水号")
    zhifu_shijian: Optional[datetime] = Field(None, description="支付时间")
    disanfang_dingdan_hao: Optional[str] = Field(None, description="第三方订单号")
    disanfang_liushui_hao: Optional[str] = Field(None, description="第三方流水号")
    zhifu_beizhu: Optional[str] = Field(None, description="支付备注")
    tuikuan_jine: Optional[Decimal] = Field(None, description="退款金额")
    tuikuan_shijian: Optional[datetime] = Field(None, description="退款时间")
    tuikuan_yuanyin: Optional[str] = Field(None, description="退款原因")


class HetongZhifuResponse(BaseModel):
    """合同支付响应模型"""
    id: str
    hetong_id: str
    zhifu_fangshi: str
    zhifu_jine: Decimal
    zhifu_zhuangtai: str
    zhifu_liushui_hao: Optional[str]
    zhifu_shijian: Optional[datetime]
    disanfang_dingdan_hao: Optional[str]
    disanfang_liushui_hao: Optional[str]
    zhifu_beizhu: Optional[str]
    tuikuan_jine: Decimal
    tuikuan_shijian: Optional[datetime]
    tuikuan_yuanyin: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class HetongZhifuListParams(BaseModel):
    """合同支付列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    hetong_id: Optional[str] = Field(None, description="合同ID筛选")
    zhifu_fangshi: Optional[str] = Field(None, description="支付方式筛选")
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态筛选")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向")
