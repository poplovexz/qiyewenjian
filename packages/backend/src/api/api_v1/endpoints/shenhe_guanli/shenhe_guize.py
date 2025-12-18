"""
审核规则配置API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from core.security.audit_permissions import require_audit_permission
from models.yonghu_guanli import Yonghu
from services.shenhe_guanli import ShenheGuizeService
from schemas.shenhe_guanli import (
    ShenheGuizeCreate,
    ShenheGuizeUpdate,
    ShenheGuizeResponse,
    ShenheGuizeListParams
)

router = APIRouter()


@router.post("/", response_model=ShenheGuizeResponse, summary="创建审核规则")
@require_audit_permission("audit_rule:create")
async def create_shenhe_guize(
    guize_data: ShenheGuizeCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    创建新的审核规则
    
    - **guize_mingcheng**: 规则名称（必填）
    - **guize_leixing**: 规则类型（必填）
    - **chufa_tiaojian**: 触发条件配置（JSON格式）
    - **shenhe_liucheng_peizhi**: 审核流程配置（JSON格式）
    """
    service = ShenheGuizeService(db)
    return service.create_shenhe_guize(guize_data, current_user.id)


@router.get("/", summary="获取审核规则列表")
@require_audit_permission("audit_rule:read")
async def get_shenhe_guize_list(
    page: int = 1,
    size: int = 20,
    search: str = None,
    guize_leixing: str = None,
    shi_qiyong: str = None,
    sort_by: str = "paixu",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取审核规则列表"""
    params = ShenheGuizeListParams(
        page=page,
        size=size,
        search=search,
        guize_leixing=guize_leixing,
        shi_qiyong=shi_qiyong,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = ShenheGuizeService(db)
    return service.get_shenhe_guize_list(params)


@router.get("/{guize_id}", response_model=ShenheGuizeResponse, summary="获取审核规则详情")
@require_audit_permission("audit_rule:read", "guize_id")
async def get_shenhe_guize_by_id(
    guize_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取审核规则详情"""
    service = ShenheGuizeService(db)
    return service.get_shenhe_guize_by_id(guize_id)


@router.put("/{guize_id}", response_model=ShenheGuizeResponse, summary="更新审核规则")
@require_audit_permission("audit_rule:update", "guize_id")
async def update_shenhe_guize(
    guize_id: str,
    guize_data: ShenheGuizeUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新审核规则"""
    service = ShenheGuizeService(db)
    return service.update_shenhe_guize(guize_id, guize_data, current_user.id)


@router.delete("/{guize_id}", summary="删除审核规则")
async def delete_shenhe_guize(
    guize_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除审核规则"""
    service = ShenheGuizeService(db)
    success = service.delete_shenhe_guize(guize_id)
    return {"success": success, "message": "审核规则删除成功"}


@router.get("/type/{guize_leixing}", summary="根据类型获取启用的审核规则")
async def get_active_rules_by_type(
    guize_leixing: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据类型获取启用的审核规则"""
    service = ShenheGuizeService(db)
    return service.get_active_rules_by_type(guize_leixing)


@router.get("/workflows/options", summary="获取审核流程选项")
async def get_workflow_options(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取审核流程选项，用于规则配置的下拉选择"""
    try:
        # 从audit_workflows API获取真实数据
        from ..audit_workflows import get_workflows

        # 获取工作流列表
        workflows_response = await get_workflows(
            current_user=current_user,
            db=db,
            page=1,
            size=100,  # 获取所有活跃的工作流
            status="active"
        )

        # 转换为下拉选项格式
        workflow_options = []
        if workflows_response and "items" in workflows_response:
            for workflow in workflows_response["items"]:
                workflow_options.append({
                    "value": workflow.get("id", ""),
                    "label": workflow.get("name", "")
                })

        # 如果没有真实数据，返回默认选项
        if not workflow_options:
            workflow_options = [
                {"value": "contract_audit", "label": "合同审核流程"},
                {"value": "quote_audit", "label": "报价审核流程"},
                {"value": "amount_change_audit", "label": "金额变更审核流程"},
                {"value": "discount_audit", "label": "折扣审核流程"}
            ]

        return {"options": workflow_options}  # 修复：返回前端期望的格式
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流选项失败: {str(e)}")
