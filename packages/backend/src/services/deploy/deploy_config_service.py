"""部署配置服务"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.deploy.deploy_config import DeployConfig
from schemas.deploy.deploy_schemas import (
    DeployConfigCreate,
    DeployConfigUpdate,
    )

class DeployConfigService:
    """部署配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_config(self, environment: str) -> Optional[DeployConfig]:
        """获取指定环境的配置"""
        return self.db.query(DeployConfig).filter(
            DeployConfig.environment == environment,
            DeployConfig.is_deleted == 'N'
        ).first()
    
    def get_all_configs(self) -> List[DeployConfig]:
        """获取所有配置"""
        return self.db.query(DeployConfig).filter(
            DeployConfig.is_deleted == 'N'
        ).order_by(desc(DeployConfig.created_at)).all()
    
    def create_config(self, config: DeployConfigCreate) -> DeployConfig:
        """创建配置"""
        # 检查环境是否已存在
        existing = self.get_config(config.environment)
        if existing:
            raise ValueError(f"环境 {config.environment} 的配置已存在")
        
        db_config = DeployConfig(
            environment=config.environment,
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,  # TODO: 加密存储
            deploy_path=config.deploy_path,
            backup_path=config.backup_path,
            backend_port=config.backend_port,
            frontend_port=config.frontend_port,
            description=config.description,
        )
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def update_config(self, environment: str, config: DeployConfigUpdate) -> DeployConfig:
        """更新配置"""
        db_config = self.get_config(environment)
        if not db_config:
            raise ValueError(f"环境 {environment} 的配置不存在")
        
        # 更新字段
        update_data = config.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def delete_config(self, environment: str) -> bool:
        """删除配置（软删除）"""
        db_config = self.get_config(environment)
        if not db_config:
            return False
        
        db_config.is_deleted = 'Y'
        self.db.commit()
        
        return True
