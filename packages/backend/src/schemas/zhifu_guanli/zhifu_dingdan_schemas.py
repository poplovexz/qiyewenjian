"""
支付订单相关的 Pydantic 模式
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class ZhifuDingdanCreate(BaseModel):
    """创建支付订单的请求模式"""
    hetong_id: str = Field(..., description="合同ID")
    kehu_id: str = Field(..., description="客户ID")
    yifang_zhuti_id: Optional[str] = Field(None, description="乙方主体ID")
    zhifu_fangshi_id: Optional[str] = Field(None, description="支付方式ID")
    dingdan_mingcheng: str = Field(..., min_length=1, max_length=200, description="订单名称")
    dingdan_miaoshu: Optional[str] = Field(None, description="订单描述")
    dingdan_jine: Decimal = Field(..., gt=0, description="订单金额")
    yingfu_jine: Decimal = Field(..., gt=0, description="应付金额")
    zhifu_leixing: str = Field(..., description="支付类型")
    guoqi_shijian: Optional[datetime] = Field(None, description="过期时间")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhifu_leixing')
    def validate_zhifu_leixing(cls, v):
        allowed_types = ['weixin', 'zhifubao', 'yinhangzhuanzhang', 'xianjin', 'qita']
        if v not in allowed_types:
            raise ValueError(f'支付类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class ZhifuDingdanUpdate(BaseModel):
    """更新支付订单的请求模式"""
    dingdan_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="订单名称")
    dingdan_miaoshu: Optional[str] = Field(None, description="订单描述")
    yingfu_jine: Optional[Decimal] = Field(None, gt=0, description="应付金额")
    zhifu_leixing: Optional[str] = Field(None, description="支付类型")
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态")
    disanfang_dingdan_hao: Optional[str] = Field(None, description="第三方订单号")
    disanfang_liushui_hao: Optional[str] = Field(None, description="第三方流水号")
    erweima_lujing: Optional[str] = Field(None, description="二维码路径")
    zhifu_shijian: Optional[datetime] = Field(None, description="支付时间")
    guoqi_shijian: Optional[datetime] = Field(None, description="过期时间")
    huidiao_zhuangtai: Optional[str] = Field(None, description="回调状态")
    huidiao_shijian: Optional[datetime] = Field(None, description="回调时间")
    huidiao_xinxi: Optional[str] = Field(None, description="回调信息")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('zhifu_leixing')
    def validate_zhifu_leixing(cls, v):
        if v is not None:
            allowed_types = ['weixin', 'zhifubao', 'yinhangzhuanzhang', 'xianjin', 'qita']
            if v not in allowed_types:
                raise ValueError(f'支付类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhifu_zhuangtai')
    def validate_zhifu_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'paying', 'paid', 'failed', 'cancelled', 'refunded']
            if v not in allowed_statuses:
                raise ValueError(f'支付状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class ZhifuDingdanResponse(BaseModel):
    """支付订单响应模式"""
    id: str
    hetong_id: str
    kehu_id: str
    yifang_zhuti_id: Optional[str]
    zhifu_fangshi_id: Optional[str]
    zhifu_peizhi_id: Optional[str]
    dingdan_bianhao: str
    dingdan_mingcheng: str
    dingdan_miaoshu: Optional[str]
    dingdan_jine: Decimal
    yingfu_jine: Decimal
    shifu_jine: Decimal
    zhifu_leixing: str
    zhifu_zhuangtai: str
    zhifu_pingtai: Optional[str]
    zhifu_fangshi_mingxi: Optional[str]
    disanfang_dingdan_hao: Optional[str]
    disanfang_liushui_hao: Optional[str]
    erweima_lujing: Optional[str]
    erweima_neirong: Optional[str]
    tuikuan_jine: Optional[Decimal]
    tuikuan_cishu: Optional[int]
    chuangjian_shijian: datetime
    zhifu_shijian: Optional[datetime]
    guoqi_shijian: Optional[datetime]
    huidiao_zhuangtai: str
    huidiao_shijian: Optional[datetime]
    huidiao_xinxi: Optional[str]
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str

    # 关联的合同信息
    hetong_bianhao: Optional[str] = None
    hetong_mingcheng: Optional[str] = None

    class Config:
        from_attributes = True


class ZhifuDingdanListParams(BaseModel):
    """支付订单列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    kehu_id: Optional[str] = Field(None, description="客户ID")
    zhifu_leixing: Optional[str] = Field(None, description="支付类型")
    zhifu_zhuangtai: Optional[str] = Field(None, description="支付状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class ZhifuDingdanListResponse(BaseModel):
    """支付订单列表响应模式"""
    total: int
    items: List[ZhifuDingdanResponse]
    page: int
    size: int


class ZhifuDingdanStatistics(BaseModel):
    """支付订单统计信息"""
    total_count: int = Field(..., description="总订单数")
    pending_count: int = Field(..., description="待支付订单数")
    paid_count: int = Field(..., description="已支付订单数")
    failed_count: int = Field(..., description="支付失败订单数")
    total_amount: Decimal = Field(..., description="总金额")
    paid_amount: Decimal = Field(..., description="已支付金额")
    pending_amount: Decimal = Field(..., description="待支付金额")


class CreatePaymentRequest(BaseModel):
    """创建第三方支付请求"""
    dingdan_id: str = Field(..., description="支付订单ID")
    zhifu_pingtai: str = Field(..., description="支付平台：weixin/zhifubao")
    zhifu_fangshi: str = Field(..., description="支付方式：jsapi/app/h5/native/page/wap")
    openid: Optional[str] = Field(None, description="微信用户openid（JSAPI支付必填）")
    return_url: Optional[str] = Field(None, description="支付成功返回URL（支付宝必填）")
    quit_url: Optional[str] = Field(None, description="支付取消返回URL（支付宝可选）")

    @validator('zhifu_pingtai')
    def validate_zhifu_pingtai(cls, v):
        allowed_platforms = ['weixin', 'zhifubao']
        if v not in allowed_platforms:
            raise ValueError(f'支付平台必须是以下之一: {", ".join(allowed_platforms)}')
        return v

    @validator('zhifu_fangshi')
    def validate_zhifu_fangshi(cls, v):
        allowed_methods = ['jsapi', 'app', 'h5', 'native', 'page', 'wap']
        if v not in allowed_methods:
            raise ValueError(f'支付方式必须是以下之一: {", ".join(allowed_methods)}')
        return v


class CreatePaymentResponse(BaseModel):
    """创建第三方支付响应"""
    dingdan_id: str
    dingdan_bianhao: str
    zhifu_pingtai: str
    zhifu_fangshi: str
    payment_data: dict


class QueryPaymentResponse(BaseModel):
    """查询支付订单响应"""
    dingdan_id: str
    dingdan_bianhao: str
    zhifu_zhuangtai: str
    zhifu_pingtai: Optional[str]
    disanfang_dingdan_hao: Optional[str]
    disanfang_liushui_hao: Optional[str]
    query_result: dict
