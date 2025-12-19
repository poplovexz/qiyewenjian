"""
合同表模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey

from sqlalchemy.orm import relationship

from ..base import BaseModel

class Hetong(BaseModel):
    """合同表"""
    
    __tablename__ = "hetong"
    __table_args__ = {"comment": "合同表"}
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    hetong_moban_id = Column(
        String(36),
        ForeignKey("hetong_moban.id"),
        nullable=False,
        comment="合同模板ID"
    )

    # 阶段2新增：报价关联
    baojia_id = Column(
        String(36),
        ForeignKey("xiansuo_baojia.id"),
        nullable=True,
        comment="关联报价ID"
    )

    # 阶段2新增：乙方主体关联
    yifang_zhuti_id = Column(
        String(36),
        ForeignKey("hetong_yifang_zhuti.id"),
        nullable=True,
        comment="乙方主体ID"
    )
    
    # 合同基本信息
    hetong_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="合同编号"
    )
    
    hetong_mingcheng = Column(
        String(200),
        nullable=False,
        comment="合同名称"
    )
    
    hetong_neirong = Column(
        Text,
        nullable=False,
        comment="合同内容"
    )
    
    # 合同状态
    hetong_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="合同状态：draft-草稿，pending-待审批，approved-已审批，active-已生效，signed-已签署，expired-已过期，cancelled-已取消"
    )
    
    # 时间信息
    qianshu_riqi = Column(
        DateTime,
        nullable=True,
        comment="签署日期"
    )
    
    shengxiao_riqi = Column(
        DateTime,
        nullable=True,
        comment="生效日期"
    )
    
    daoqi_riqi = Column(
        DateTime,
        nullable=False,
        comment="到期日期"
    )
    
    # 文件信息
    pdf_lujing = Column(
        String(500),
        nullable=True,
        comment="PDF文件路径"
    )
    
    qianshu_lujing = Column(
        String(500),
        nullable=True,
        comment="签署文件路径"
    )
    
    # 审批信息
    shenpi_ren_id = Column(
        String(36),
        nullable=True,
        comment="审批人ID"
    )
    
    shenpi_riqi = Column(
        DateTime,
        nullable=True,
        comment="审批日期"
    )
    
    shenpi_yijian = Column(
        Text,
        nullable=True,
        comment="审批意见"
    )

    # 阶段2新增：电子签名相关字段
    dianziqianming_lujing = Column(
        String(500),
        nullable=True,
        comment="电子签名文件路径"
    )

    qianming_ren_id = Column(
        String(36),
        nullable=True,
        comment="签名人ID"
    )

    qianming_shijian = Column(
        DateTime,
        nullable=True,
        comment="签名时间"
    )

    qianming_ip = Column(
        String(50),
        nullable=True,
        comment="签名IP地址"
    )

    qianming_beizhu = Column(
        Text,
        nullable=True,
        comment="签名备注"
    )

    # 阶段2新增：合同来源信息
    hetong_laiyuan = Column(
        String(50),
        default="manual",
        nullable=False,
        comment="合同来源：manual(手动创建)、auto_from_quote(报价自动生成)"
    )

    zidong_shengcheng = Column(
        String(1),
        default="N",
        nullable=False,
        comment="是否自动生成：Y(是)、N(否)"
    )

    # 客户签署链接相关字段
    sign_token = Column(
        String(100),
        unique=True,
        nullable=True,
        comment="签署链接的唯一令牌"
    )

    sign_token_expires_at = Column(
        DateTime,
        nullable=True,
        comment="签署链接过期时间"
    )

    customer_signature = Column(
        Text,
        nullable=True,
        comment="客户签名图片（base64）"
    )

    signed_at = Column(
        DateTime,
        nullable=True,
        comment="客户签署时间"
    )

    # 支付相关字段
    payment_status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="支付状态：pending-待支付，paid-已支付，failed-支付失败，refunded-已退款"
    )

    paid_at = Column(
        DateTime,
        nullable=True,
        comment="支付时间"
    )

    payment_amount = Column(
        String(20),
        nullable=True,
        comment="支付金额"
    )

    payment_method = Column(
        String(50),
        nullable=True,
        comment="支付方式：wechat-微信支付，alipay-支付宝，bank-银行转账"
    )

    payment_transaction_id = Column(
        String(100),
        nullable=True,
        comment="支付交易号"
    )

    # 关联关系
    kehu = relationship("Kehu", foreign_keys=[kehu_id])
    hetong_moban = relationship("HetongMoban", back_populates="hetong_list")
    baojia = relationship("XiansuoBaojia", back_populates="hetong_list")
    yifang_zhuti = relationship("HetongYifangZhuti", back_populates="hetong_list")
    zhifu_dingdan_list = relationship(
        "ZhifuDingdan",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    # 新增关联关系
    zhifu_list = relationship(
        "HetongZhifu",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    jine_biangeng_list = relationship(
        "HetongJineBiangeng",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    # 开票申请关系
    kaipiao_shenqing_list = relationship(
        "KaipiaoShenqing",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    # 成本记录关系
    chengben_jilu_list = relationship(
        "ChengbenJilu",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    fuwu_gongdan_list = relationship(
        "FuwuGongdan",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Hetong(hetong_bianhao='{self.hetong_bianhao}', hetong_zhuangtai='{self.hetong_zhuangtai}')>"
