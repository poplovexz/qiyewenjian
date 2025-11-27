"""
支付流水表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel


class ZhifuLiushui(BaseModel):
    """支付流水表"""
    
    __tablename__ = "zhifu_liushui"
    __table_args__ = {"comment": "支付流水表"}
    
    # 关联信息
    zhifu_dingdan_id = Column(
        String(36),
        ForeignKey("zhifu_dingdan.id", ondelete="CASCADE"),
        nullable=True,
        comment="支付订单ID（收入流水必填）"
    )

    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=True,
        comment="客户ID（收入流水必填）"
    )

    baoxiao_shenqing_id = Column(
        String(36),
        ForeignKey("baoxiao_shenqing.id", ondelete="CASCADE"),
        nullable=True,
        comment="报销申请ID（支出流水必填）"
    )

    guanlian_leixing = Column(
        String(20),
        default="zhifu_dingdan",
        nullable=False,
        comment="关联类型：zhifu_dingdan(支付订单)、baoxiao_shenqing(报销申请)"
    )
    
    # 流水基本信息
    liushui_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="流水编号"
    )
    
    liushui_leixing = Column(
        String(20),
        nullable=False,
        comment="流水类型：income(收入)、refund(退款)、fee(手续费)、expense(支出)"
    )
    
    # 金额信息
    jiaoyijine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="交易金额"
    )
    
    shouxufei = Column(
        Numeric(10, 2),
        default=0.00,
        comment="手续费"
    )
    
    shiji_shouru = Column(
        Numeric(10, 2),
        nullable=False,
        comment="实际金额（收入为正，支出为负）"
    )
    
    # 支付信息
    zhifu_fangshi = Column(
        String(50),
        nullable=False,
        comment="支付方式"
    )
    
    zhifu_zhanghu = Column(
        String(100),
        nullable=True,
        comment="支付账户"
    )
    
    # 第三方信息
    disanfang_liushui_hao = Column(
        String(100),
        nullable=True,
        comment="第三方流水号"
    )
    
    disanfang_dingdan_hao = Column(
        String(100),
        nullable=True,
        comment="第三方订单号"
    )
    
    # 时间信息
    jiaoyishijian = Column(
        DateTime,
        nullable=False,
        comment="交易时间"
    )
    
    daozhangjian = Column(
        DateTime,
        nullable=True,
        comment="到账时间"
    )
    
    # 状态信息
    liushui_zhuangtai = Column(
        String(20),
        default="success",
        nullable=False,
        comment="流水状态：success(成功)、failed(失败)、processing(处理中)"
    )
    
    duizhang_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="对账状态：pending(待对账)、matched(已对账)、unmatched(未对账)"
    )
    
    # 银行信息（银行转账专用）
    yinhang_mingcheng = Column(
        String(100),
        nullable=True,
        comment="银行名称"
    )
    
    yinhang_zhanghu = Column(
        String(50),
        nullable=True,
        comment="银行账户"
    )
    
    zhuanzhang_pingzheng = Column(
        String(500),
        nullable=True,
        comment="转账凭证图片路径"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 财务信息
    caiwu_queren_ren = Column(
        String(36),
        nullable=True,
        comment="财务确认人ID"
    )
    
    caiwu_queren_shijian = Column(
        DateTime,
        nullable=True,
        comment="财务确认时间"
    )
    
    # 关联关系
    zhifu_dingdan = relationship("ZhifuDingdan", back_populates="zhifu_liushui_list")
    kehu = relationship("Kehu")
    baoxiao_shenqing = relationship("BaoxiaoShenqing")
    
    def __repr__(self) -> str:
        return f"<ZhifuLiushui(liushui_bianhao='{self.liushui_bianhao}', jiaoyijine='{self.jiaoyijine}', liushui_zhuangtai='{self.liushui_zhuangtai}')>"
