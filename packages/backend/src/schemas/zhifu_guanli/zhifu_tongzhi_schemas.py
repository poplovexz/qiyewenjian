"""
支付通知相关的 Pydantic 模式
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ZhifuTongzhiCreate(BaseModel):
    """创建支付通知的请求模式"""
    zhifu_dingdan_id: Optional[str] = Field(None, description="支付订单ID")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    jieshou_ren_id: str = Field(..., description="接收人ID")
    tongzhi_leixing: str = Field(..., description="通知类型")
    tongzhi_biaoti: str = Field(..., min_length=1, max_length=200, description="通知标题")
    tongzhi_neirong: str = Field(..., min_length=1, description="通知内容")
    youxian_ji: str = Field("normal", description="优先级")
    fasong_shijian: datetime = Field(..., description="发送时间")
    guoqi_shijian: Optional[datetime] = Field(None, description="过期时间")
    kuozhan_shuju: Optional[str] = Field(None, description="扩展数据")
    lianjie_url: Optional[str] = Field(None, description="相关链接URL")
    fasong_qudao: str = Field("system", description="发送渠道")

    @validator('tongzhi_leixing')
    def validate_tongzhi_leixing(cls, v):
        allowed_types = ['payment_success', 'payment_failed', 'contract_signed', 'invoice_generated', 'task_assigned']
        if v not in allowed_types:
            raise ValueError(f'通知类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('youxian_ji')
    def validate_youxian_ji(cls, v):
        allowed_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in allowed_priorities:
            raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v

    @validator('fasong_qudao')
    def validate_fasong_qudao(cls, v):
        allowed_channels = ['system', 'email', 'sms', 'wechat']
        if v not in allowed_channels:
            raise ValueError(f'发送渠道必须是以下之一: {", ".join(allowed_channels)}')
        return v


class ZhifuTongzhiUpdate(BaseModel):
    """更新支付通知的请求模式"""
    tongzhi_biaoti: Optional[str] = Field(None, min_length=1, max_length=200, description="通知标题")
    tongzhi_neirong: Optional[str] = Field(None, min_length=1, description="通知内容")
    tongzhi_zhuangtai: Optional[str] = Field(None, description="通知状态")
    youxian_ji: Optional[str] = Field(None, description="优先级")
    yuedu_shijian: Optional[datetime] = Field(None, description="阅读时间")
    guoqi_shijian: Optional[datetime] = Field(None, description="过期时间")
    kuozhan_shuju: Optional[str] = Field(None, description="扩展数据")
    lianjie_url: Optional[str] = Field(None, description="相关链接URL")

    @validator('tongzhi_zhuangtai')
    def validate_tongzhi_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['unread', 'read', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'通知状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('youxian_ji')
    def validate_youxian_ji(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'normal', 'high', 'urgent']
            if v not in allowed_priorities:
                raise ValueError(f'优先级必须是以下之一: {", ".join(allowed_priorities)}')
        return v


class ZhifuTongzhiResponse(BaseModel):
    """支付通知响应模式"""
    id: str
    zhifu_dingdan_id: Optional[str]
    hetong_id: Optional[str]
    jieshou_ren_id: str
    tongzhi_leixing: str
    tongzhi_biaoti: str
    tongzhi_neirong: str
    tongzhi_zhuangtai: str
    youxian_ji: str
    fasong_shijian: datetime
    yuedu_shijian: Optional[datetime]
    guoqi_shijian: Optional[datetime]
    kuozhan_shuju: Optional[str]
    lianjie_url: Optional[str]
    fasong_qudao: str
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class ZhifuTongzhiListParams(BaseModel):
    """支付通知列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    jieshou_ren_id: Optional[str] = Field(None, description="接收人ID")
    tongzhi_leixing: Optional[str] = Field(None, description="通知类型")
    tongzhi_zhuangtai: Optional[str] = Field(None, description="通知状态")
    youxian_ji: Optional[str] = Field(None, description="优先级")
    fasong_qudao: Optional[str] = Field(None, description="发送渠道")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class ZhifuTongzhiListResponse(BaseModel):
    """支付通知列表响应模式"""
    total: int
    items: List[ZhifuTongzhiResponse]
    page: int
    size: int
