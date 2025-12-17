"""
数据库基础模型类
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import uuid


@as_declarative()
class Base:
    """数据库基础模型类"""
    
    id: Any
    __name__: str
    
    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class BaseModel(Base):
    """包含通用字段的基础模型"""
    
    __abstract__ = True
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键ID"
    )
    
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
    
    created_by = Column(
        String(36),
        nullable=True,
        comment="创建人ID"
    )

    updated_by = Column(
        String(36),
        nullable=True,
        comment="更新人ID"
    )
    
    is_deleted = Column(
        String(1),
        default="N",
        nullable=False,
        comment="是否删除 Y/N"
    )
    
    remark = Column(
        String(500),
        nullable=True,
        comment="备注"
    )
