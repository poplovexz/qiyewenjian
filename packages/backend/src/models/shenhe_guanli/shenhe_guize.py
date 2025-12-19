"""
审核规则配置模型
"""
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship

from ..base import BaseModel

class ShenheGuize(BaseModel):
    """审核规则配置表"""
    
    __tablename__ = "shenhe_guize"
    __table_args__ = {"comment": "审核规则配置表"}
    
    # 基本信息
    guize_mingcheng = Column(
        String(200),
        nullable=False,
        comment="规则名称"
    )
    
    guize_leixing = Column(
        String(50),
        nullable=False,
        comment="规则类型：hetong_jine_xiuzheng(合同金额修正)、baojia_shenhe(报价审核)"
    )
    
    # 触发条件配置
    chufa_tiaojian = Column(
        Text,
        nullable=False,
        comment="触发条件配置（JSON格式）：如金额阈值、百分比等"
    )
    
    # 审核流程配置
    shenhe_liucheng_peizhi = Column(
        Text,
        nullable=False,
        comment="审核流程配置（JSON格式）：审核步骤、审核人员等"
    )
    
    # 状态和排序
    shi_qiyong = Column(
        String(1),
        default="Y",
        nullable=False,
        comment="是否启用：Y(是)、N(否)"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号，数字越小优先级越高"
    )
    
    # 描述信息
    guize_miaoshu = Column(
        Text,
        nullable=True,
        comment="规则描述"
    )
    
    # 关联关系
    shenhe_liucheng_list = relationship(
        "ShenheLiucheng",
        back_populates="chufa_guize",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ShenheGuize(guize_mingcheng='{self.guize_mingcheng}', guize_leixing='{self.guize_leixing}')>"
