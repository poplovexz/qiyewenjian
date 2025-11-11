"""
用户表模型
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from ..base import BaseModel


class Yonghu(BaseModel):
    """用户表"""
    
    __tablename__ = "yonghu"
    __table_args__ = {"comment": "用户表"}
    
    # 基本信息
    yonghu_ming = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名"
    )
    
    mima = Column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    youxiang = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="邮箱"
    )
    
    xingming = Column(
        String(50),
        nullable=False,
        comment="姓名"
    )
    
    shouji = Column(
        String(20),
        nullable=True,
        comment="手机号码"
    )
    
    # 状态信息
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-活跃，inactive-非活跃，locked-锁定"
    )
    
    zuihou_denglu = Column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    
    denglu_cishu = Column(
        String(10),
        default="0",
        comment="登录次数"
    )
    
    # 关联关系
    yonghu_jiaose_list = relationship(
        "YonghuJiaose",
        back_populates="yonghu",
        cascade="all, delete-orphan"
    )

    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Yonghu(yonghu_ming='{self.yonghu_ming}', xingming='{self.xingming}')>"
