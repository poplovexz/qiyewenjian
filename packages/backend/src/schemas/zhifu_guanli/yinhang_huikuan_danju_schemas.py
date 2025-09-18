"""
银行汇款单据数据模式
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class YinhangHuikuanDanjuBase(BaseModel):
    """银行汇款单据基础模型"""
    hetong_zhifu_id: str = Field(..., description="合同支付ID")
    danju_lujing: str = Field(..., description="单据文件路径")
    danju_mingcheng: Optional[str] = Field(None, description="单据文件名称")
    huikuan_jine: Decimal = Field(..., description="汇款金额")
    huikuan_riqi: datetime = Field(..., description="汇款日期")
    huikuan_ren: str = Field(..., description="汇款人")
    huikuan_yinhang: Optional[str] = Field(None, description="汇款银行")
    huikuan_zhanghu: Optional[str] = Field(None, description="汇款账户")
    beizhu: Optional[str] = Field(None, description="备注")


class YinhangHuikuanDanjuCreate(YinhangHuikuanDanjuBase):
    """创建银行汇款单据模型"""
    pass


class YinhangHuikuanDanjuUpdate(BaseModel):
    """更新银行汇款单据模型"""
    danju_lujing: Optional[str] = Field(None, description="单据文件路径")
    danju_mingcheng: Optional[str] = Field(None, description="单据文件名称")
    huikuan_jine: Optional[Decimal] = Field(None, description="汇款金额")
    huikuan_riqi: Optional[datetime] = Field(None, description="汇款日期")
    huikuan_ren: Optional[str] = Field(None, description="汇款人")
    huikuan_yinhang: Optional[str] = Field(None, description="汇款银行")
    huikuan_zhanghu: Optional[str] = Field(None, description="汇款账户")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态")
    shenhe_yijian: Optional[str] = Field(None, description="审核意见")
    beizhu: Optional[str] = Field(None, description="备注")


class YinhangHuikuanDanjuResponse(BaseModel):
    """银行汇款单据响应模型"""
    id: str
    hetong_zhifu_id: str
    danju_bianhao: str
    danju_lujing: str
    danju_mingcheng: Optional[str]
    huikuan_jine: Decimal
    huikuan_riqi: datetime
    huikuan_ren: str
    huikuan_yinhang: Optional[str]
    huikuan_zhanghu: Optional[str]
    shangchuan_ren_id: str
    shangchuan_shijian: Optional[datetime]
    shenhe_zhuangtai: str
    shenhe_ren_id: Optional[str]
    shenhe_shijian: Optional[datetime]
    shenhe_yijian: Optional[str]
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class YinhangHuikuanDanjuListParams(BaseModel):
    """银行汇款单据列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    hetong_zhifu_id: Optional[str] = Field(None, description="合同支付ID筛选")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    shangchuan_ren_id: Optional[str] = Field(None, description="上传人筛选")
    shenhe_ren_id: Optional[str] = Field(None, description="审核人筛选")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向")


class HuikuanDanjuAuditRequest(BaseModel):
    """汇款单据审核请求模型"""
    shenhe_jieguo: str = Field(..., description="审核结果：tongguo、jujue")
    shenhe_yijian: Optional[str] = Field(None, description="审核意见")
