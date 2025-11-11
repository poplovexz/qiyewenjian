"""
请假申请数据模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QingjiaShenqingBase(BaseModel):
    """请假申请基础模式"""
    qingjia_leixing: str = Field(..., description="请假类型")
    kaishi_shijian: datetime = Field(..., description="开始时间")
    jieshu_shijian: datetime = Field(..., description="结束时间")
    qingjia_tianshu: int = Field(..., description="请假天数")
    qingjia_yuanyin: str = Field(..., description="请假原因")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class QingjiaShenqingCreate(QingjiaShenqingBase):
    """创建请假申请模式"""
    pass


class QingjiaShenqingUpdate(BaseModel):
    """更新请假申请模式"""
    qingjia_leixing: Optional[str] = Field(None, description="请假类型")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    qingjia_tianshu: Optional[int] = Field(None, description="请假天数")
    qingjia_yuanyin: Optional[str] = Field(None, description="请假原因")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class QingjiaShenqingResponse(QingjiaShenqingBase):
    """请假申请响应模式"""
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


class QingjiaShenqingListParams(BaseModel):
    """请假申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    qingjia_leixing: Optional[str] = Field(None, description="请假类型筛选")
    shenqing_ren_id: Optional[str] = Field(None, description="申请人ID筛选")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")

