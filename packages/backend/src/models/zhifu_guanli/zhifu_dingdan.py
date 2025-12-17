"""
支付订单表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel


class ZhifuDingdan(BaseModel):
    """支付订单表"""
    
    __tablename__ = "zhifu_dingdan"
    __table_args__ = {"comment": "支付订单表"}
    
    # 关联信息
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id", ondelete="CASCADE"),
        nullable=False,
        comment="合同ID"
    )
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    yifang_zhuti_id = Column(
        String(36),
        ForeignKey("hetong_yifang_zhuti.id"),
        nullable=True,
        comment="乙方主体ID"
    )
    
    zhifu_fangshi_id = Column(
        String(36),
        ForeignKey("hetong_zhifu_fangshi.id"),
        nullable=True,
        comment="支付方式ID"
    )
    
    # 订单基本信息
    dingdan_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="支付订单编号"
    )
    
    dingdan_mingcheng = Column(
        String(200),
        nullable=False,
        comment="订单名称"
    )
    
    dingdan_miaoshu = Column(
        Text,
        nullable=True,
        comment="订单描述"
    )
    
    # 金额信息
    dingdan_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="订单金额"
    )
    
    yingfu_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="应付金额"
    )
    
    shifu_jine = Column(
        Numeric(10, 2),
        default=0.00,
        comment="实付金额"
    )
    
    # 支付信息
    zhifu_leixing = Column(
        String(50),
        nullable=False,
        comment="支付类型：weixin(微信支付)、zhifubao(支付宝)、yinhangzhuanzhang(银行转账)、xianjin(现金)、qita(其他)"
    )
    
    zhifu_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="支付状态：pending(待支付)、paying(支付中)、paid(已支付)、failed(支付失败)、cancelled(已取消)、refunded(已退款)"
    )
    
    # 支付配置
    zhifu_peizhi_id = Column(
        String(36),
        ForeignKey("zhifu_peizhi.id"),
        nullable=True,
        comment="支付配置ID"
    )

    # 第三方支付信息
    disanfang_dingdan_hao = Column(
        String(100),
        nullable=True,
        comment="第三方支付订单号"
    )

    disanfang_liushui_hao = Column(
        String(100),
        nullable=True,
        comment="第三方支付流水号"
    )

    zhifu_pingtai = Column(
        String(20),
        nullable=True,
        comment="支付平台：weixin(微信)、zhifubao(支付宝)"
    )

    zhifu_fangshi_mingxi = Column(
        String(50),
        nullable=True,
        comment="支付方式明细：jsapi(公众号)、app(APP)、h5(H5)、native(扫码)、page(网页)、wap(手机网页)"
    )

    erweima_lujing = Column(
        String(500),
        nullable=True,
        comment="支付二维码图片路径"
    )

    erweima_neirong = Column(
        Text,
        nullable=True,
        comment="支付二维码内容（code_url或支付链接）"
    )

    # 退款信息
    tuikuan_jine = Column(
        Numeric(10, 2),
        default=0.00,
        comment="退款金额"
    )

    tuikuan_cishu = Column(
        String(10),
        default="0",
        comment="退款次数"
    )
    
    # 时间信息
    chuangjian_shijian = Column(
        DateTime,
        nullable=False,
        comment="创建时间"
    )
    
    zhifu_shijian = Column(
        DateTime,
        nullable=True,
        comment="支付时间"
    )
    
    guoqi_shijian = Column(
        DateTime,
        nullable=True,
        comment="过期时间"
    )
    
    # 回调信息
    huidiao_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="回调状态：pending(待回调)、success(回调成功)、failed(回调失败)"
    )
    
    huidiao_shijian = Column(
        DateTime,
        nullable=True,
        comment="回调时间"
    )
    
    huidiao_xinxi = Column(
        Text,
        nullable=True,
        comment="回调信息"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong = relationship("Hetong", back_populates="zhifu_dingdan_list")
    kehu = relationship("Kehu")
    yifang_zhuti = relationship("HetongYifangZhuti")
    zhifu_fangshi = relationship("HetongZhifuFangshi")
    zhifu_peizhi = relationship("ZhifuPeizhi")
    zhifu_liushui_list = relationship(
        "ZhifuLiushui",
        back_populates="zhifu_dingdan",
        cascade="all, delete-orphan"
    )
    tuikuan_jilu_list = relationship(
        "ZhifuTuikuan",
        foreign_keys="ZhifuTuikuan.zhifu_dingdan_id",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ZhifuDingdan(dingdan_bianhao='{self.dingdan_bianhao}', dingdan_jine='{self.dingdan_jine}', zhifu_zhuangtai='{self.zhifu_zhuangtai}')>"
