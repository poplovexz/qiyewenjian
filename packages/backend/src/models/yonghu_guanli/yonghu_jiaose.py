"""
用户角色关联表模型
"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import BaseModel


class YonghuJiaose(BaseModel):
    """用户角色关联表"""
    
    __tablename__ = "yonghu_jiaose"
    __table_args__ = {"comment": "用户角色关联表"}
    
    yonghu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    jiaose_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jiaose.id", ondelete="CASCADE"),
        nullable=False,
        comment="角色ID"
    )
    
    # 关联关系
    yonghu = relationship("Yonghu", back_populates="yonghu_jiaose_list")
    jiaose = relationship("Jiaose", back_populates="yonghu_jiaose_list")
    
    def __repr__(self) -> str:
        return f"<YonghuJiaose(yonghu_id='{self.yonghu_id}', jiaose_id='{self.jiaose_id}')>"
