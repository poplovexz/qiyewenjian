"""
产品步骤数据模型
"""
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel


class ChanpinBuzou(BaseModel):
    """产品步骤模型"""
    
    __tablename__ = "chanpin_buzou"
    __table_args__ = {"comment": "产品步骤表"}
    
    buzou_mingcheng = Column(
        String(200),
        nullable=False,
        comment="步骤名称"
    )
    
    xiangmu_id = Column(
        String(36),
        ForeignKey("chanpin_xiangmu.id"),
        nullable=False,
        comment="所属项目ID"
    )
    
    yugu_shichang = Column(
        Numeric(5, 2),
        nullable=False,
        default=1.00,
        comment="预估时长（天）"
    )
    
    shichang_danwei = Column(
        String(10),
        default="tian",
        comment="时长单位：tian(天)、xiaoshi(小时)"
    )
    
    buzou_feiyong = Column(
        Numeric(10, 2),
        default=0.00,
        comment="步骤费用"
    )
    
    buzou_miaoshu = Column(
        Text,
        nullable=True,
        comment="步骤描述"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    shi_bixu = Column(
        String(1),
        default="Y",
        comment="是否必须：Y(是)、N(否)"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )
    
    # 关联关系
    xiangmu = relationship(
        "ChanpinXiangmu",
        back_populates="buzou_list"
    )
    
    def __repr__(self):
        return f"<ChanpinBuzou(id={self.id}, buzou_mingcheng={self.buzou_mingcheng})>"
