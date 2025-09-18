"""
合同相关的Pydantic模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class HetongBase(BaseModel):
    """合同基础模型"""
    kehu_id: str = Field(..., description="客户ID")
    hetong_moban_id: str = Field(..., description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="关联报价ID")
    yifang_zhuti_id: Optional[str] = Field(None, description="乙方主体ID")
    hetong_bianhao: str = Field(..., min_length=1, max_length=50, description="合同编号")
    hetong_mingcheng: str = Field(..., min_length=1, max_length=200, description="合同名称")
    hetong_neirong: str = Field(..., min_length=1, description="合同内容")
    hetong_zhuangtai: str = Field(default="draft", description="合同状态")
    daoqi_riqi: datetime = Field(..., description="到期日期")
    shengxiao_riqi: Optional[datetime] = Field(None, description="生效日期")
    hetong_laiyuan: str = Field(default="manual", description="合同来源")
    zidong_shengcheng: str = Field(default="N", description="是否自动生成")

    @validator('hetong_zhuangtai')
    def validate_hetong_zhuangtai(cls, v):
        allowed_states = ['draft', 'pending', 'approved', 'signed', 'expired', 'cancelled']
        if v not in allowed_states:
            raise ValueError(f'合同状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('hetong_laiyuan')
    def validate_hetong_laiyuan(cls, v):
        allowed_sources = ['manual', 'auto_from_quote']
        if v not in allowed_sources:
            raise ValueError(f'合同来源必须是以下之一: {", ".join(allowed_sources)}')
        return v

    @validator('zidong_shengcheng')
    def validate_zidong_shengcheng(cls, v):
        if v not in ['Y', 'N']:
            raise ValueError('是否自动生成必须是Y或N')
        return v


class HetongCreate(HetongBase):
    """创建合同的请求模型"""
    pass


class HetongUpdate(BaseModel):
    """更新合同的请求模型"""
    kehu_id: Optional[str] = Field(None, description="客户ID")
    hetong_moban_id: Optional[str] = Field(None, description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="关联报价ID")
    yifang_zhuti_id: Optional[str] = Field(None, description="乙方主体ID")
    hetong_bianhao: Optional[str] = Field(None, min_length=1, max_length=50, description="合同编号")
    hetong_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="合同名称")
    hetong_neirong: Optional[str] = Field(None, min_length=1, description="合同内容")
    hetong_zhuangtai: Optional[str] = Field(None, description="合同状态")
    daoqi_riqi: Optional[datetime] = Field(None, description="到期日期")
    shengxiao_riqi: Optional[datetime] = Field(None, description="生效日期")
    hetong_laiyuan: Optional[str] = Field(None, description="合同来源")
    zidong_shengcheng: Optional[str] = Field(None, description="是否自动生成")

    @validator('hetong_zhuangtai')
    def validate_hetong_zhuangtai(cls, v):
        if v is not None:
            allowed_states = ['draft', 'pending', 'approved', 'signed', 'expired', 'cancelled']
            if v not in allowed_states:
                raise ValueError(f'合同状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('hetong_laiyuan')
    def validate_hetong_laiyuan(cls, v):
        if v is not None:
            allowed_sources = ['manual', 'auto_from_quote']
            if v not in allowed_sources:
                raise ValueError(f'合同来源必须是以下之一: {", ".join(allowed_sources)}')
        return v

    @validator('zidong_shengcheng')
    def validate_zidong_shengcheng(cls, v):
        if v is not None and v not in ['Y', 'N']:
            raise ValueError('是否自动生成必须是Y或N')
        return v


class HetongSignRequest(BaseModel):
    """合同签署请求模型"""
    qianming_beizhu: Optional[str] = Field(None, description="签名备注")


class HetongResponse(BaseModel):
    """合同响应模型"""
    id: str
    kehu_id: str
    hetong_moban_id: str
    baojia_id: Optional[str]
    yifang_zhuti_id: Optional[str]
    hetong_bianhao: str
    hetong_mingcheng: str
    hetong_neirong: str
    hetong_zhuangtai: str
    qianshu_riqi: Optional[datetime]
    shengxiao_riqi: Optional[datetime]
    daoqi_riqi: datetime
    pdf_lujing: Optional[str]
    qianshu_lujing: Optional[str]
    shenpi_ren_id: Optional[str]
    shenpi_riqi: Optional[datetime]
    shenpi_yijian: Optional[str]
    dianziqianming_lujing: Optional[str]
    qianming_ren_id: Optional[str]
    qianming_shijian: Optional[datetime]
    qianming_ip: Optional[str]
    qianming_beizhu: Optional[str]
    hetong_laiyuan: str
    zidong_shengcheng: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class HetongListResponse(BaseModel):
    """合同列表响应模型"""
    total: int
    items: List[HetongResponse]
    page: int
    size: int


class HetongPreviewRequest(BaseModel):
    """合同预览请求模型"""
    hetong_moban_id: str = Field(..., description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="报价ID（用于自动填充变量）")
    bianliang_zhis: Optional[dict] = Field(None, description="变量值字典")


class HetongPreviewResponse(BaseModel):
    """合同预览响应模型"""
    hetong_neirong: str = Field(..., description="预览的合同内容")
    bianliang_list: List[str] = Field(..., description="模板中的变量列表")
