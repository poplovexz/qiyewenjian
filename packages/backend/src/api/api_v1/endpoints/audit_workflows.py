"""
审核工作流 API 端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import check_permission
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.shenhe_guanli.audit_workflow_service import AuditWorkflowService
from schemas.shenhe_guanli.audit_workflow_schemas import (
    AuditWorkflowCreate,
    AuditWorkflowUpdate,
    AuditWorkflowResponse,
    AuditWorkflowListParams
)
from typing import Dict, Any

router = APIRouter()

@router.get("/pending/my", response_model=List[dict])
@check_permission("audit:read")
async def get_my_pending_audits(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """获取我的待审核任务"""
    try:
        # 模拟数据，实际应该从数据库查询
        mock_data = [
            {
                "id": "1",
                "title": "合同金额修改审核",
                "type": "contract_audit",
                "status": "pending",
                "created_at": "2024-01-15T10:30:00",
                "priority": "high",
                "description": "客户要求将合同金额从10000元调整为8000元",
                "applicant": "张三",
                "department": "销售部"
            },
            {
                "id": "2", 
                "title": "报价单审核",
                "type": "quote_audit",
                "status": "pending",
                "created_at": "2024-01-15T09:15:00",
                "priority": "medium",
                "description": "新客户报价单需要审核确认",
                "applicant": "李四",
                "department": "商务部"
            },
            {
                "id": "3",
                "title": "特殊折扣申请",
                "type": "discount_audit", 
                "status": "pending",
                "created_at": "2024-01-14T16:45:00",
                "priority": "low",
                "description": "客户申请15%特殊折扣",
                "applicant": "王五",
                "department": "销售部"
            }
        ]
        
        # 分页处理
        start = (page - 1) * size
        end = start + size
        paginated_data = mock_data[start:end]
        
        return paginated_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待审核任务失败: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
@check_permission("audit_config")
async def get_workflows(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """获取审核工作流列表"""
    try:
        params = AuditWorkflowListParams(
            page=page,
            size=size,
            status=status,
            audit_type=audit_type,
            search=search
        )

        service = AuditWorkflowService(db)
        return service.get_workflow_list(params)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流列表失败: {str(e)}")

@router.post("/", response_model=AuditWorkflowResponse)
@check_permission("audit_config")
async def create_workflow(
    workflow_data: AuditWorkflowCreate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建审核工作流"""
    try:
        service = AuditWorkflowService(db)
        return service.create_workflow_template(workflow_data, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建工作流失败: {str(e)}")

@router.put("/{workflow_id}", response_model=AuditWorkflowResponse)
@check_permission("audit_config")
async def update_workflow(
    workflow_id: str,
    workflow_data: AuditWorkflowUpdate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新审核工作流"""
    try:
        service = AuditWorkflowService(db)
        return service.update_workflow_template(workflow_id, workflow_data, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新工作流失败: {str(e)}")

@router.delete("/{workflow_id}")
@check_permission("audit_config")
async def delete_workflow(
    workflow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除审核工作流"""
    try:
        service = AuditWorkflowService(db)
        success = service.delete_workflow_template(workflow_id)
        return {"success": success, "message": f"工作流 {workflow_id} 已删除"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除工作流失败: {str(e)}")

@router.get("/{workflow_id}", response_model=AuditWorkflowResponse)
@check_permission("audit:read")
async def get_workflow(
    workflow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个审核工作流详情"""
    try:
        service = AuditWorkflowService(db)
        return service.get_workflow_by_id(workflow_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流详情失败: {str(e)}")
