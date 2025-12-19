"""
系统配置API端点
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli.yonghu import Yonghu
from schemas.xitong_guanli.system_config_schemas import (
    SystemConfigResponse,
    SystemConfigUpdate,
    SystemConfigBatchUpdate,
    SystemInfoResponse,
    CacheClearResponse
)
from services.xitong_guanli.system_config_service import SystemConfigService

router = APIRouter()

@router.get("/info", response_model=SystemInfoResponse, summary="获取系统信息")
def get_system_info(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取系统基本信息
    
    包括：
    - 系统名称和版本
    - 运行环境
    - 数据库状态
    - Redis状态
    - 系统运行时间
    """
    service = SystemConfigService(db)
    return service.get_system_info()

@router.get("/configs", response_model=List[SystemConfigResponse], summary="获取所有配置")
def get_all_configs(
    config_type: Optional[str] = Query(None, description="配置类型筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("system:config:read"))
):
    """
    获取所有系统配置
    
    可选参数：
    - config_type: 配置类型（security/cache/business/system）
    """
    service = SystemConfigService(db)
    
    if config_type:
        configs = service.get_configs_by_type(config_type)
    else:
        configs = service.get_all_configs()
    
    return configs

@router.get("/configs/{config_key}", response_model=SystemConfigResponse, summary="获取单个配置")
def get_config_by_key(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("system:config:read"))
):
    """
    根据配置键获取配置
    """
    service = SystemConfigService(db)
    config = service.get_config_by_key(config_key)
    
    if not config:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 {config_key} 不存在"
        )
    
    return config

@router.put("/configs/{config_key}", response_model=SystemConfigResponse, summary="更新配置")
def update_config(
    config_key: str,
    config_update: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("system:config:update"))
):
    """
    更新单个配置项
    """
    service = SystemConfigService(db)
    return service.update_config(config_key, config_update)

@router.put("/configs", response_model=Dict, summary="批量更新配置")
def batch_update_configs(
    batch_update: SystemConfigBatchUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("system:config:update"))
):
    """
    批量更新配置项
    
    请求体示例：
    ```json
    {
      "configs": {
        "token_expire_hours": "8",
        "cache_default_minutes": "15"
      }
    }
    ```
    """
    service = SystemConfigService(db)
    return service.batch_update_configs(batch_update)

@router.post("/cache/clear", response_model=CacheClearResponse, summary="清除缓存")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="缓存键模式，如：user:*"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("system:cache:clear"))
):
    """
    清除缓存

    参数：
    - pattern: 缓存键模式（可选），不提供则清除所有缓存
    """
    service = SystemConfigService(db)
    return await service.clear_cache(pattern)
