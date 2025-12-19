"""
发票表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey

from sqlalchemy.orm import relationship

from ..base import BaseModel

class Fapiao(BaseModel):
    """发票表"""
    
    __tablename__ = "fapiao"
    __table_args__ = {"comment": "发票表"}
    
    dingdan_id = Column(
        String(36),
        ForeignKey("dingdan.id", ondelete="CASCADE"),
        nullable=False,
        comment="订单ID"
    )
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    # 发票基本信息
    fapiao_haoma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="发票号码"
    )
    
    fapiao_leixing = Column(
        String(20),
        nullable=False,
        comment="发票类型：putong-增值税普通发票，zhuanyong-增值税专用发票"
    )
    
    fapiao_mingcheng = Column(
        String(200),
        nullable=False,
        comment="发票名称"
    )
    
    # 开票信息
    kaipiao_riqi = Column(
        DateTime,
        nullable=False,
        comment="开票日期"
    )
    
    kaipiao_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="开票金额"
    )
    
    shuie = Column(
        Numeric(10, 2),
        default=0.00,
        comment="税额"
    )
    
    jia_shui_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="价税合计金额"
    )
    
    # 发票状态
    fapiao_zhuangtai = Column(
        String(20),
        default="normal",
        nullable=False,
        comment="发票状态：normal-正常，cancelled-作废，red-红冲"
    )
    
    # 文件信息
    pdf_lujing = Column(
        String(500),
        nullable=True,
        comment="发票PDF文件路径"
    )
    
    # 作废/红冲信息
    zuofei_riqi = Column(
        DateTime,
        nullable=True,
        comment="作废日期"
    )
    
    zuofei_yuanyin = Column(
        String(200),
        nullable=True,
        comment="作废原因"
    )
    
    # 关联关系
    dingdan = relationship("Dingdan", back_populates="fapiao_list")
    
    def __repr__(self) -> str:
        return f"<Fapiao(fapiao_haoma='{self.fapiao_haoma}', kaipiao_jine='{self.kaipiao_jine}')>"
