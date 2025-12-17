"""
线索跟进记录相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class XiansuoGenjinBase(BaseModel):
    """线索跟进记录基础模式"""
    xiansuo_id: str = Field(..., description="线索ID")
    genjin_fangshi: str = Field(..., description="跟进方式：phone-电话，email-邮件，wechat-微信，visit-拜访，other-其他")
    genjin_neirong: str = Field(..., min_length=1, description="跟进内容")
    kehu_fankui: Optional[str] = Field(None, description="客户反馈")
    kehu_taidu: Optional[str] = Field(None, description="客户态度：positive-积极，neutral-中性，negative-消极")
    xiaci_genjin_shijian: Optional[datetime] = Field(None, description="下次跟进时间")
    xiaci_genjin_neirong: Optional[str] = Field(None, max_length=500, description="下次跟进内容计划")
    genjin_jieguo: Optional[str] = Field(None, description="跟进结果：interested-有兴趣，considering-考虑中，rejected-拒绝，no_response-无回应")
    fujian_lujing: Optional[str] = Field(None, max_length=500, description="附件路径（多个用逗号分隔）")


class XiansuoGenjinCreate(XiansuoGenjinBase):
    """创建线索跟进记录模式"""
    genjin_shijian: Optional[datetime] = Field(None, description="跟进时间（不填则为当前时间）")


class XiansuoGenjinUpdate(BaseModel):
    """更新线索跟进记录模式"""
    genjin_fangshi: Optional[str] = Field(None, description="跟进方式")
    genjin_shijian: Optional[datetime] = Field(None, description="跟进时间")
    genjin_neirong: Optional[str] = Field(None, min_length=1, description="跟进内容")
    kehu_fankui: Optional[str] = Field(None, description="客户反馈")
    kehu_taidu: Optional[str] = Field(None, description="客户态度")
    xiaci_genjin_shijian: Optional[datetime] = Field(None, description="下次跟进时间")
    xiaci_genjin_neirong: Optional[str] = Field(None, max_length=500, description="下次跟进内容计划")
    genjin_jieguo: Optional[str] = Field(None, description="跟进结果")
    fujian_lujing: Optional[str] = Field(None, max_length=500, description="附件路径")


class XiansuoGenjinResponse(XiansuoGenjinBase):
    """线索跟进记录响应模式"""
    id: str
    genjin_shijian: datetime
    genjin_ren_id: str
    genjin_ren_xingming: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class XiansuoGenjinListItem(BaseModel):
    """线索跟进记录列表项模式"""
    id: str
    xiansuo_id: str
    genjin_fangshi: str
    genjin_shijian: datetime
    genjin_neirong: str
    kehu_taidu: Optional[str]
    genjin_jieguo: Optional[str]
    genjin_ren_xingming: Optional[str]
    xiaci_genjin_shijian: Optional[datetime]
    
    class Config:
        from_attributes = True


class XiansuoGenjinListResponse(BaseModel):
    """线索跟进记录列表响应模式"""
    items: List[XiansuoGenjinResponse]
    total: int
    page: int
    size: int
