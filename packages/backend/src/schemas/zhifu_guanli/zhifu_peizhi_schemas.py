"""
支付配置相关的 Pydantic 模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ZhifuPeizhiCreate(BaseModel):
    """创建支付配置的请求模式"""
    peizhi_mingcheng: str = Field(..., min_length=1, max_length=100, description="配置名称")
    peizhi_leixing: str = Field(..., description="配置类型：weixin(微信)、zhifubao(支付宝)、yinhang(银行汇款)、xianjin(现金)")
    zhuangtai: Optional[str] = Field('qiyong', description="状态：qiyong(启用)、tingyong(停用)")
    huanjing: Optional[str] = Field('wuxu', description="环境：shachang(沙箱)、shengchan(生产)、wuxu(无需，用于线下支付)")

    # 微信支付配置（明文输入，后端加密存储）
    weixin_appid: Optional[str] = Field(None, description="微信APPID")
    weixin_shanghu_hao: Optional[str] = Field(None, description="微信商户号")
    weixin_shanghu_siyao: Optional[str] = Field(None, description="微信商户私钥")
    weixin_zhengshu_xuliehao: Optional[str] = Field(None, description="微信证书序列号")
    weixin_api_v3_miyao: Optional[str] = Field(None, description="微信API v3密钥")

    # 支付宝配置（明文输入，后端加密存储）
    zhifubao_appid: Optional[str] = Field(None, description="支付宝APPID")
    zhifubao_shanghu_siyao: Optional[str] = Field(None, description="支付宝商户私钥")
    zhifubao_zhifubao_gongyao: Optional[str] = Field(None, description="支付宝公钥")
    zhifubao_wangguan: Optional[str] = Field(None, description="支付宝网关地址")

    # 银行汇款配置
    yinhang_mingcheng: Optional[str] = Field(None, description="银行名称")
    yinhang_zhanghu_mingcheng: Optional[str] = Field(None, description="银行账户名称")
    yinhang_zhanghu_haoma: Optional[str] = Field(None, description="银行账号")
    kaihuhang_mingcheng: Optional[str] = Field(None, description="开户行名称")
    kaihuhang_lianhanghao: Optional[str] = Field(None, description="开户行联行号")

    # 通用配置
    tongzhi_url: Optional[str] = Field(None, description="支付回调通知URL")
    beizhu: Optional[str] = Field(None, description="备注")

    @validator('peizhi_leixing')
    def validate_peizhi_leixing(cls, v):
        allowed_types = ['weixin', 'zhifubao', 'yinhang', 'xianjin']
        if v not in allowed_types:
            raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['qiyong', 'tingyong']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @validator('huanjing')
    def validate_huanjing(cls, v):
        if v is not None:
            allowed_envs = ['shachang', 'shengchan', 'wuxu']
            if v not in allowed_envs:
                raise ValueError(f'环境必须是以下之一: {", ".join(allowed_envs)}')
        return v

class ZhifuPeizhiUpdate(BaseModel):
    """更新支付配置的请求模式"""
    peizhi_mingcheng: Optional[str] = Field(None, min_length=1, max_length=100, description="配置名称")
    zhuangtai: Optional[str] = Field(None, description="状态：qiyong(启用)、tingyong(停用)")
    huanjing: Optional[str] = Field(None, description="环境：shachang(沙箱)、shengchan(生产)、wuxu(无需，用于线下支付)")

    # 微信支付配置（明文输入，后端加密存储）
    weixin_appid: Optional[str] = Field(None, description="微信APPID")
    weixin_shanghu_hao: Optional[str] = Field(None, description="微信商户号")
    weixin_shanghu_siyao: Optional[str] = Field(None, description="微信商户私钥")
    weixin_zhengshu_xuliehao: Optional[str] = Field(None, description="微信证书序列号")
    weixin_api_v3_miyao: Optional[str] = Field(None, description="微信API v3密钥")

    # 支付宝配置（明文输入，后端加密存储）
    zhifubao_appid: Optional[str] = Field(None, description="支付宝APPID")
    zhifubao_shanghu_siyao: Optional[str] = Field(None, description="支付宝商户私钥")
    zhifubao_zhifubao_gongyao: Optional[str] = Field(None, description="支付宝公钥")
    zhifubao_wangguan: Optional[str] = Field(None, description="支付宝网关地址")

    # 银行汇款配置
    yinhang_mingcheng: Optional[str] = Field(None, description="银行名称")
    yinhang_zhanghu_mingcheng: Optional[str] = Field(None, description="银行账户名称")
    yinhang_zhanghu_haoma: Optional[str] = Field(None, description="银行账号")
    kaihuhang_mingcheng: Optional[str] = Field(None, description="开户行名称")
    kaihuhang_lianhanghao: Optional[str] = Field(None, description="开户行联行号")

    # 通用配置
    tongzhi_url: Optional[str] = Field(None, description="支付回调通知URL")
    beizhu: Optional[str] = Field(None, description="备注")
    
    @validator('zhuangtai')
    def validate_zhuangtai(cls, v):
        if v is not None:
            allowed_statuses = ['qiyong', 'tingyong']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    @validator('huanjing')
    def validate_huanjing(cls, v):
        if v is not None:
            allowed_envs = ['shachang', 'shengchan', 'wuxu']
            if v not in allowed_envs:
                raise ValueError(f'环境必须是以下之一: {", ".join(allowed_envs)}')
        return v

class ZhifuPeizhiResponse(BaseModel):
    """支付配置响应模式（敏感信息脱敏）"""
    id: str
    peizhi_mingcheng: str
    peizhi_leixing: str
    zhuangtai: str
    huanjing: str

    # 微信支付配置（脱敏显示）
    weixin_appid: Optional[str] = None
    weixin_shanghu_hao: Optional[str] = None
    weixin_shanghu_siyao_masked: Optional[str] = None  # 脱敏显示
    weixin_zhengshu_xuliehao: Optional[str] = None
    weixin_api_v3_miyao_masked: Optional[str] = None  # 脱敏显示

    # 支付宝配置（脱敏显示）
    zhifubao_appid: Optional[str] = None
    zhifubao_wangguan: Optional[str] = None
    zhifubao_shanghu_siyao_masked: Optional[str] = None  # 脱敏显示
    zhifubao_zhifubao_gongyao_masked: Optional[str] = None  # 脱敏显示

    # 银行汇款配置
    yinhang_mingcheng: Optional[str] = None
    yinhang_zhanghu_mingcheng: Optional[str] = None
    yinhang_zhanghu_haoma: Optional[str] = None
    kaihuhang_mingcheng: Optional[str] = None
    kaihuhang_lianhanghao: Optional[str] = None

    # 通用配置
    tongzhi_url: Optional[str] = None
    beizhu: Optional[str] = None

    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class ZhifuPeizhiDetail(BaseModel):
    """支付配置详情模式（包含解密后的敏感信息，仅用于内部使用）"""
    id: str
    peizhi_mingcheng: str
    peizhi_leixing: str
    zhuangtai: str
    huanjing: str

    # 微信支付配置（解密后的明文）
    weixin_appid: Optional[str] = None
    weixin_shanghu_hao: Optional[str] = None
    weixin_shanghu_siyao: Optional[str] = None
    weixin_zhengshu_xuliehao: Optional[str] = None
    weixin_api_v3_miyao: Optional[str] = None

    # 支付宝配置（解密后的明文）
    zhifubao_appid: Optional[str] = None
    zhifubao_wangguan: Optional[str] = None
    zhifubao_shanghu_siyao: Optional[str] = None
    zhifubao_zhifubao_gongyao: Optional[str] = None

    # 银行汇款配置
    yinhang_mingcheng: Optional[str] = None
    yinhang_zhanghu_mingcheng: Optional[str] = None
    yinhang_zhanghu_haoma: Optional[str] = None
    kaihuhang_mingcheng: Optional[str] = None
    kaihuhang_lianhanghao: Optional[str] = None

    # 通用配置
    tongzhi_url: Optional[str] = None
    beizhu: Optional[str] = None

    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class ZhifuPeizhiListResponse(BaseModel):
    """支付配置列表响应模式"""
    total: int
    items: list[ZhifuPeizhiResponse]
