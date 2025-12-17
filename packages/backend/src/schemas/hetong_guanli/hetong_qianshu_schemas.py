"""
合同签署相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class HetongQianshuBase(BaseModel):
    """合同签署基础模型"""
    hetong_id: str = Field(..., description="合同ID")
    qianshu_lianjie: str = Field(..., description="签署链接")
    qianshu_token: str = Field(..., description="签署令牌")
    qianshu_zhuangtai: str = Field(default="pending", description="签署状态")
    qianshu_neirong: Optional[str] = Field(None, description="签署内容")
    qianshu_ip: Optional[str] = Field(None, description="签署IP地址")
    qianshu_shebei: Optional[str] = Field(None, description="签署设备信息")
    youxiao_shijian: Optional[datetime] = Field(None, description="有效时间")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('qianshu_zhuangtai')
    def validate_qianshu_zhuangtai(cls, v):
        allowed_values = ['pending', 'signed', 'expired', 'cancelled']
        if v not in allowed_values:
            raise ValueError(f'签署状态必须是以下值之一: {", ".join(allowed_values)}')
        return v


class HetongQianshuCreate(HetongQianshuBase):
    """创建合同签署请求模型"""
    pass


class HetongQianshuUpdate(BaseModel):
    """更新合同签署请求模型"""
    qianshu_zhuangtai: Optional[str] = Field(None, description="签署状态")
    qianshu_neirong: Optional[str] = Field(None, description="签署内容")
    qianshu_ip: Optional[str] = Field(None, description="签署IP地址")
    qianshu_shebei: Optional[str] = Field(None, description="签署设备信息")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('qianshu_zhuangtai')
    def validate_qianshu_zhuangtai(cls, v):
        if v is not None:
            allowed_values = ['pending', 'signed', 'expired', 'cancelled']
            if v not in allowed_values:
                raise ValueError(f'签署状态必须是以下值之一: {", ".join(allowed_values)}')
        return v


class HetongQianshuResponse(HetongQianshuBase):
    """合同签署响应模型"""
    id: str = Field(..., description="签署记录ID")
    qianshu_shijian: Optional[datetime] = Field(None, description="签署时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class HetongQianshuListResponse(BaseModel):
    """合同签署列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[HetongQianshuResponse] = Field(..., description="签署记录列表")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class HetongQianshuSignRequest(BaseModel):
    """合同签署请求模型"""
    qianshu_neirong: str = Field(..., description="签署内容（电子签名数据）")
    qianshu_ip: Optional[str] = Field(None, description="签署IP地址")
    qianshu_shebei: Optional[str] = Field(None, description="签署设备信息")


class HetongQianshuVerifyResponse(BaseModel):
    """合同签署验证响应模型"""
    valid: bool = Field(..., description="签署链接是否有效")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    qianshu_zhuangtai: Optional[str] = Field(None, description="签署状态")
    message: str = Field(..., description="验证消息")


class HetongQianshuLinkRequest(BaseModel):
    """生成签署链接请求模型"""
    hetong_id: str = Field(..., description="合同ID")
    youxiao_xiaoshi: int = Field(default=24, description="有效小时数")
    beizhu: Optional[str] = Field(None, description="备注")


class HetongQianshuLinkResponse(BaseModel):
    """生成签署链接响应模型"""
    qianshu_lianjie: str = Field(..., description="签署链接")
    qianshu_token: str = Field(..., description="签署令牌")
    youxiao_shijian: datetime = Field(..., description="有效时间")
    message: str = Field(..., description="响应消息")
