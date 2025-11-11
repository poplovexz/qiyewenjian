"""
对外付款申请数据模式
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class DuiwaiFukuanShenqingBase(BaseModel):
    """对外付款申请基础模式"""
    fukuan_duixiang: str = Field(..., description="付款对象")
    fukuan_jine: Decimal = Field(..., description="付款金额")
    fukuan_yuanyin: str = Field(..., description="付款原因")
    fukuan_fangshi: str = Field(..., description="付款方式")
    shoukuan_zhanghu: str = Field(..., description="收款账户信息")
    shoukuan_yinhang: Optional[str] = Field(None, description="收款银行")
    yaoqiu_fukuan_shijian: Optional[datetime] = Field(None, description="要求付款时间")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")


class DuiwaiFukuanShenqingCreate(DuiwaiFukuanShenqingBase):
    """创建对外付款申请模式"""
    pass


class DuiwaiFukuanShenqingUpdate(BaseModel):
    """更新对外付款申请模式"""
    fukuan_duixiang: Optional[str] = Field(None, description="付款对象")
    fukuan_jine: Optional[Decimal] = Field(None, description="付款金额")
    fukuan_yuanyin: Optional[str] = Field(None, description="付款原因")
    fukuan_fangshi: Optional[str] = Field(None, description="付款方式")
    shoukuan_zhanghu: Optional[str] = Field(None, description="收款账户信息")
    shoukuan_yinhang: Optional[str] = Field(None, description="收款银行")
    yaoqiu_fukuan_shijian: Optional[datetime] = Field(None, description="要求付款时间")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")
    fukuan_zhuangtai: Optional[str] = Field(None, description="付款状态")
    shiji_fukuan_shijian: Optional[datetime] = Field(None, description="实际付款时间")
    fukuan_liushui_hao: Optional[str] = Field(None, description="付款流水号")


class DuiwaiFukuanShenqingResponse(DuiwaiFukuanShenqingBase):
    """对外付款申请响应模式"""
    id: str
    shenqing_bianhao: str
    shenqing_ren_id: str
    shenhe_zhuangtai: str
    shenhe_liucheng_id: Optional[str]
    fukuan_zhuangtai: str
    shiji_fukuan_shijian: Optional[datetime]
    fukuan_liushui_hao: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    shenqing_ren_xingming: Optional[str] = Field(None, description="申请人姓名")
    
    class Config:
        from_attributes = True


class DuiwaiFukuanShenqingListParams(BaseModel):
    """对外付款申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    fukuan_zhuangtai: Optional[str] = Field(None, description="付款状态筛选")
    shenqing_ren_id: Optional[str] = Field(None, description="申请人ID筛选")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")

