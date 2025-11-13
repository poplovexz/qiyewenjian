"""部署配置API端点"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models import Yonghu
from services.deploy.deploy_config_service import DeployConfigService
from schemas.deploy.deploy_schemas import (
    DeployConfigCreate,
    DeployConfigUpdate,
    DeployConfigResponse,
)

router = APIRouter()


@router.get("/configs", response_model=List[DeployConfigResponse])
def get_all_configs(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取所有部署配置"""
    service = DeployConfigService(db)
    configs = service.get_all_configs()
    
    # 不返回密码
    return [
        DeployConfigResponse(
            id=config.id,
            environment=config.environment,
            host=config.host,
            port=config.port,
            username=config.username,
            deploy_path=config.deploy_path,
            backup_path=config.backup_path,
            backend_port=config.backend_port,
            frontend_port=config.frontend_port,
            description=config.description,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
        for config in configs
    ]


@router.get("/configs/{environment}", response_model=DeployConfigResponse)
def get_config(
    environment: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取指定环境的配置"""
    service = DeployConfigService(db)
    config = service.get_config(environment)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"环境 {environment} 的配置不存在")
    
    return DeployConfigResponse(
        id=config.id,
        environment=config.environment,
        host=config.host,
        port=config.port,
        username=config.username,
        deploy_path=config.deploy_path,
        backup_path=config.backup_path,
        backend_port=config.backend_port,
        frontend_port=config.frontend_port,
        description=config.description,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.post("/configs", response_model=DeployConfigResponse)
def create_config(
    config: DeployConfigCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建部署配置"""
    service = DeployConfigService(db)
    
    try:
        db_config = service.create_config(config)
        return DeployConfigResponse(
            id=db_config.id,
            environment=db_config.environment,
            host=db_config.host,
            port=db_config.port,
            username=db_config.username,
            deploy_path=db_config.deploy_path,
            backup_path=db_config.backup_path,
            backend_port=db_config.backend_port,
            frontend_port=db_config.frontend_port,
            description=db_config.description,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/configs/{environment}", response_model=DeployConfigResponse)
def update_config(
    environment: str,
    config: DeployConfigUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新部署配置"""
    service = DeployConfigService(db)
    
    try:
        db_config = service.update_config(environment, config)
        return DeployConfigResponse(
            id=db_config.id,
            environment=db_config.environment,
            host=db_config.host,
            port=db_config.port,
            username=db_config.username,
            deploy_path=db_config.deploy_path,
            backup_path=db_config.backup_path,
            backend_port=db_config.backend_port,
            frontend_port=db_config.frontend_port,
            description=db_config.description,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/configs/{environment}")
def delete_config(
    environment: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除部署配置"""
    service = DeployConfigService(db)
    
    if not service.delete_config(environment):
        raise HTTPException(status_code=404, detail=f"环境 {environment} 的配置不存在")
    
    return {"message": "配置已删除"}

