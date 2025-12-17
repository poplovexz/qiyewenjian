"""
报销申请数据模式
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class BaoxiaoShenqingBase(BaseModel):
    """报销申请基础模式"""
    baoxiao_leixing: str = Field(..., description="报销类型")
    baoxiao_jine: Decimal = Field(..., description="报销金额")
    baoxiao_shijian: datetime = Field(..., description="报销事项发生时间")
    baoxiao_yuanyin: str = Field(..., description="报销原因说明")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class BaoxiaoShenqingCreate(BaoxiaoShenqingBase):
    """创建报销申请模式"""
    pass


class BaoxiaoShenqingUpdate(BaseModel):
    """更新报销申请模式"""
    baoxiao_leixing: Optional[str] = Field(None, description="报销类型")
    baoxiao_jine: Optional[Decimal] = Field(None, description="报销金额")
    baoxiao_shijian: Optional[datetime] = Field(None, description="报销事项发生时间")
    baoxiao_yuanyin: Optional[str] = Field(None, description="报销原因说明")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class BaoxiaoShenqingResponse(BaoxiaoShenqingBase):
    """报销申请响应模式"""
    id: str
    shenqing_bianhao: str
    shenqing_ren_id: str
    shenhe_zhuangtai: str
    shenhe_liucheng_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    shenqing_ren_xingming: Optional[str] = Field(None, description="申请人姓名")
    
    class Config:
        from_attributes = True


class BaoxiaoShenqingListParams(BaseModel):
    """报销申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    baoxiao_leixing: Optional[str] = Field(None, description="报销类型筛选")
    shenqing_ren_id: Optional[str] = Field(None, description="申请人ID筛选")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")

