"""
系统配置Schema
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    id: str
    config_key: str
    config_value: Optional[str] = None
    config_type: str
    config_name: Optional[str] = None
    config_desc: Optional[str] = None
    default_value: Optional[str] = None
    value_type: Optional[str] = None
    is_editable: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    config_value: str = Field(..., description="配置值")

class SystemConfigBatchUpdate(BaseModel):
    """批量更新系统配置"""
    configs: Dict[str, str] = Field(..., description="配置键值对")

class SystemInfoResponse(BaseModel):
    """系统信息响应"""
    system_name: str = Field(default="代理记账营运内部系统", description="系统名称")
    version: str = Field(default="1.0.0", description="系统版本")
    environment: str = Field(default="production", description="运行环境")
    database_status: str = Field(default="connected", description="数据库状态")
    redis_status: str = Field(default="connected", description="Redis状态")
    uptime: str = Field(default="", description="运行时间")

class CacheClearResponse(BaseModel):
    """清除缓存响应"""
    message: str = Field(default="缓存已清除", description="响应消息")
    cleared_keys: int = Field(default=0, description="清除的键数量")
