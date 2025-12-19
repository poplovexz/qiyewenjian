"""
服务记录管理 Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class FuwuJiluBase(BaseModel):
    """服务记录基础模型"""
    kehu_id: str = Field(..., description="客户ID")
    
    # 沟通记录
    goutong_fangshi: str = Field(..., description="沟通方式")
    goutong_neirong: str = Field(..., min_length=1, description="沟通内容")
    goutong_shijian: str = Field(..., description="沟通时间")
    
    # 问题处理
    wenti_leixing: Optional[str] = Field(None, description="问题类型")
    wenti_miaoshu: Optional[str] = Field(None, description="问题描述")
    chuli_zhuangtai: str = Field(default="pending", description="处理状态")
    chuli_jieguo: Optional[str] = Field(None, description="处理结果")
    chuli_ren_id: Optional[str] = Field(None, description="处理人ID")
    
    @field_validator("goutong_fangshi")
    @classmethod
    def validate_communication_method(cls, v: str) -> str:
        """验证沟通方式"""
        allowed_methods = ["phone", "email", "online", "meeting"]
        if v not in allowed_methods:
            raise ValueError(f'沟通方式必须是以下之一: {", ".join(allowed_methods)}')
        return v
    
    @field_validator("wenti_leixing")
    @classmethod
    def validate_problem_type(cls, v: Optional[str]) -> Optional[str]:
        """验证问题类型"""
        if v is not None:
            allowed_types = ["zhangwu", "shuiwu", "zixun", "other"]
            if v not in allowed_types:
                raise ValueError(f'问题类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    @field_validator("chuli_zhuangtai")
    @classmethod
    def validate_processing_status(cls, v: str) -> str:
        """验证处理状态"""
        allowed_statuses = ["pending", "processing", "completed", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f'处理状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

class FuwuJiluCreate(FuwuJiluBase):
    """创建服务记录模型"""
    pass

class FuwuJiluUpdate(BaseModel):
    """更新服务记录模型"""
    # 沟通记录
    goutong_fangshi: Optional[str] = Field(None, description="沟通方式")
    goutong_neirong: Optional[str] = Field(None, min_length=1, description="沟通内容")
    goutong_shijian: Optional[str] = Field(None, description="沟通时间")
    
    # 问题处理
    wenti_leixing: Optional[str] = Field(None, description="问题类型")
    wenti_miaoshu: Optional[str] = Field(None, description="问题描述")
    chuli_zhuangtai: Optional[str] = Field(None, description="处理状态")
    chuli_jieguo: Optional[str] = Field(None, description="处理结果")
    chuli_ren_id: Optional[str] = Field(None, description="处理人ID")

class FuwuJiluResponse(FuwuJiluBase):
    """服务记录响应模型"""
    id: str = Field(..., description="服务记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人ID")
    
    class Config:
        from_attributes = True

class FuwuJiluListResponse(BaseModel):
    """服务记录列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[FuwuJiluResponse] = Field(..., description="服务记录列表")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    
    class Config:
        from_attributes = True
