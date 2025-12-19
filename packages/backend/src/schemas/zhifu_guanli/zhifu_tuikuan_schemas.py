"""
退款记录相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ZhifuTuikuanCreate(BaseModel):
    """创建退款请求"""
    zhifu_dingdan_id: str = Field(..., description="支付订单ID")
    tuikuan_jine: Decimal = Field(..., description="退款金额")
    tuikuan_yuanyin: Optional[str] = Field(None, description="退款原因")

class ZhifuTuikuanResponse(BaseModel):
    """退款记录响应"""
    id: str
    zhifu_dingdan_id: str
    zhifu_peizhi_id: Optional[str]
    tuikuan_danhao: str
    yuanshi_dingdan_hao: str
    disanfang_tuikuan_hao: Optional[str]
    yuanshi_jine: Decimal
    tuikuan_jine: Decimal
    tuikuan_yuanyin: Optional[str]
    tuikuan_zhuangtai: str
    tuikuan_pingtai: str
    shenqing_shijian: Optional[datetime]
    chenggong_shijian: Optional[datetime]
    daozhang_shijian: Optional[datetime]
    chuli_jieguo: Optional[str]
    cuowu_xinxi: Optional[str]
    cuowu_daima: Optional[str]
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ZhifuTuikuanListResponse(BaseModel):
    """退款记录列表响应"""
    total: int
    items: list[ZhifuTuikuanResponse]
    page: int
    page_size: int
