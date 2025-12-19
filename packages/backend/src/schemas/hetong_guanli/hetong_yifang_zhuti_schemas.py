"""
合同乙方主体相关的Pydantic模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class HetongYifangZhutiBase(BaseModel):
    """合同乙方主体基础模型"""
    zhuti_mingcheng: str = Field(..., min_length=1, max_length=200, description="主体名称")
    zhuti_leixing: str = Field(..., description="主体类型")
    lianxi_ren: str = Field(..., min_length=1, max_length=100, description="联系人")
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    tongxin_dizhi: Optional[str] = Field(None, max_length=500, description="通信地址")
    zhengjianhao: Optional[str] = Field(None, max_length=100, description="证件号码")
    zhengjianleixing: Optional[str] = Field(None, description="证件类型")
    kaihuhang: Optional[str] = Field(None, max_length=200, description="开户行")
    yinhangzhanghu: Optional[str] = Field(None, max_length=50, description="银行账户")
    zhuti_zhuangtai: str = Field(default="active", description="主体状态")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhuti_leixing')
    def validate_zhuti_leixing(cls, v):
        allowed_types = ['geren', 'gongsi', 'hehuo', 'qita']
        if v not in allowed_types:
            raise ValueError(f'主体类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhengjianleixing')
    def validate_zhengjianleixing(cls, v):
        if v is not None:
            allowed_types = ['shenfenzheng', 'yingyezhizhao', 'qita']
            if v not in allowed_types:
                raise ValueError(f'证件类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhuti_zhuangtai')
    def validate_zhuti_zhuangtai(cls, v):
        allowed_states = ['active', 'inactive']
        if v not in allowed_states:
            raise ValueError(f'主体状态必须是以下之一: {", ".join(allowed_states)}')
        return v

class HetongYifangZhutiCreate(HetongYifangZhutiBase):
    """创建合同乙方主体的请求模型"""
    pass

class HetongYifangZhutiUpdate(BaseModel):
    """更新合同乙方主体的请求模型"""
    zhuti_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="主体名称")
    zhuti_leixing: Optional[str] = Field(None, description="主体类型")
    lianxi_ren: Optional[str] = Field(None, min_length=1, max_length=100, description="联系人")
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    tongxin_dizhi: Optional[str] = Field(None, max_length=500, description="通信地址")
    zhengjianhao: Optional[str] = Field(None, max_length=100, description="证件号码")
    zhengjianleixing: Optional[str] = Field(None, description="证件类型")
    kaihuhang: Optional[str] = Field(None, max_length=200, description="开户行")
    yinhangzhanghu: Optional[str] = Field(None, max_length=50, description="银行账户")
    zhuti_zhuangtai: Optional[str] = Field(None, description="主体状态")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhuti_leixing')
    def validate_zhuti_leixing(cls, v):
        if v is not None:
            allowed_types = ['geren', 'gongsi', 'hehuo', 'qita']
            if v not in allowed_types:
                raise ValueError(f'主体类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhengjianleixing')
    def validate_zhengjianleixing(cls, v):
        if v is not None:
            allowed_types = ['shenfenzheng', 'yingyezhizhao', 'qita']
            if v not in allowed_types:
                raise ValueError(f'证件类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhuti_zhuangtai')
    def validate_zhuti_zhuangtai(cls, v):
        if v is not None:
            allowed_states = ['active', 'inactive']
            if v not in allowed_states:
                raise ValueError(f'主体状态必须是以下之一: {", ".join(allowed_states)}')
        return v

class HetongYifangZhutiResponse(BaseModel):
    """合同乙方主体响应模型"""
    id: str
    zhuti_mingcheng: str
    zhuti_leixing: str
    lianxi_ren: str
    lianxi_dianhua: Optional[str]
    lianxi_youxiang: Optional[str]
    zhuce_dizhi: Optional[str]
    tongxin_dizhi: Optional[str]
    zhengjianhao: Optional[str]
    zhengjianleixing: Optional[str]
    kaihuhang: Optional[str]
    yinhangzhanghu: Optional[str]
    zhuti_zhuangtai: str
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

class HetongYifangZhutiListResponse(BaseModel):
    """合同乙方主体列表响应模型"""
    total: int
    items: List[HetongYifangZhutiResponse]
    page: int
    size: int
