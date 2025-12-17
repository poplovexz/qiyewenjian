"""
合同支付方式表模型 - 关联支付配置
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel


class HetongZhifuFangshi(BaseModel):
    """合同支付方式表 - 关联乙方主体和支付配置"""

    __tablename__ = "hetong_zhifu_fangshi"
    __table_args__ = {"comment": "合同支付方式表 - 关联乙方主体和支付配置"}

    # 关联信息
    yifang_zhuti_id = Column(
        String(36),
        ForeignKey("hetong_yifang_zhuti.id", ondelete="CASCADE"),
        nullable=False,
        comment="乙方主体ID"
    )

    zhifu_peizhi_id = Column(
        String(36),
        ForeignKey("zhifu_peizhi.id", ondelete="CASCADE"),
        nullable=False,
        comment="支付配置ID - 关联到支付配置管理"
    )

    # 支付方式信息
    zhifu_mingcheng = Column(
        String(100),
        nullable=False,
        comment="支付方式名称"
    )

    # 状态信息
    zhifu_zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="支付状态：active(启用)、inactive(停用)"
    )

    shi_moren = Column(
        String(1),
        default="N",
        nullable=False,
        comment="是否默认：Y(是)、N(否)"
    )

    # 排序
    paixu = Column(
        String(10),
        default="0",
        nullable=False,
        comment="排序号"
    )

    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 关联关系
    yifang_zhuti = relationship("HetongYifangZhuti", back_populates="zhifu_fangshi_list")
    zhifu_peizhi = relationship("ZhifuPeizhi")

    def __repr__(self) -> str:
        return f"<HetongZhifuFangshi(zhifu_mingcheng='{self.zhifu_mingcheng}')>"
