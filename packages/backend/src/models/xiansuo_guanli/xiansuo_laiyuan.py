"""
线索来源表模型
"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from ..base import BaseModel


class XiansuoLaiyuan(BaseModel):
    """线索来源表"""
    
    __tablename__ = "xiansuo_laiyuan"
    __table_args__ = {"comment": "线索来源表"}
    
    # 基本信息
    laiyuan_mingcheng = Column(
        String(100),
        nullable=False,
        comment="来源名称"
    )
    
    laiyuan_bianma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="来源编码"
    )
    
    laiyuan_leixing = Column(
        String(50),
        nullable=False,
        comment="来源类型：online-线上，offline-线下，referral-推荐"
    )
    
    # 成本信息
    huoqu_chengben = Column(
        Numeric(10, 2),
        default=0.00,
        comment="获取成本（元）"
    )
    
    # 统计信息
    xiansuo_shuliang = Column(
        Integer,
        default=0,
        comment="线索数量"
    )
    
    zhuanhua_shuliang = Column(
        Integer,
        default=0,
        comment="转化数量"
    )
    
    zhuanhua_lv = Column(
        Numeric(5, 2),
        default=0.00,
        comment="转化率（%）"
    )
    
    # 状态信息
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-启用，inactive-停用"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    miaoshu = Column(
        String(500),
        nullable=True,
        comment="描述"
    )
    
    # 关联关系
    xiansuo_list = relationship(
        "Xiansuo",
        back_populates="laiyuan",
        cascade="all, delete-orphan"
    )
