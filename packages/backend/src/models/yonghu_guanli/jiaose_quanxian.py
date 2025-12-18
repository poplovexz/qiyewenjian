"""
角色权限关联表模型
"""
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from ..base import BaseModel


class JiaoseQuanxian(BaseModel):
    """角色权限关联表"""
    
    __tablename__ = "jiaose_quanxian"
    __table_args__ = {"comment": "角色权限关联表"}
    
    jiaose_id = Column(
        String(36),
        ForeignKey("jiaose.id", ondelete="CASCADE"),
        nullable=False,
        comment="角色ID"
    )

    quanxian_id = Column(
        String(36),
        ForeignKey("quanxian.id", ondelete="CASCADE"),
        nullable=False,
        comment="权限ID"
    )
    
    # 关联关系
    jiaose = relationship("Jiaose", back_populates="jiaose_quanxian_list")
    quanxian = relationship("Quanxian", back_populates="jiaose_quanxian_list")
    
    def __repr__(self) -> str:
        return f"<JiaoseQuanxian(jiaose_id='{self.jiaose_id}', quanxian_id='{self.quanxian_id}')>"
