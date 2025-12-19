"""
支付流水相关的 Pydantic 模式
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

class ZhifuLiushuiCreate(BaseModel):
    """创建支付流水的请求模式"""
    zhifu_dingdan_id: Optional[str] = Field(None, description="支付订单ID（收入流水必填）")
    kehu_id: Optional[str] = Field(None, description="客户ID（收入流水必填）")
    baoxiao_shenqing_id: Optional[str] = Field(None, description="报销申请ID（支出流水必填）")
    guanlian_leixing: str = Field("zhifu_dingdan", description="关联类型：zhifu_dingdan/baoxiao_shenqing")
    liushui_leixing: str = Field(..., description="流水类型")
    jiaoyijine: Decimal = Field(..., gt=0, description="交易金额")
    shouxufei: Decimal = Field(0, ge=0, description="手续费")
    shiji_shouru: Decimal = Field(..., description="实际金额（收入为正，支出为负）")
    zhifu_fangshi: str = Field(..., description="支付方式")
    zhifu_zhanghu: Optional[str] = Field(None, description="支付账户")
    disanfang_liushui_hao: Optional[str] = Field(None, description="第三方流水号")
    disanfang_dingdan_hao: Optional[str] = Field(None, description="第三方订单号")
    jiaoyishijian: datetime = Field(..., description="交易时间")
    daozhangjian: Optional[datetime] = Field(None, description="到账时间")
    liushui_zhuangtai: str = Field("success", description="流水状态")
    duizhang_zhuangtai: str = Field("pending", description="对账状态")
    yinhang_mingcheng: Optional[str] = Field(None, description="银行名称")
    yinhang_zhanghu: Optional[str] = Field(None, description="银行账户")
    zhuanzhang_pingzheng: Optional[str] = Field(None, description="转账凭证路径")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('liushui_leixing')
    def validate_liushui_leixing(cls, v):
        allowed_types = ['income', 'refund', 'fee', 'expense']
        if v not in allowed_types:
            raise ValueError(f'流水类型必须是以下之一: {", ".join(allowed_types)}')
        return v

class ZhifuLiushuiUpdate(BaseModel):
    """更新支付流水的请求模式"""
    jiaoyijine: Optional[Decimal] = Field(None, gt=0, description="交易金额")
    shouxufei: Optional[Decimal] = Field(None, ge=0, description="手续费")
    shiji_shouru: Optional[Decimal] = Field(None, gt=0, description="实际收入")
    zhifu_fangshi: Optional[str] = Field(None, description="支付方式")
    zhifu_zhanghu: Optional[str] = Field(None, description="支付账户")
    disanfang_liushui_hao: Optional[str] = Field(None, description="第三方流水号")
    disanfang_dingdan_hao: Optional[str] = Field(None, description="第三方订单号")
    jiaoyishijian: Optional[datetime] = Field(None, description="交易时间")
    daozhangjian: Optional[datetime] = Field(None, description="到账时间")
    liushui_zhuangtai: Optional[str] = Field(None, description="流水状态")
    duizhang_zhuangtai: Optional[str] = Field(None, description="对账状态")
    yinhang_mingcheng: Optional[str] = Field(None, description="银行名称")
    yinhang_zhanghu: Optional[str] = Field(None, description="银行账户")
    zhuanzhang_pingzheng: Optional[str] = Field(None, description="转账凭证路径")
    beizhu: Optional[str] = Field(None, description="备注")
    caiwu_queren_ren: Optional[str] = Field(None, description="财务确认人ID")
    caiwu_queren_shijian: Optional[datetime] = Field(None, description="财务确认时间")

    @validator('liushui_zhuangtai')
    def validate_liushui_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['success', 'failed', 'processing']
            if v not in allowed_statuses:
                raise ValueError(f'流水状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('duizhang_zhuangtai')
    def validate_duizhang_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'matched', 'unmatched']
            if v not in allowed_statuses:
                raise ValueError(f'对账状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

class ZhifuLiushuiResponse(BaseModel):
    """支付流水响应模式"""
    id: str
    zhifu_dingdan_id: Optional[str]
    kehu_id: Optional[str]
    baoxiao_shenqing_id: Optional[str]
    guanlian_leixing: str
    liushui_bianhao: str
    liushui_leixing: str
    jiaoyijine: Decimal
    shouxufei: Decimal
    shiji_shouru: Decimal
    zhifu_fangshi: str
    zhifu_zhanghu: Optional[str]
    disanfang_liushui_hao: Optional[str]
    disanfang_dingdan_hao: Optional[str]
    jiaoyishijian: datetime
    daozhangjian: Optional[datetime]
    liushui_zhuangtai: str
    duizhang_zhuangtai: str
    yinhang_mingcheng: Optional[str]
    yinhang_zhanghu: Optional[str]
    zhuanzhang_pingzheng: Optional[str]
    beizhu: Optional[str]
    caiwu_queren_ren: Optional[str]
    caiwu_queren_shijian: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class ZhifuLiushuiListParams(BaseModel):
    """支付流水列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    zhifu_dingdan_id: Optional[str] = Field(None, description="支付订单ID")
    kehu_id: Optional[str] = Field(None, description="客户ID")
    liushui_leixing: Optional[str] = Field(None, description="流水类型")
    zhifu_fangshi: Optional[str] = Field(None, description="支付方式")
    liushui_zhuangtai: Optional[str] = Field(None, description="流水状态")
    duizhang_zhuangtai: Optional[str] = Field(None, description="对账状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")

class ZhifuLiushuiListResponse(BaseModel):
    """支付流水列表响应模式"""
    total: int
    items: List[ZhifuLiushuiResponse]
    page: int
    size: int
