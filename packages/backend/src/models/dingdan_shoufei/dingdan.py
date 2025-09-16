"""
订单表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import BaseModel


class Dingdan(BaseModel):
    """订单表"""
    
    __tablename__ = "dingdan"
    __table_args__ = {"comment": "订单表"}
    
    kehu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    # 订单基本信息
    dingdan_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="订单编号"
    )
    
    taocan_leixing = Column(
        String(50),
        nullable=False,
        comment="套餐类型：basic-基础套餐，standard-标准套餐，premium-高级套餐，custom-定制套餐"
    )
    
    fuwu_neirong = Column(
        String(500),
        nullable=True,
        comment="服务内容描述"
    )
    
    # 价格信息
    jiben_feiyong = Column(
        Numeric(10, 2),
        nullable=False,
        comment="基本费用"
    )
    
    fujia_feiyong = Column(
        Numeric(10, 2),
        default=0.00,
        comment="附加费用"
    )
    
    zongje = Column(
        Numeric(10, 2),
        nullable=False,
        comment="订单总金额"
    )
    
    # 订单状态
    dingdan_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="订单状态：pending-待支付，paid-已支付，processing-处理中，completed-已完成，cancelled-已取消，refunded-已退款"
    )
    
    # 支付信息
    zhifu_fangshi = Column(
        String(20),
        nullable=True,
        comment="支付方式：alipay-支付宝，wechat-微信，bank-银行转账，cash-现金"
    )
    
    zhifu_riqi = Column(
        DateTime,
        nullable=True,
        comment="支付日期"
    )
    
    zhifu_liushui = Column(
        String(100),
        nullable=True,
        comment="支付流水号"
    )
    
    # 服务周期
    fuwu_kaishi = Column(
        DateTime,
        nullable=True,
        comment="服务开始时间"
    )
    
    fuwu_jieshu = Column(
        DateTime,
        nullable=True,
        comment="服务结束时间"
    )
    
    # 关联关系
    fapiao_list = relationship(
        "Fapiao",
        back_populates="dingdan",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Dingdan(dingdan_bianhao='{self.dingdan_bianhao}', zongje='{self.zongje}')>"
