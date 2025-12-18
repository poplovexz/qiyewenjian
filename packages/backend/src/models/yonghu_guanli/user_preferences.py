"""
用户偏好设置模型
"""
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import BaseModel


class UserPreferences(BaseModel):
    """用户偏好设置"""
    __tablename__ = "user_preferences"
    
    user_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    preference_key = Column(
        String(100),
        nullable=False,
        comment="偏好键"
    )
    
    preference_value = Column(
        String(500),
        nullable=True,
        comment="偏好值"
    )
    
    # 添加唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'preference_key', name='uk_user_preference'),
    )
    
    # 关系
    user = relationship("Yonghu", back_populates="preferences")

