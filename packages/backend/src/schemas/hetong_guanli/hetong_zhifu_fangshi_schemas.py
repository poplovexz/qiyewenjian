"""
合同支付方式相关的Pydantic模型
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class HetongZhifuFangshiBase(BaseModel):
    """合同支付方式基础模型"""
    yifang_zhuti_id: str = Field(..., description="乙方主体ID")
    zhifu_leixing: str = Field(..., description="支付类型")
    zhifu_mingcheng: str = Field(..., min_length=1, max_length=100, description="支付方式名称")
    zhanghu_mingcheng: Optional[str] = Field(None, max_length=100, description="账户名称")
    zhanghu_haoma: Optional[str] = Field(None, max_length=100, description="账户号码")
    kaihuhang_mingcheng: Optional[str] = Field(None, max_length=200, description="开户行名称")
    kaihuhang_dizhi: Optional[str] = Field(None, max_length=300, description="开户行地址")
    lianhanghao: Optional[str] = Field(None, max_length=50, description="联行号")
    danbi_xiange: Optional[Decimal] = Field(None, description="单笔限额")
    riqi_xiange: Optional[Decimal] = Field(None, description="日期限额")
    zhifu_zhuangtai: str = Field(default="active", description="支付状态")
    shi_moren: str = Field(default="N", description="是否默认")
    paixu: str = Field(default="0", description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhifu_leixing')
    def validate_zhifu_leixing(cls, v):
        allowed_types = ['weixin', 'zhifubao', 'yinhangzhuanzhang', 'xianjin', 'qita']
        if v not in allowed_types:
            raise ValueError(f'支付类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhifu_zhuangtai')
    def validate_zhifu_zhuangtai(cls, v):
        allowed_states = ['active', 'inactive']
        if v not in allowed_states:
            raise ValueError(f'支付状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('shi_moren')
    def validate_shi_moren(cls, v):
        if v not in ['Y', 'N']:
            raise ValueError('是否默认必须是Y或N')
        return v


class HetongZhifuFangshiCreate(HetongZhifuFangshiBase):
    """创建合同支付方式的请求模型"""
    pass


class HetongZhifuFangshiUpdate(BaseModel):
    """更新合同支付方式的请求模型"""
    zhifu_leixing: Optional[str] = Field(None, description="支付类型")
    zhifu_mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="支付方式名称")
    zhanghu_mingcheng: Optional[str] = Field(None, max_length=100, description="账户名称")
    zhanghu_haoma: Optional[str] = Field(None, max_length=100, description="账户号码")
    kaihuhang_mingcheng: Optional[str] = Field(None, max_length=200, description="开户行名称")
    kaihuhang_dizhi: Optional[str] = Field(None, max_length=300, description="开户行地址")
    lianhanghao: Optional[str] = Field(None, max_length=50, description="联行号")
    danbi_xiange: Optional[Decimal] = Field(None, description="单笔限额")
    riqi_xiange: Optional[Decimal] = Field(None, description="日期限额")
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态")
    shi_moren: Optional[str] = Field(None, description="是否默认")
    paixu: Optional[str] = Field(None, description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhifu_leixing')
    def validate_zhifu_leixing(cls, v):
        if v is not None:
            allowed_types = ['weixin', 'zhifubao', 'yinhangzhuanzhang', 'xianjin', 'qita']
            if v not in allowed_types:
                raise ValueError(f'支付类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhifu_zhuangtai')
    def validate_zhifu_zhuangtai(cls, v):
        if v is not None:
            allowed_states = ['active', 'inactive']
            if v not in allowed_states:
                raise ValueError(f'支付状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('shi_moren')
    def validate_shi_moren(cls, v):
        if v is not None and v not in ['Y', 'N']:
            raise ValueError('是否默认必须是Y或N')
        return v


class HetongZhifuFangshiResponse(BaseModel):
    """合同支付方式响应模型"""
    id: str
    yifang_zhuti_id: str
    zhifu_leixing: str
    zhifu_mingcheng: str
    zhanghu_mingcheng: Optional[str]
    zhanghu_haoma: Optional[str]
    kaihuhang_mingcheng: Optional[str]
    kaihuhang_dizhi: Optional[str]
    lianhanghao: Optional[str]
    danbi_xiange: Optional[Decimal]
    riqi_xiange: Optional[Decimal]
    zhifu_zhuangtai: str
    shi_moren: str
    paixu: str
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class HetongZhifuFangshiListResponse(BaseModel):
    """合同支付方式列表响应模型"""
    total: int
    items: List[HetongZhifuFangshiResponse]
    page: int
    size: int
