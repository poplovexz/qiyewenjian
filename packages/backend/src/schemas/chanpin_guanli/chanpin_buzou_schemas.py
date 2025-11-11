"""
产品步骤数据验证模式
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class ChanpinBuzouBase(BaseModel):
    """产品步骤基础模式"""
    buzou_mingcheng: str = Field(..., min_length=1, max_length=200, description="步骤名称")
    xiangmu_id: str = Field(..., description="所属项目ID")
    yugu_shichang: Decimal = Field(..., gt=0, description="预估时长")
    shichang_danwei: Optional[str] = Field("tian", description="时长单位")
    buzou_feiyong: Optional[Decimal] = Field(0.00, ge=0, description="步骤费用")
    buzou_miaoshu: Optional[str] = Field(None, max_length=2000, description="步骤描述")
    paixu: Optional[int] = Field(0, ge=0, description="排序号")
    shi_bixu: Optional[str] = Field("Y", description="是否必须")
    zhuangtai: Optional[str] = Field("active", description="状态")


class ChanpinBuzouCreate(ChanpinBuzouBase):
    """创建产品步骤模式"""
    pass


class ChanpinBuzouUpdate(BaseModel):
    """更新产品步骤模式"""
    buzou_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="步骤名称")
    xiangmu_id: Optional[str] = Field(None, description="所属项目ID")
    yugu_shichang: Optional[Decimal] = Field(None, gt=0, description="预估时长")
    shichang_danwei: Optional[str] = Field(None, description="时长单位")
    buzou_feiyong: Optional[Decimal] = Field(None, ge=0, description="步骤费用")
    buzou_miaoshu: Optional[str] = Field(None, max_length=2000, description="步骤描述")
    paixu: Optional[int] = Field(None, ge=0, description="排序号")
    shi_bixu: Optional[str] = Field(None, description="是否必须")
    zhuangtai: Optional[str] = Field(None, description="状态")


class ChanpinBuzouResponse(ChanpinBuzouBase):
    """产品步骤响应模式"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else 0.0
        }


class ChanpinBuzouBatchCreate(BaseModel):
    """批量创建产品步骤模式"""
    xiangmu_id: str = Field(..., description="所属项目ID")
    buzou_list: list[ChanpinBuzouCreate] = Field(..., description="步骤列表")


class ChanpinBuzouBatchUpdate(BaseModel):
    """批量更新产品步骤模式"""
    xiangmu_id: str = Field(..., description="所属项目ID")
    buzou_list: list[dict] = Field(..., description="步骤列表（包含id的为更新，不包含id的为新增）")
