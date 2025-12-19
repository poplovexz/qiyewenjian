"""部署配置模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.base import Base

class DeployConfig(Base):
    """部署配置表"""
    __tablename__ = "deploy_config"
    __table_args__ = {'comment': '部署配置表'}

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    environment = Column(String(50), unique=True, nullable=False, comment="环境名称")
    host = Column(String(100), nullable=False, comment="服务器IP地址")
    port = Column(Integer, default=22, comment="SSH端口")
    username = Column(String(50), nullable=False, comment="SSH用户名")
    password = Column(String(255), comment="SSH密码（加密存储）")
    deploy_path = Column(String(255), nullable=False, comment="部署目录路径")
    backup_path = Column(String(255), comment="备份目录路径")

    # 服务配置
    backend_port = Column(Integer, default=8000, comment="后端服务端口")
    frontend_port = Column(Integer, comment="前端服务端口（Nginx）")

    # 其他配置
    description = Column(Text, comment="配置说明")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    is_deleted = Column(String(1), nullable=False, default='N', comment="是否删除")
