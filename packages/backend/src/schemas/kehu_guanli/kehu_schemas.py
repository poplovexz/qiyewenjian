"""
客户管理 Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re

class KehuBase(BaseModel):
    """客户基础模型"""
    gongsi_mingcheng: str = Field(..., min_length=1, max_length=200, description="公司名称")
    tongyi_shehui_xinyong_daima: str = Field(..., min_length=18, max_length=18, description="统一社会信用代码")
    chengli_riqi: Optional[datetime] = Field(None, description="成立日期")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    
    # 法人信息
    faren_xingming: str = Field(..., min_length=1, max_length=50, description="法人姓名")
    faren_shenfenzheng: Optional[str] = Field(None, min_length=18, max_length=18, description="法人身份证号码")
    faren_lianxi: Optional[str] = Field(None, max_length=20, description="法人联系方式")
    
    # 联系信息
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    lianxi_dizhi: Optional[str] = Field(None, max_length=500, description="联系地址")
    
    # 营业执照信息
    yingye_zhizhao_lujing: Optional[str] = Field(None, max_length=500, description="营业执照文件路径")
    yingye_zhizhao_youxiao_qi: Optional[datetime] = Field(None, description="营业执照有效期")
    
    # 状态信息
    kehu_zhuangtai: str = Field(default="active", description="客户状态")
    fuwu_kaishi_riqi: Optional[datetime] = Field(None, description="服务开始日期")
    fuwu_jieshu_riqi: Optional[datetime] = Field(None, description="服务结束日期")
    
    @field_validator("tongyi_shehui_xinyong_daima")
    @classmethod
    def validate_credit_code(cls, v: str) -> str:
        """验证统一社会信用代码格式"""
        # 允许临时信用代码（TEMP开头）
        if v.startswith('TEMP'):
            return v
        # 验证正式的统一社会信用代码格式
        if not re.match(r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$', v):
            raise ValueError('统一社会信用代码格式不正确')
        return v
    
    @field_validator("faren_shenfenzheng")
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        """验证身份证号码格式"""
        if v and not re.match(r'^\d{17}[\dXx]$', v):
            raise ValueError('身份证号码格式不正确')
        return v
    
    @field_validator("lianxi_youxiang")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式不正确')
        return v
    
    @field_validator("kehu_zhuangtai")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """验证客户状态"""
        allowed_statuses = ["active", "renewing", "terminated"]
        if v not in allowed_statuses:
            raise ValueError(f'客户状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

class KehuCreate(KehuBase):
    """创建客户模型"""
    pass

class KehuUpdate(BaseModel):
    """更新客户模型"""
    gongsi_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="公司名称")
    tongyi_shehui_xinyong_daima: Optional[str] = Field(None, min_length=18, max_length=18, description="统一社会信用代码")
    chengli_riqi: Optional[datetime] = Field(None, description="成立日期")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    
    # 法人信息
    faren_xingming: Optional[str] = Field(None, min_length=1, max_length=50, description="法人姓名")
    faren_shenfenzheng: Optional[str] = Field(None, min_length=18, max_length=18, description="法人身份证号码")
    faren_lianxi: Optional[str] = Field(None, max_length=20, description="法人联系方式")
    
    # 联系信息
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    lianxi_dizhi: Optional[str] = Field(None, max_length=500, description="联系地址")
    
    # 营业执照信息
    yingye_zhizhao_lujing: Optional[str] = Field(None, max_length=500, description="营业执照文件路径")
    yingye_zhizhao_youxiao_qi: Optional[datetime] = Field(None, description="营业执照有效期")
    
    # 状态信息
    kehu_zhuangtai: Optional[str] = Field(None, description="客户状态")
    fuwu_kaishi_riqi: Optional[datetime] = Field(None, description="服务开始日期")
    fuwu_jieshu_riqi: Optional[datetime] = Field(None, description="服务结束日期")

class KehuResponse(KehuBase):
    """客户响应模型"""
    id: str = Field(..., description="客户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人ID")
    
    class Config:
        from_attributes = True

class KehuListResponse(BaseModel):
    """客户列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[KehuResponse] = Field(..., description="客户列表")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    
    class Config:
        from_attributes = True
