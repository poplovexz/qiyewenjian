"""部署管理相关的Pydantic schemas"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class DeployTriggerRequest(BaseModel):
    """触发部署请求"""
    environment: Literal["production", "staging", "development"] = Field(
        default="production",
        description="部署环境"
    )
    branch: str = Field(
        default="main",
        description="Git分支名称"
    )
    description: Optional[str] = Field(
        default=None,
        description="部署说明"
    )
    skip_build: bool = Field(
        default=False,
        description="是否跳过构建步骤"
    )
    skip_migration: bool = Field(
        default=False,
        description="是否跳过数据库迁移"
    )


class DeployStatusResponse(BaseModel):
    """部署状态响应"""
    deploy_id: int = Field(description="部署ID")
    status: Literal["pending", "running", "success", "failed", "cancelled"] = Field(
        description="部署状态"
    )
    environment: str = Field(description="部署环境")
    branch: str = Field(description="Git分支")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration: Optional[int] = Field(default=None, description="耗时（秒）")
    deployed_by: str = Field(description="部署人")
    commit_hash: Optional[str] = Field(default=None, description="Git提交哈希")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class DeployLogResponse(BaseModel):
    """部署日志响应"""
    deploy_id: int = Field(description="部署ID")
    logs: List[str] = Field(description="日志行列表")
    is_complete: bool = Field(description="是否完成")


class DeployHistoryItem(BaseModel):
    """部署历史项"""
    id: int = Field(description="部署ID")
    environment: str = Field(description="部署环境")
    branch: str = Field(description="Git分支")
    status: str = Field(description="部署状态")
    started_at: datetime = Field(description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration: Optional[int] = Field(default=None, description="耗时（秒）")
    deployed_by: str = Field(description="部署人")
    commit_hash: Optional[str] = Field(default=None, description="Git提交哈希")
    description: Optional[str] = Field(default=None, description="部署说明")


class DeployHistoryListResponse(BaseModel):
    """部署历史列表响应"""
    items: List[DeployHistoryItem] = Field(description="部署历史列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页")
    size: int = Field(description="每页大小")


class DeployHistoryResponse(BaseModel):
    """部署历史详情响应"""
    id: int = Field(description="部署ID")
    environment: str = Field(description="部署环境")
    branch: str = Field(description="Git分支")
    status: str = Field(description="部署状态")
    started_at: datetime = Field(description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration: Optional[int] = Field(default=None, description="耗时（秒）")
    deployed_by: str = Field(description="部署人")
    commit_hash: Optional[str] = Field(default=None, description="Git提交哈希")
    description: Optional[str] = Field(default=None, description="部署说明")
    logs: Optional[str] = Field(default=None, description="完整日志")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class RollbackRequest(BaseModel):
    """回滚请求"""
    deploy_id: int = Field(description="要回滚到的部署ID")
    description: Optional[str] = Field(
        default=None,
        description="回滚说明"
    )


class DeployConfigCreate(BaseModel):
    """创建部署配置"""
    environment: str = Field(description="环境名称")
    host: str = Field(description="服务器IP地址")
    port: int = Field(default=22, description="SSH端口")
    username: str = Field(description="SSH用户名")
    password: Optional[str] = Field(default=None, description="SSH密码")
    deploy_path: str = Field(description="部署目录路径")
    backup_path: Optional[str] = Field(default=None, description="备份目录路径")
    backend_port: int = Field(default=8000, description="后端服务端口")
    frontend_port: Optional[int] = Field(default=None, description="前端服务端口")
    description: Optional[str] = Field(default=None, description="配置说明")


class DeployConfigUpdate(BaseModel):
    """更新部署配置"""
    host: Optional[str] = Field(default=None, description="服务器IP地址")
    port: Optional[int] = Field(default=None, description="SSH端口")
    username: Optional[str] = Field(default=None, description="SSH用户名")
    password: Optional[str] = Field(default=None, description="SSH密码")
    deploy_path: Optional[str] = Field(default=None, description="部署目录路径")
    backup_path: Optional[str] = Field(default=None, description="备份目录路径")
    backend_port: Optional[int] = Field(default=None, description="后端服务端口")
    frontend_port: Optional[int] = Field(default=None, description="前端服务端口")
    description: Optional[str] = Field(default=None, description="配置说明")


class DeployConfigResponse(BaseModel):
    """部署配置响应"""
    id: int = Field(description="配置ID")
    environment: str = Field(description="环境名称")
    host: str = Field(description="服务器IP地址")
    port: int = Field(description="SSH端口")
    username: str = Field(description="SSH用户名")
    deploy_path: str = Field(description="部署目录路径")
    backup_path: Optional[str] = Field(default=None, description="备份目录路径")
    backend_port: int = Field(description="后端服务端口")
    frontend_port: Optional[int] = Field(default=None, description="前端服务端口")
    description: Optional[str] = Field(default=None, description="配置说明")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

