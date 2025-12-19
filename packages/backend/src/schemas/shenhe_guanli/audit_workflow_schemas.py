"""
审核工作流模板数据模式
用于前端工作流配置页面
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class WorkflowStepBase(BaseModel):
    """工作流步骤基础模型"""
    step_name: str = Field(..., description="步骤名称")
    step_order: int = Field(..., ge=1, description="步骤顺序")
    approver_user_id: Optional[str] = Field(None, description="审批人用户ID")
    approver_role: Optional[str] = Field(None, description="审批人角色（兼容旧数据）")
    description: Optional[str] = Field(None, description="步骤描述")
    expected_time: int = Field(default=24, description="预期处理时间(小时)")
    is_required: bool = Field(default=True, description="是否必需")

    @model_validator(mode='after')
    def check_approver(self):
        """验证至少有一个审核人字段"""
        if not self.approver_user_id and not self.approver_role:
            raise ValueError('必须指定审核人（approver_user_id 或 approver_role）')
        return self

class AuditWorkflowBase(BaseModel):
    """审核工作流基础模型"""
    workflow_name: str = Field(..., min_length=1, max_length=200, description="工作流名称")
    audit_type: str = Field(..., description="审核类型")
    description: Optional[str] = Field(None, description="工作流描述")
    status: str = Field(default="active", description="状态")
    steps: List[WorkflowStepBase] = Field(..., description="工作流步骤")

class AuditWorkflowCreate(AuditWorkflowBase):
    """创建审核工作流模型"""
    pass

class AuditWorkflowUpdate(BaseModel):
    """更新审核工作流模型"""
    workflow_name: Optional[str] = Field(None, min_length=1, max_length=200, description="工作流名称")
    audit_type: Optional[str] = Field(None, description="审核类型")
    description: Optional[str] = Field(None, description="工作流描述")
    status: Optional[str] = Field(None, description="状态")
    steps: Optional[List[WorkflowStepBase]] = Field(None, description="工作流步骤")

class AuditWorkflowResponse(BaseModel):
    """审核工作流响应模型"""
    id: str
    workflow_name: str  # 工作流名称
    audit_type: str  # 审核类型
    description: Optional[str]
    status: str
    steps: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AuditWorkflowListParams(BaseModel):
    """审核工作流列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    status: Optional[str] = Field(None, description="状态筛选")
    audit_type: Optional[str] = Field(None, description="审核类型筛选")
    search: Optional[str] = Field(None, description="搜索关键词")
