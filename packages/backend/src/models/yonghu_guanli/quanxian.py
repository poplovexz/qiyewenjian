"""
权限表模型
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..base import BaseModel


class Quanxian(BaseModel):
    """权限表"""
    
    __tablename__ = "quanxian"
    __table_args__ = {"comment": "权限表"}
    
    quanxian_ming = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="权限名称"
    )
    
    quanxian_bianma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="权限编码"
    )
    
    miaoshu = Column(
        String(200),
        nullable=True,
        comment="权限描述"
    )
    
    ziyuan_leixing = Column(
        String(20),
        nullable=False,
        comment="资源类型：menu-菜单，button-按钮，api-接口"
    )
    
    ziyuan_lujing = Column(
        String(200),
        nullable=True,
        comment="资源路径"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-启用，inactive-禁用"
    )
    
    # 关联关系
    jiaose_quanxian_list = relationship(
        "JiaoseQuanxian",
        back_populates="quanxian",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Quanxian(quanxian_ming='{self.quanxian_ming}', quanxian_bianma='{self.quanxian_bianma}')>"
