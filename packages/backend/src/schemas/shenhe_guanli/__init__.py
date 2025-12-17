"""
审核管理模块数据模式
"""
from .shenhe_guize_schemas import (
    ShenheGuizeBase,
    ShenheGuizeCreate,
    ShenheGuizeUpdate,
    ShenheGuizeResponse,
    ShenheGuizeListParams
)

from .shenhe_liucheng_schemas import (
    ShenheLiuchengBase,
    ShenheLiuchengCreate,
    ShenheLiuchengUpdate,
    ShenheLiuchengResponse,
    ShenheLiuchengListParams
)

from .shenhe_jilu_schemas import (
    ShenheJiluBase,
    ShenheJiluCreate,
    ShenheJiluUpdate,
    ShenheJiluResponse,
    ShenheJiluListParams,
    ShenheActionRequest
)

from .audit_workflow_schemas import (
    WorkflowStepBase,
    AuditWorkflowBase,
    AuditWorkflowCreate,
    AuditWorkflowUpdate,
    AuditWorkflowResponse,
    AuditWorkflowListParams
)

__all__ = [
    # 审核规则
    "ShenheGuizeBase",
    "ShenheGuizeCreate",
    "ShenheGuizeUpdate",
    "ShenheGuizeResponse",
    "ShenheGuizeListParams",

    # 审核流程
    "ShenheLiuchengBase",
    "ShenheLiuchengCreate",
    "ShenheLiuchengUpdate",
    "ShenheLiuchengResponse",
    "ShenheLiuchengListParams",

    # 审核记录
    "ShenheJiluBase",
    "ShenheJiluCreate",
    "ShenheJiluUpdate",
    "ShenheJiluResponse",
    "ShenheJiluListParams",
    "ShenheActionRequest",

    # 审核工作流模板
    "WorkflowStepBase",
    "AuditWorkflowBase",
    "AuditWorkflowCreate",
    "AuditWorkflowUpdate",
    "AuditWorkflowResponse",
    "AuditWorkflowListParams"
]
