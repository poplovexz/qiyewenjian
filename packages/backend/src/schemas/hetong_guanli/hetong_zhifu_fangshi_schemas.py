"""
合同支付方式相关的Pydantic模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict


# 简化的关联对象Schema
class YifangZhutiSimple(BaseModel):
    """乙方主体简化信息"""
    id: str
    zhuti_mingcheng: str

    model_config = ConfigDict(from_attributes=True)


class ZhifuPeizhiSimple(BaseModel):
    """支付配置简化信息"""
    id: str
    peizhi_mingcheng: str
    peizhi_leixing: str

    model_config = ConfigDict(from_attributes=True)


class HetongZhifuFangshiBase(BaseModel):
    """合同支付方式基础模型 - 关联到支付配置"""
    yifang_zhuti_id: str = Field(..., description="乙方主体ID")
    zhifu_peizhi_id: str = Field(..., description="支付配置ID - 关联到支付配置管理")
    zhifu_mingcheng: str = Field(..., min_length=1, max_length=100, description="支付方式名称")
    zhifu_zhuangtai: str = Field(default="active", description="支付状态")
    shi_moren: str = Field(default="N", description="是否默认")
    paixu: str = Field(default="0", description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")

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
    zhifu_peizhi_id: Optional[str] = Field(None, description="支付配置ID")
    zhifu_mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="支付方式名称")
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态")
    shi_moren: Optional[str] = Field(None, description="是否默认")
    paixu: Optional[str] = Field(None, description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")

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
    zhifu_peizhi_id: str
    zhifu_mingcheng: str
    zhifu_zhuangtai: str
    shi_moren: str
    paixu: str
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    # 关联对象
    yifang_zhuti: Optional[YifangZhutiSimple] = None  # 乙方主体信息
    zhifu_peizhi: Optional[ZhifuPeizhiSimple] = None  # 支付配置信息

    model_config = ConfigDict(from_attributes=True)


class HetongZhifuFangshiListResponse(BaseModel):
    """合同支付方式列表响应模型"""
    total: int
    items: List[HetongZhifuFangshiResponse]
    page: int
    size: int
