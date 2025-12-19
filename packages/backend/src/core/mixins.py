"""
数据库模型 Mixin 类
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import CHAR

class UUIDMixin:
    """UUID主键 Mixin"""
    
    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键ID"
    )

class TimestampMixin:
    """时间戳 Mixin"""
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

class UserTrackingMixin:
    """用户跟踪 Mixin"""
    
    created_by = Column(
        CHAR(36),
        nullable=True,
        comment="创建人ID"
    )

    updated_by = Column(
        CHAR(36),
        nullable=True,
        comment="更新人ID"
    )

class SoftDeleteMixin:
    """软删除 Mixin"""
    
    is_deleted = Column(
        CHAR(1),
        default="N",
        nullable=False,
        comment="是否删除：Y-是，N-否"
    )

class RemarkMixin:
    """备注 Mixin"""
    
    beizhu = Column(
        String(500),
        nullable=True,
        comment="备注"
    )

class FullMixin(UUIDMixin, TimestampMixin, UserTrackingMixin, SoftDeleteMixin):
    """完整的 Mixin，包含所有常用字段"""
    pass
