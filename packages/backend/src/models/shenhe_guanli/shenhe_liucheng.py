"""
审核流程模型
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..base import BaseModel

class ShenheLiucheng(BaseModel):
    """审核流程表"""
    
    __tablename__ = "shenhe_liucheng"
    __table_args__ = {"comment": "审核流程表"}
    
    # 流程基本信息
    liucheng_bianhao = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="流程编号"
    )
    
    shenhe_leixing = Column(
        String(50),
        nullable=False,
        comment="审核类型：hetong(合同审核)、baojia(报价审核)"
    )
    
    guanlian_id = Column(
        String(36),
        nullable=False,
        comment="关联ID：合同ID或报价ID"
    )
    
    # 审核状态
    shenhe_zhuangtai = Column(
        String(20),
        default="daishehe",
        nullable=False,
        comment="审核状态：daishehe(待审核)、shenhzhong(审核中)、tongguo(已通过)、jujue(已拒绝)、chexiao(已撤销)"
    )
    
    # 规则关联
    chufa_guize_id = Column(
        String(36),
        ForeignKey("shenhe_guize.id"),
        nullable=False,
        comment="触发规则ID"
    )
    
    # 流程进度
    dangqian_buzhou = Column(
        Integer,
        default=1,
        nullable=False,
        comment="当前步骤"
    )
    
    zonggong_buzhou = Column(
        Integer,
        nullable=False,
        comment="总共步骤"
    )
    
    # 申请信息
    shenqing_ren_id = Column(
        String(36),
        nullable=False,
        comment="申请人ID"
    )
    
    shenqing_yuanyin = Column(
        Text,
        nullable=True,
        comment="申请原因"
    )
    
    shenqing_shijian = Column(
        DateTime,
        nullable=True,
        comment="申请时间"
    )
    
    # 完成信息
    wancheng_shijian = Column(
        DateTime,
        nullable=True,
        comment="完成时间"
    )
    
    # 备注
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    chufa_guize = relationship(
        "ShenheGuize",
        back_populates="shenhe_liucheng_list"
    )
    
    shenhe_jilu_list = relationship(
        "ShenheJilu",
        back_populates="shenhe_liucheng",
        cascade="all, delete-orphan",
        order_by="ShenheJilu.buzhou_bianhao"
    )
    
    def __repr__(self) -> str:
        return f"<ShenheLiucheng(liucheng_bianhao='{self.liucheng_bianhao}', shenhe_leixing='{self.shenhe_leixing}')>"
