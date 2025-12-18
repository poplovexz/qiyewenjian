"""
系统配置服务
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
import time

from models.xitong_guanli.system_config import SystemConfig
from schemas.xitong_guanli.system_config_schemas import (
    SystemConfigUpdate,
    SystemConfigBatchUpdate,
    SystemInfoResponse,
    CacheClearResponse
)
from core.redis_client import redis_client


# 系统启动时间
_start_time = time.time()


class SystemConfigService:
    """系统配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_configs(self) -> List[SystemConfig]:
        """获取所有配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.is_deleted == "N"
        ).order_by(SystemConfig.sort_order, SystemConfig.config_key).all()
    
    def get_configs_by_type(self, config_type: str) -> List[SystemConfig]:
        """根据类型获取配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.config_type == config_type,
            SystemConfig.is_deleted == "N"
        ).order_by(SystemConfig.sort_order, SystemConfig.config_key).all()
    
    def get_config_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """根据键获取配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key,
            SystemConfig.is_deleted == "N"
        ).first()
    
    def update_config(self, config_key: str, config_update: SystemConfigUpdate) -> SystemConfig:
        """更新配置"""
        config = self.get_config_by_key(config_key)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"配置项 {config_key} 不存在"
            )
        
        if config.is_editable == "N":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置项 {config_key} 不可编辑"
            )
        
        # 验证值类型
        self._validate_value_type(config.value_type, config_update.config_value)
        
        config.config_value = config_update.config_value
        self.db.commit()
        self.db.refresh(config)

        return config
    
    def batch_update_configs(self, batch_update: SystemConfigBatchUpdate) -> Dict[str, str]:
        """批量更新配置"""
        updated = {}
        errors = {}
        
        for config_key, config_value in batch_update.configs.items():
            try:
                config = self.get_config_by_key(config_key)
                
                if not config:
                    errors[config_key] = "配置项不存在"
                    continue
                
                if config.is_editable == "N":
                    errors[config_key] = "配置项不可编辑"
                    continue
                
                # 验证值类型
                self._validate_value_type(config.value_type, config_value)
                
                config.config_value = config_value
                updated[config_key] = config_value
                
            except Exception as e:
                errors[config_key] = str(e)
        
        if updated:
            self.db.commit()

        return {
            "updated": updated,
            "errors": errors
        }
    
    def get_system_info(self) -> SystemInfoResponse:
        """获取系统信息"""
        # 计算运行时间
        uptime_seconds = int(time.time() - _start_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        
        uptime = f"{days}天 {hours}小时 {minutes}分钟"
        
        # 检查数据库状态
        try:
            self.db.execute("SELECT 1")
            database_status = "正常"
        except Exception:
            database_status = "异常"
        
        # 检查Redis状态
        try:
            if redis_client._connected and redis_client.redis:
                redis_status = "正常"
            else:
                redis_status = "未连接"
        except Exception:
            redis_status = "异常"
        
        return SystemInfoResponse(
            system_name="代理记账营运内部系统",
            version="1.0.0",
            environment="production",
            database_status=database_status,
            redis_status=redis_status,
            uptime=uptime
        )
    
    @staticmethod
    async def clear_cache(pattern: Optional[str] = None) -> CacheClearResponse:
        """清除缓存"""
        try:
            cleared = 0
            if redis_client._connected and redis_client.redis:
                if pattern:
                    # 查找匹配的键
                    keys = await redis_client.redis.keys(pattern)
                    if keys:
                        cleared = await redis_client.redis.delete(*keys)
                else:
                    # 清除所有缓存
                    await redis_client.redis.flushdb()
                    cleared = -1  # 表示清除了所有

            return CacheClearResponse(
                message="缓存已清除" if cleared != 0 else "Redis未连接或无匹配的缓存",
                cleared_keys=cleared if cleared >= 0 else 0
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清除缓存失败: {str(e)}"
            )
    
    @staticmethod
    def _validate_value_type(value_type: Optional[str], value: str):
        """验证值类型"""
        if not value_type:
            return
        
        try:
            if value_type == "int":
                int(value)
            elif value_type == "float":
                float(value)
            elif value_type == "bool":
                if value.lower() not in ["true", "false", "1", "0"]:
                    raise ValueError("布尔值必须是 true/false 或 1/0")
            elif value_type == "json":
                json.loads(value)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"值类型验证失败: {str(e)}"
            )

