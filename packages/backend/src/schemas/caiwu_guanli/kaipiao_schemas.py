"""
开票申请相关的 Pydantic 模式
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

class KaipiaoShenqingCreate(BaseModel):
    """创建开票申请的请求模式"""
    hetong_id: Optional[str] = Field(None, description="合同ID")
    kehu_id: str = Field(..., description="客户ID")
    zhifu_dingdan_id: Optional[str] = Field(None, description="支付订单ID")
    kaipiao_leixing: str = Field(..., description="开票类型")
    kaipiao_mingcheng: str = Field(..., min_length=1, max_length=200, description="开票名称")
    kaipiao_neirong: Optional[str] = Field(None, description="开票内容")
    kaipiao_jine: Decimal = Field(..., gt=0, description="开票金额")
    shuie: Decimal = Field(0, ge=0, description="税额")
    jia_shui_jine: Decimal = Field(..., gt=0, description="价税合计金额")
    gouwu_fang_mingcheng: str = Field(..., description="购物方名称")
    gouwu_fang_shuihao: Optional[str] = Field(None, description="购物方税号")
    gouwu_fang_dizhi: Optional[str] = Field(None, description="购物方地址")
    gouwu_fang_dianhua: Optional[str] = Field(None, description="购物方电话")
    gouwu_fang_yinhang: Optional[str] = Field(None, description="购物方开户银行")
    gouwu_fang_zhanghu: Optional[str] = Field(None, description="购物方银行账户")
    xiaoshou_fang_mingcheng: str = Field(..., description="销售方名称")
    xiaoshou_fang_shuihao: str = Field(..., description="销售方税号")
    xiaoshou_fang_dizhi: Optional[str] = Field(None, description="销售方地址")
    xiaoshou_fang_dianhua: Optional[str] = Field(None, description="销售方电话")
    xiaoshou_fang_yinhang: Optional[str] = Field(None, description="销售方开户银行")
    xiaoshou_fang_zhanghu: Optional[str] = Field(None, description="销售方银行账户")
    yaoqiu_kaipiao_shijian: Optional[datetime] = Field(None, description="要求开票时间")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('jia_shui_jine')
    def validate_total_amount(cls, v, values):
        """验证价税合计金额"""
        if 'kaipiao_jine' in values and 'shuie' in values:
            expected_total = values['kaipiao_jine'] + values['shuie']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('价税合计金额应等于开票金额加税额')
        return v

class KaipiaoShenqingUpdate(BaseModel):
    """更新开票申请的请求模式"""
    kaipiao_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="开票名称")
    kaipiao_neirong: Optional[str] = Field(None, description="开票内容")
    kaipiao_jine: Optional[Decimal] = Field(None, gt=0, description="开票金额")
    shuie: Optional[Decimal] = Field(None, ge=0, description="税额")
    jia_shui_jine: Optional[Decimal] = Field(None, gt=0, description="价税合计金额")
    gouwu_fang_mingcheng: Optional[str] = Field(None, description="购物方名称")
    gouwu_fang_shuihao: Optional[str] = Field(None, description="购物方税号")
    gouwu_fang_dizhi: Optional[str] = Field(None, description="购物方地址")
    gouwu_fang_dianhua: Optional[str] = Field(None, description="购物方电话")
    gouwu_fang_yinhang: Optional[str] = Field(None, description="购物方开户银行")
    gouwu_fang_zhanghu: Optional[str] = Field(None, description="购物方银行账户")
    xiaoshou_fang_mingcheng: Optional[str] = Field(None, description="销售方名称")
    xiaoshou_fang_shuihao: Optional[str] = Field(None, description="销售方税号")
    xiaoshou_fang_dizhi: Optional[str] = Field(None, description="销售方地址")
    xiaoshou_fang_dianhua: Optional[str] = Field(None, description="销售方电话")
    xiaoshou_fang_yinhang: Optional[str] = Field(None, description="销售方开户银行")
    xiaoshou_fang_zhanghu: Optional[str] = Field(None, description="销售方银行账户")
    shenqing_zhuangtai: Optional[str] = Field(None, description="申请状态")
    kaipiao_zhuangtai: Optional[str] = Field(None, description="开票状态")
    yaoqiu_kaipiao_shijian: Optional[datetime] = Field(None, description="要求开票时间")
    kaipiao_shijian: Optional[datetime] = Field(None, description="实际开票时间")
    fapiao_hao: Optional[str] = Field(None, description="发票号码")
    fapiao_daima: Optional[str] = Field(None, description="发票代码")
    fapiao_wenjian_lujing: Optional[str] = Field(None, description="发票文件路径")
    beizhu: Optional[str] = Field(None, description="备注")

class KaipiaoShenqingResponse(BaseModel):
    """开票申请响应模式"""
    id: str
    hetong_id: Optional[str]
    kehu_id: str
    zhifu_dingdan_id: Optional[str]
    shenqing_bianhao: str
    kaipiao_leixing: str
    kaipiao_mingcheng: str
    kaipiao_neirong: Optional[str]
    kaipiao_jine: Decimal
    shuie: Decimal
    jia_shui_jine: Decimal
    gouwu_fang_mingcheng: str
    gouwu_fang_shuihao: Optional[str]
    gouwu_fang_dizhi: Optional[str]
    gouwu_fang_dianhua: Optional[str]
    gouwu_fang_yinhang: Optional[str]
    gouwu_fang_zhanghu: Optional[str]
    xiaoshou_fang_mingcheng: str
    xiaoshou_fang_shuihao: str
    xiaoshou_fang_dizhi: Optional[str]
    xiaoshou_fang_dianhua: Optional[str]
    xiaoshou_fang_yinhang: Optional[str]
    xiaoshou_fang_zhanghu: Optional[str]
    shenqing_zhuangtai: str
    kaipiao_zhuangtai: str
    shenqing_shijian: datetime
    yaoqiu_kaipiao_shijian: Optional[datetime]
    kaipiao_shijian: Optional[datetime]
    fapiao_hao: Optional[str]
    fapiao_daima: Optional[str]
    fapiao_wenjian_lujing: Optional[str]
    shenhe_jilu_id: Optional[str]
    shenhe_ren: Optional[str]
    shenhe_shijian: Optional[datetime]
    shenhe_yijian: Optional[str]
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class KaipiaoShenqingListParams(BaseModel):
    """开票申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    kehu_id: Optional[str] = Field(None, description="客户ID")
    kaipiao_leixing: Optional[str] = Field(None, description="开票类型")
    shenqing_zhuangtai: Optional[str] = Field(None, description="申请状态")
    kaipiao_zhuangtai: Optional[str] = Field(None, description="开票状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")

