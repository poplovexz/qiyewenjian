"""
合同相关的Pydantic模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, computed_field

class HetongBase(BaseModel):
    """合同基础模型"""
    kehu_id: str = Field(..., description="客户ID")
    hetong_moban_id: str = Field(..., description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="关联报价ID")
    yifang_zhuti_id: Optional[str] = Field(None, description="乙方主体ID")
    hetong_bianhao: str = Field(..., min_length=1, max_length=50, description="合同编号")
    hetong_mingcheng: str = Field(..., min_length=1, max_length=200, description="合同名称")
    hetong_neirong: str = Field(..., min_length=1, description="合同内容")
    hetong_zhuangtai: str = Field(default="draft", description="合同状态")
    daoqi_riqi: datetime = Field(..., description="到期日期")
    shengxiao_riqi: Optional[datetime] = Field(None, description="生效日期")
    hetong_laiyuan: str = Field(default="manual", description="合同来源")
    zidong_shengcheng: str = Field(default="N", description="是否自动生成")

    @validator('hetong_zhuangtai')
    def validate_hetong_zhuangtai(cls, v):
        allowed_states = ['draft', 'pending', 'approved', 'active', 'signed', 'expired', 'cancelled']
        if v not in allowed_states:
            raise ValueError(f'合同状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('hetong_laiyuan')
    def validate_hetong_laiyuan(cls, v):
        allowed_sources = ['manual', 'auto_from_quote']
        if v not in allowed_sources:
            raise ValueError(f'合同来源必须是以下之一: {", ".join(allowed_sources)}')
        return v

    @validator('zidong_shengcheng')
    def validate_zidong_shengcheng(cls, v):
        if v not in ['Y', 'N']:
            raise ValueError('是否自动生成必须是Y或N')
        return v

class HetongCreate(HetongBase):
    """创建合同的请求模型"""
    pass

class HetongUpdate(BaseModel):
    """更新合同的请求模型"""
    kehu_id: Optional[str] = Field(None, description="客户ID")
    hetong_moban_id: Optional[str] = Field(None, description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="关联报价ID")
    yifang_zhuti_id: Optional[str] = Field(None, description="乙方主体ID")
    hetong_bianhao: Optional[str] = Field(None, min_length=1, max_length=50, description="合同编号")
    hetong_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="合同名称")
    hetong_neirong: Optional[str] = Field(None, min_length=1, description="合同内容")
    hetong_zhuangtai: Optional[str] = Field(None, description="合同状态")
    daoqi_riqi: Optional[datetime] = Field(None, description="到期日期")
    shengxiao_riqi: Optional[datetime] = Field(None, description="生效日期")
    hetong_laiyuan: Optional[str] = Field(None, description="合同来源")
    zidong_shengcheng: Optional[str] = Field(None, description="是否自动生成")

    @validator('hetong_zhuangtai')
    def validate_hetong_zhuangtai(cls, v):
        if v is not None:
            allowed_states = ['draft', 'pending', 'approved', 'active', 'signed', 'expired', 'cancelled']
            if v not in allowed_states:
                raise ValueError(f'合同状态必须是以下之一: {", ".join(allowed_states)}')
        return v

    @validator('hetong_laiyuan')
    def validate_hetong_laiyuan(cls, v):
        if v is not None:
            allowed_sources = ['manual', 'auto_from_quote']
            if v not in allowed_sources:
                raise ValueError(f'合同来源必须是以下之一: {", ".join(allowed_sources)}')
        return v

    @validator('zidong_shengcheng')
    def validate_zidong_shengcheng(cls, v):
        if v is not None and v not in ['Y', 'N']:
            raise ValueError('是否自动生成必须是Y或N')
        return v

class HetongSignRequest(BaseModel):
    """合同签署请求模型"""
    qianming_beizhu: Optional[str] = Field(None, description="签名备注")

class KehuBrief(BaseModel):
    """客户简要信息模型（用于合同列表）"""
    id: str
    gongsi_mingcheng: str

    class Config:
        from_attributes = True

class HetongMobanBrief(BaseModel):
    """合同模板简要信息模型（用于合同列表）"""
    id: str
    moban_mingcheng: str
    hetong_leixing: str

    class Config:
        from_attributes = True

class HetongResponse(BaseModel):
    """合同响应模型"""
    id: str
    kehu_id: str
    hetong_moban_id: str
    baojia_id: Optional[str]
    yifang_zhuti_id: Optional[str]
    hetong_bianhao: str
    hetong_mingcheng: str
    hetong_neirong: str
    hetong_zhuangtai: str
    qianshu_riqi: Optional[datetime]
    shengxiao_riqi: Optional[datetime]
    daoqi_riqi: datetime
    pdf_lujing: Optional[str]
    qianshu_lujing: Optional[str]
    shenpi_ren_id: Optional[str]
    shenpi_riqi: Optional[datetime]
    shenpi_yijian: Optional[str]
    dianziqianming_lujing: Optional[str]
    qianming_ren_id: Optional[str]
    qianming_shijian: Optional[datetime]
    qianming_ip: Optional[str]
    qianming_beizhu: Optional[str]
    hetong_laiyuan: str
    zidong_shengcheng: str
    # 新增字段
    sign_token: Optional[str]
    sign_token_expires_at: Optional[datetime]
    customer_signature: Optional[str]
    signed_at: Optional[datetime]
    payment_status: str
    paid_at: Optional[datetime]
    payment_amount: Optional[str]
    payment_method: Optional[str]
    payment_transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    # 关联对象
    kehu: Optional[KehuBrief] = None
    hetong_moban: Optional[HetongMobanBrief] = None

    # 扩展字段（非数据库字段，由service层动态设置）
    has_service_order: bool = False

    @computed_field
    @property
    def hetong_jine(self) -> Optional[float]:
        """合同金额（从payment_amount转换）"""
        if self.payment_amount:
            try:
                return float(self.payment_amount)
            except (ValueError, TypeError):
                return None
        return None

    class Config:
        from_attributes = True

class HetongListResponse(BaseModel):
    """合同列表响应模型"""
    total: int
    items: List[HetongResponse]
    page: int
    size: int

class HetongPreviewRequest(BaseModel):
    """合同预览请求模型"""
    hetong_moban_id: str = Field(..., description="合同模板ID")
    baojia_id: Optional[str] = Field(None, description="报价ID（用于自动填充变量）")
    bianliang_zhis: Optional[dict] = Field(None, description="变量值字典")

class HetongPreviewResponse(BaseModel):
    """合同预览响应模型"""
    hetong_neirong: str = Field(..., description="预览的合同内容")
    bianliang_list: List[str] = Field(..., description="模板中的变量列表")

class GenerateSignLinkResponse(BaseModel):
    """生成签署链接响应模型"""
    sign_link: str = Field(..., description="签署链接")
    sign_token: str = Field(..., description="签署令牌")
    expires_at: datetime = Field(..., description="过期时间")

class ContractSignInfoResponse(BaseModel):
    """合同签署信息响应模型（无需认证）"""
    id: str
    hetong_bianhao: str
    hetong_mingcheng: str
    hetong_neirong: str
    daoqi_riqi: datetime
    payment_amount: Optional[str]
    payment_status: str
    signed_at: Optional[datetime]
    customer_signature: Optional[str]

    class Config:
        from_attributes = True

class CustomerSignRequest(BaseModel):
    """客户签署请求模型"""
    signature_data: str = Field(..., description="签名数据（base64）")
    signer_name: str = Field(..., min_length=1, max_length=50, description="签署人姓名")
    signer_phone: Optional[str] = Field(None, max_length=20, description="签署人电话")
    signer_email: Optional[str] = Field(None, max_length=100, description="签署人邮箱")

class CustomerPaymentRequest(BaseModel):
    """客户支付请求模型"""
    payment_method: str = Field(..., description="支付方式：wechat/alipay/bank")
    payment_amount: str = Field(..., description="支付金额")
    return_url: Optional[str] = Field(None, description="支付成功后的返回URL")

    @validator('payment_method')
    def validate_payment_method(cls, v):
        allowed_methods = ['wechat', 'alipay', 'bank']
        if v not in allowed_methods:
            raise ValueError(f'支付方式必须是以下之一: {", ".join(allowed_methods)}')
        return v

class PaymentCallbackRequest(BaseModel):
    """支付回调请求模型"""
    transaction_id: str = Field(..., description="交易号")
    payment_status: str = Field(..., description="支付状态")
    paid_amount: str = Field(..., description="实际支付金额")
    paid_at: datetime = Field(..., description="支付时间")

class BankPaymentInfoRequest(BaseModel):
    """客户确认使用银行转账请求模型"""
    # 客户只需要确认使用银行转账，不需要填写汇款信息
    # 汇款信息由业务员后续跟踪获取
    pass

class BankPaymentInfoResponse(BaseModel):
    """客户提交银行汇款信息响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    danju_id: str = Field(..., description="单据ID")
    danju_bianhao: str = Field(..., description="单据编号")

