"""
支付配置表模型
"""
from sqlalchemy import Column, String, Text
from ..base import BaseModel


class ZhifuPeizhi(BaseModel):
    """支付配置表"""
    
    __tablename__ = "zhifu_peizhi"
    __table_args__ = {"comment": "支付配置表"}
    
    # 基本信息
    peizhi_mingcheng = Column(
        String(100),
        nullable=False,
        comment="配置名称"
    )
    
    peizhi_leixing = Column(
        String(20),
        nullable=False,
        comment="配置类型：weixin(微信)、zhifubao(支付宝)、yinhang(银行汇款)、xianjin(现金)"
    )
    
    zhuangtai = Column(
        String(20),
        default='qiyong',
        comment="状态：qiyong(启用)、tingyong(停用)"
    )
    
    huanjing = Column(
        String(20),
        default='shengchan',
        comment="环境：shachang(沙箱)、shengchan(生产)、wuxu(无需，用于线下支付)"
    )
    
    # 微信支付配置（加密存储）
    weixin_appid = Column(
        String(500),
        comment="微信APPID（加密）"
    )
    
    weixin_shanghu_hao = Column(
        String(500),
        comment="微信商户号（加密）"
    )
    
    weixin_shanghu_siyao = Column(
        Text,
        comment="微信商户私钥（加密）"
    )
    
    weixin_zhengshu_xuliehao = Column(
        String(500),
        comment="微信证书序列号（加密）"
    )
    
    weixin_api_v3_miyao = Column(
        String(500),
        comment="微信API v3密钥（加密）"
    )
    
    # 支付宝配置（加密存储）
    zhifubao_appid = Column(
        String(500),
        comment="支付宝APPID（加密）"
    )
    
    zhifubao_shanghu_siyao = Column(
        Text,
        comment="支付宝商户私钥（加密）"
    )
    
    zhifubao_zhifubao_gongyao = Column(
        Text,
        comment="支付宝公钥（加密）"
    )

    # 银行汇款配置
    yinhang_mingcheng = Column(
        String(100),
        comment="银行名称"
    )

    yinhang_zhanghu_mingcheng = Column(
        String(100),
        comment="银行账户名称"
    )

    yinhang_zhanghu_haoma = Column(
        String(100),
        comment="银行账号"
    )

    kaihuhang_mingcheng = Column(
        String(200),
        comment="开户行名称"
    )

    kaihuhang_lianhanghao = Column(
        String(50),
        comment="开户行联行号"
    )

    # 通用配置
    tongzhi_url = Column(
        String(500),
        comment="支付回调通知URL"
    )

    beizhu = Column(
        Text,
        comment="备注"
    )
    
    def __repr__(self):
        return f"<ZhifuPeizhi(id={self.id}, mingcheng={self.peizhi_mingcheng}, leixing={self.peizhi_leixing})>"