class KaipiaoShenqingListResponse(BaseModel):
    """开票申请列表响应模式"""
    items: List[KaipiaoShenqingResponse]
    total: int
    page: int
    size: int
    pages: int

class KaipiaoAuditRequest(BaseModel):
    """开票审核请求模式"""
    shenqing_id: str = Field(..., description="申请ID")
    shenhe_yijian: Optional[str] = Field(None, description="审核意见")
    shenhe_jieguo: str = Field(..., description="审核结果：approved(通过)、rejected(拒绝)")

class KaipiaoProcessRequest(BaseModel):
    """开票处理请求模式"""
    shenqing_id: str = Field(..., description="申请ID")
    fapiao_hao: str = Field(..., description="发票号码")
    fapiao_daima: str = Field(..., description="发票代码")
    fapiao_wenjian_lujing: Optional[str] = Field(None, description="发票文件路径")
    kaipiao_shijian: Optional[datetime] = Field(None, description="开票时间")

class KaipiaoStatistics(BaseModel):
    """开票统计信息"""
    total_count: int = Field(..., description="总申请数")
    draft_count: int = Field(..., description="草稿数")
    submitted_count: int = Field(..., description="已提交数")
    approved_count: int = Field(..., description="已审批数")
    invoiced_count: int = Field(..., description="已开票数")
    rejected_count: int = Field(..., description="已拒绝数")
    total_amount: Decimal = Field(..., description="总金额")
    invoiced_amount: Decimal = Field(..., description="已开票金额")
    pending_amount: Decimal = Field(..., description="待开票金额")