class PaymentMethodItem(BaseModel):
    """可用支付方式条目模型"""
    method: str = Field(..., description="支付方式标识，如 wechat/alipay/bank")
    label: str = Field(..., description="展示名称")
    icon: Optional[str] = Field(None, description="图标标识")
    description: Optional[str] = Field(None, description="说明")

class AvailablePaymentMethodsResponse(BaseModel):
    """获取可用支付方式响应模型"""
    available_methods: List[PaymentMethodItem] = Field(..., description="可用支付方式列表")
    has_online_payment: bool = Field(..., description="是否存在在线支付方式")

class PaymentInitiateResponse(BaseModel):
    """发起支付响应模型，兼容扫码支付与银行确认"""
    payment_method: str = Field(..., description="支付方式：wechat/alipay/bank")
    message: Optional[str] = Field(None, description="提示信息（银行转账场景）")
    order_id: Optional[str] = Field(None, description="订单ID（在线支付场景）")
    order_no: Optional[str] = Field(None, description="订单编号（在线支付场景）")
    amount: Optional[str] = Field(None, description="支付金额（在线支付场景）")
    qr_code: Optional[str] = Field(None, description="二维码内容（扫码场景）")
    payment_config: Optional[str] = Field(None, description="支付配置名称（在线支付场景）")

class PaymentCallbackResponse(BaseModel):
    """支付回调响应模型"""
    success: bool = Field(..., description="是否处理成功")
    message: str = Field(..., description="提示信息")
    danju_bianhao: str = Field(..., description="单据编号")
