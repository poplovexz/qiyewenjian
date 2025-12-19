"""
支付回调日志相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ZhifuHuidiaoRizhiCreate(BaseModel):
    """创建回调日志请求"""
    zhifu_peizhi_id: Optional[str] = Field(None, description="支付配置ID")
    huidiao_leixing: str = Field(..., description="回调类型：zhifu/tuikuan")
    zhifu_pingtai: str = Field(..., description="支付平台：weixin/zhifubao")
    qingqiu_url: Optional[str] = Field(None, description="请求URL")
    qingqiu_fangfa: Optional[str] = Field(None, description="请求方法")
    qingqiu_tou: Optional[str] = Field(None, description="请求头JSON")
    qingqiu_shuju: Optional[str] = Field(None, description="请求数据JSON")
    qianming: Optional[str] = Field(None, description="签名")
    qianming_yanzheng: Optional[str] = Field(None, description="签名验证结果")
    chuli_zhuangtai: Optional[str] = Field(None, description="处理状态")
    chuli_jieguo: Optional[str] = Field(None, description="处理结果")
    cuowu_xinxi: Optional[str] = Field(None, description="错误信息")
    jieshou_shijian: Optional[datetime] = Field(None, description="接收时间")
    chuli_shijian: Optional[datetime] = Field(None, description="处理时间")

class ZhifuHuidiaoRizhiResponse(BaseModel):
    """回调日志响应"""
    id: str
    zhifu_peizhi_id: Optional[str]
    huidiao_leixing: str
    zhifu_pingtai: str
    qingqiu_url: Optional[str]
    qingqiu_fangfa: Optional[str]
    qingqiu_tou: Optional[str]
    qingqiu_shuju: Optional[str]
    qianming: Optional[str]
    qianming_yanzheng: Optional[str]
    chuli_zhuangtai: Optional[str]
    chuli_jieguo: Optional[str]
    cuowu_xinxi: Optional[str]
    jieshou_shijian: Optional[datetime]
    chuli_shijian: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ZhifuHuidiaoRizhiListResponse(BaseModel):
    """回调日志列表响应"""
    total: int
    items: list[ZhifuHuidiaoRizhiResponse]
    page: int
    page_size: int
