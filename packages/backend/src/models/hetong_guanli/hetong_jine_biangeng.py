"""
合同金额变更记录模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel

class HetongJineBiangeng(BaseModel):
    """合同金额变更记录表"""
    
    __tablename__ = "hetong_jine_biangeng"
    __table_args__ = {"comment": "合同金额变更记录表"}
    
    # 合同关联
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id"),
        nullable=False,
        comment="合同ID"
    )
    
    # 金额信息
    yuanshi_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="原始金额"
    )
    
    xiuzheng_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="修正金额"
    )
    
    biangeng_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="变更金额（修正金额-原始金额）"
    )
    
    biangeng_bili = Column(
        Numeric(5, 2),
        nullable=True,
        comment="变更比例（百分比）"
    )
    
    # 变更信息
    biangeng_yuanyin = Column(
        Text,
        nullable=False,
        comment="变更原因"
    )
    
    biangeng_ren_id = Column(
        String(36),
        nullable=False,
        comment="变更人ID"
    )
    
    biangeng_shijian = Column(
        DateTime,
        nullable=True,
        comment="变更时间"
    )
    
    # 审核关联
    shenhe_liucheng_id = Column(
        String(36),
        ForeignKey("shenhe_liucheng.id"),
        nullable=True,
        comment="关联的审核流程ID"
    )
    
    # 状态信息
    biangeng_zhuangtai = Column(
        String(20),
        default="daishehe",
        nullable=False,
        comment="变更状态：daishehe(待审核)、tongguo(已通过)、jujue(已拒绝)"
    )
    
    # 备注
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong = relationship(
        "Hetong",
        back_populates="jine_biangeng_list"
    )
    
    shenhe_liucheng = relationship(
        "ShenheLiucheng"
    )
    
    def __repr__(self) -> str:
        return f"<HetongJineBiangeng(hetong_id='{self.hetong_id}', yuanshi_jine={self.yuanshi_jine}, xiuzheng_jine={self.xiuzheng_jine})>"
