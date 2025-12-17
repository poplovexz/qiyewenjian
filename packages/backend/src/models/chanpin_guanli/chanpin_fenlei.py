"""
产品分类数据模型
"""
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship

from ..base import BaseModel


class ChanpinFenlei(BaseModel):
    """产品分类模型"""
    
    __tablename__ = "chanpin_fenlei"
    __table_args__ = {"comment": "产品分类表"}
    
    fenlei_mingcheng = Column(
        String(100),
        nullable=False,
        comment="分类名称"
    )
    
    fenlei_bianma = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="分类编码"
    )
    
    chanpin_leixing = Column(
        String(20),
        nullable=False,
        comment="产品类型：zengzhi(增值产品)、daili_jizhang(代理记账产品)"
    )
    
    miaoshu = Column(
        Text,
        nullable=True,
        comment="分类描述"
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
    chanpin_xiangmu_list = relationship(
        "ChanpinXiangmu",
        back_populates="fenlei",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ChanpinFenlei(id={self.id}, fenlei_mingcheng={self.fenlei_mingcheng})>"
