"""
产品项目数据模型
"""
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel

class ChanpinXiangmu(BaseModel):
    """产品项目模型"""
    
    __tablename__ = "chanpin_xiangmu"
    __table_args__ = {"comment": "产品项目表"}
    
    xiangmu_mingcheng = Column(
        String(200),
        nullable=False,
        comment="项目名称"
    )
    
    xiangmu_bianma = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="项目编码"
    )
    
    fenlei_id = Column(
        String(36),
        ForeignKey("chanpin_fenlei.id"),
        nullable=False,
        comment="所属分类ID"
    )
    
    yewu_baojia = Column(
        Numeric(10, 2),
        nullable=False,
        default=0.00,
        comment="业务报价"
    )
    
    baojia_danwei = Column(
        String(20),
        default="yuan",
        comment="报价单位：yuan(元)、ge(个)、ci(次)等"
    )
    
    banshi_tianshu = Column(
        Integer,
        default=0,
        comment="办事天数"
    )
    
    xiangmu_beizhu = Column(
        Text,
        nullable=True,
        comment="项目备注"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )
    
    # 关联关系
    fenlei = relationship(
        "ChanpinFenlei",
        back_populates="chanpin_xiangmu_list"
    )
    
    buzou_list = relationship(
        "ChanpinBuzou",
        back_populates="xiangmu",
        cascade="all, delete-orphan",
        order_by="ChanpinBuzou.paixu"
    )
    
    def __repr__(self):
        return f"<ChanpinXiangmu(id={self.id}, xiangmu_mingcheng={self.xiangmu_mingcheng})>"
