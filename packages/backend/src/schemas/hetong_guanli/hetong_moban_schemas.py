"""
合同模板相关的 Pydantic 模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class HetongMobanBase(BaseModel):
    """合同模板基础模型"""
    moban_mingcheng: str = Field(..., min_length=1, max_length=200, description="模板名称")
    moban_bianma: str = Field(..., min_length=1, max_length=100, description="模板编码")
    hetong_leixing: str = Field(..., description="合同类型")
    moban_neirong: str = Field(..., min_length=1, description="模板内容")
    bianliang_peizhi: Optional[str] = Field(None, description="变量配置（JSON格式）")
    banben_hao: str = Field(default="1.0", max_length=20, description="版本号")
    shi_dangqian_banben: str = Field(default="Y", description="是否当前版本")
    moban_fenlei: Optional[str] = Field(None, max_length=50, description="模板分类")
    moban_zhuangtai: str = Field(default="draft", description="模板状态")
    beizhu: Optional[str] = Field(None, description="备注")
    paixu: int = Field(default=0, description="排序号")

    @validator('hetong_leixing')
    def validate_hetong_leixing(cls, v):
        allowed_types = ['daili_jizhang', 'zengzhi_fuwu', 'zixun_fuwu']
        if v not in allowed_types:
            raise ValueError(f'合同类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('moban_zhuangtai')
    def validate_moban_zhuangtai(cls, v):
        allowed_states = ['draft', 'active', 'archived']
        if v not in allowed_states:
            raise ValueError(f'模板状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('shi_dangqian_banben')
    def validate_shi_dangqian_banben(cls, v):
        if v not in ['Y', 'N']:
            raise ValueError('是否当前版本必须是Y或N')
        return v

class HetongMobanCreate(HetongMobanBase):
    """创建合同模板的请求模型"""
    pass

class HetongMobanUpdate(BaseModel):
    """更新合同模板的请求模型"""
    moban_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="模板名称")
    moban_bianma: Optional[str] = Field(None, min_length=1, max_length=100, description="模板编码")
    hetong_leixing: Optional[str] = Field(None, description="合同类型")
    moban_neirong: Optional[str] = Field(None, min_length=1, description="模板内容")
    bianliang_peizhi: Optional[str] = Field(None, description="变量配置（JSON格式）")
    banben_hao: Optional[str] = Field(None, max_length=20, description="版本号")
    shi_dangqian_banben: Optional[str] = Field(None, description="是否当前版本")
    moban_fenlei: Optional[str] = Field(None, max_length=50, description="模板分类")
    moban_zhuangtai: Optional[str] = Field(None, description="模板状态")
    beizhu: Optional[str] = Field(None, description="备注")
    paixu: Optional[int] = Field(None, description="排序号")

    @validator('hetong_leixing')
    def validate_hetong_leixing(cls, v):
        if v is not None:
            allowed_types = ['daili_jizhang', 'zengzhi_fuwu', 'zixun_fuwu']
            if v not in allowed_types:
                raise ValueError(f'合同类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('moban_zhuangtai')
    def validate_moban_zhuangtai(cls, v):
        if v is not None:
            allowed_states = ['draft', 'active', 'archived']
            if v not in allowed_states:
                raise ValueError(f'模板状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('shi_dangqian_banben')
    def validate_shi_dangqian_banben(cls, v):
        if v is not None and v not in ['Y', 'N']:
            raise ValueError('是否当前版本必须是Y或N')
        return v

class HetongMobanResponse(BaseModel):
    """合同模板响应模型"""
    id: str
    moban_mingcheng: str
    moban_bianma: Optional[str]
    hetong_leixing: str
    moban_neirong: str
    bianliang_peizhi: Optional[str]
    banben_hao: str
    shi_dangqian_banben: str
    moban_fenlei: Optional[str]
    moban_zhuangtai: str
    shiyong_cishu: int
    shenpi_zhuangtai: str
    shenpi_ren: Optional[str]
    shenpi_shijian: Optional[datetime]
    shenpi_yijian: Optional[str]
    beizhu: Optional[str]
    paixu: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

class HetongMobanListResponse(BaseModel):
    """合同模板列表响应模型"""
    total: int
    items: List[HetongMobanResponse]
    page: int
    size: int

class HetongMobanPreview(BaseModel):
    """合同模板预览模型"""
    moban_id: str
    bianliang_zhis: Dict[str, Any] = Field(..., description="变量值映射")
    
    class Config:
        schema_extra = {
            "example": {
                "moban_id": "123e4567-e89b-12d3-a456-426614174000",
                "bianliang_zhis": {
                    "kehu_mingcheng": "测试公司",
                    "fuwu_neirong": "代理记账服务",
                    "fuwu_jiage": "2000.00",
                    "hetong_qixian": "12个月"
                }
            }
        }
