"""
角色表模型
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..base import BaseModel


class Jiaose(BaseModel):
    """角色表"""
    
    __tablename__ = "jiaose"
    __table_args__ = {"comment": "角色表"}
    
    jiaose_ming = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="角色名称"
    )
    
    jiaose_bianma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="角色编码"
    )
    
    miaoshu = Column(
        String(200),
        nullable=True,
        comment="角色描述"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-启用，inactive-禁用"
    )
    
    # 关联关系
    yonghu_jiaose_list = relationship(
        "YonghuJiaose",
        back_populates="jiaose",
        cascade="all, delete-orphan"
    )
    
    jiaose_quanxian_list = relationship(
        "JiaoseQuanxian",
        back_populates="jiaose",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Jiaose(jiaose_ming='{self.jiaose_ming}', jiaose_bianma='{self.jiaose_bianma}')>"
