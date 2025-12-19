"""
合同支付模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel

class HetongZhifu(BaseModel):
    """合同支付表"""
    
    __tablename__ = "hetong_zhifu"
    __table_args__ = {"comment": "合同支付表"}
    
    # 合同关联
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id"),
        nullable=False,
        comment="合同ID"
    )
    
    # 支付信息
    zhifu_fangshi = Column(
        String(50),
        nullable=False,
        comment="支付方式：zhifubao(支付宝)、weixin(微信)、yinhang_zhuanzhang(银行转账)"
    )
    
    zhifu_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="支付金额"
    )
    
    zhifu_zhuangtai = Column(
        String(20),
        default="daizhi",
        nullable=False,
        comment="支付状态：daizhi(待支付)、yizhi(已支付)、shibai(支付失败)、tuikuan(已退款)"
    )
    
    # 支付流水信息
    zhifu_liushui_hao = Column(
        String(100),
        nullable=True,
        comment="支付流水号"
    )
    
    zhifu_shijian = Column(
        DateTime,
        nullable=True,
        comment="支付时间"
    )
    
    # 第三方支付信息
    disanfang_dingdan_hao = Column(
        String(100),
        nullable=True,
        comment="第三方订单号"
    )
    
    disanfang_liushui_hao = Column(
        String(100),
        nullable=True,
        comment="第三方流水号"
    )
    
    # 备注信息
    zhifu_beizhu = Column(
        Text,
        nullable=True,
        comment="支付备注"
    )
    
    # 退款信息
    tuikuan_jine = Column(
        Numeric(12, 2),
        default=0.00,
        comment="退款金额"
    )
    
    tuikuan_shijian = Column(
        DateTime,
        nullable=True,
        comment="退款时间"
    )
    
    tuikuan_yuanyin = Column(
        Text,
        nullable=True,
        comment="退款原因"
    )
    
    # 关联关系
    hetong = relationship(
        "Hetong",
        back_populates="zhifu_list"
    )
    
    huikuan_danju_list = relationship(
        "YinhangHuikuanDanju",
        back_populates="hetong_zhifu",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<HetongZhifu(hetong_id='{self.hetong_id}', zhifu_fangshi='{self.zhifu_fangshi}')>"
