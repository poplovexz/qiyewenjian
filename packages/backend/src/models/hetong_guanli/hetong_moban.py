"""
合同模板表模型
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from ..base import BaseModel


class HetongMoban(BaseModel):
    """合同模板表"""
    
    __tablename__ = "hetong_moban"
    __table_args__ = {"comment": "合同模板表"}
    
    moban_mingcheng = Column(
        String(100),
        nullable=False,
        comment="模板名称"
    )
    
    moban_leixing = Column(
        String(50),
        nullable=False,
        comment="模板类型：daili_jizhang-代理记账，zengzhi_fuwu-增值服务，baomi_xieyi-保密协议"
    )
    
    moban_neirong = Column(
        Text,
        nullable=False,
        comment="模板内容"
    )
    
    moban_banben = Column(
        String(20),
        default="1.0",
        nullable=False,
        comment="模板版本"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-启用，inactive-禁用，archived-已归档"
    )
    
    shiyong_fanwei = Column(
        String(200),
        nullable=True,
        comment="适用范围"
    )
    
    # 关联关系
    hetong_list = relationship(
        "Hetong",
        back_populates="hetong_moban",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<HetongMoban(moban_mingcheng='{self.moban_mingcheng}', moban_leixing='{self.moban_leixing}')>"
