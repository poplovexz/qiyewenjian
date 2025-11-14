"""部署历史数据库模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from core.database import Base
import enum


class DeployStatus(str, enum.Enum):
    """部署状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 运行中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class DeployHistory(Base):
    """部署历史表"""
    __tablename__ = "deploy_history"
    __table_args__ = {"comment": "部署历史记录表"}

    id = Column(Integer, primary_key=True, index=True, comment="部署ID")
    environment = Column(
        String(50),
        nullable=False,
        default="production",
        comment="部署环境: production/staging/development"
    )
    branch = Column(String(100), nullable=False, default="main", comment="Git分支名称")
    commit_hash = Column(String(40), nullable=True, comment="Git提交哈希")
    status = Column(
        SQLEnum(DeployStatus),
        nullable=False,
        default=DeployStatus.PENDING,
        comment="部署状态"
    )
    deployed_by = Column(String(100), nullable=False, comment="部署人用户名")
    description = Column(Text, nullable=True, comment="部署说明")
    logs = Column(Text, nullable=True, comment="部署日志")
    error_message = Column(Text, nullable=True, comment="错误信息")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    duration = Column(Integer, nullable=True, comment="耗时（秒）")
    
    # 审计字段
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    is_deleted = Column(String(1), nullable=False, default="N", comment="是否删除: Y/N")

    def __repr__(self):
        return f"<DeployHistory(id={self.id}, environment={self.environment}, status={self.status})>"

