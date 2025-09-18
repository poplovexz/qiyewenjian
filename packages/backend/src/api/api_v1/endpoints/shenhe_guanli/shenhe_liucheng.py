"""
审核流程管理API
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.yonghu_guanli import Yonghu
from src.services.shenhe_guanli import ShenheLiuchengService
from src.schemas.shenhe_guanli import (
    ShenheLiuchengResponse,
    ShenheLiuchengListParams,
    ShenheActionRequest
)

router = APIRouter()


@router.get("/", summary="获取审核流程列表")
async def get_shenhe_liucheng_list(
    page: int = 1,
    size: int = 20,
    search: str = None,
    shenhe_leixing: str = None,
    shenhe_zhuangtai: str = None,
    shenqing_ren_id: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取审核流程列表"""
    params = ShenheLiuchengListParams(
        page=page,
        size=size,
        search=search,
        shenhe_leixing=shenhe_leixing,
        shenhe_zhuangtai=shenhe_zhuangtai,
        shenqing_ren_id=shenqing_ren_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = ShenheLiuchengService(db)
    return service.get_shenhe_liucheng_list(params)


@router.get("/{liucheng_id}", response_model=ShenheLiuchengResponse, summary="获取审核流程详情")
async def get_shenhe_liucheng_by_id(
    liucheng_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取审核流程详情"""
    service = ShenheLiuchengService(db)
    return service.get_shenhe_liucheng_by_id(liucheng_id)


@router.get("/pending/my", summary="获取我的待审核任务")
async def get_my_pending_audits(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """获取当前用户的待审核任务"""
    service = ShenheLiuchengService(db)
    return service.get_pending_audits_by_user(current_user.id)


@router.post("/{liucheng_id}/steps/{step_id}/action", summary="处理审核操作")
async def process_audit_action(
    liucheng_id: str,
    step_id: str,
    action_data: ShenheActionRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """处理审核操作"""
    service = ShenheLiuchengService(db)
    is_completed = service.process_audit_action(liucheng_id, step_id, action_data, current_user.id)
    
    return {
        "success": True,
        "message": "审核操作处理成功",
        "is_completed": is_completed
    }


@router.get("/history/{audit_type}/{related_id}", summary="获取审核历史")
async def get_audit_history(
    audit_type: str,
    related_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> List[ShenheLiuchengResponse]:
    """根据关联ID获取审核历史"""
    service = ShenheLiuchengService(db)
    return service.get_audit_history_by_related_id(audit_type, related_id)


@router.post("/{liucheng_id}/cancel", summary="取消审核流程")
async def cancel_audit_workflow(
    liucheng_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """取消审核流程"""
    service = ShenheLiuchengService(db)
    success = service.cancel_audit_workflow(liucheng_id, current_user.id, reason)
    
    return {
        "success": success,
        "message": "审核流程取消成功"
    }


@router.get("/statistics/overview", summary="获取审核统计概览")
async def get_audit_statistics_overview(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取审核统计概览"""
    service = ShenheLiuchengService(db)
    
    # 获取各种状态的审核流程数量
    from src.models.shenhe_guanli import ShenheLiucheng
    
    total_count = db.query(ShenheLiucheng).filter(ShenheLiucheng.is_deleted == "N").count()
    pending_count = db.query(ShenheLiucheng).filter(
        ShenheLiucheng.shenhe_zhuangtai == "shenhzhong",
        ShenheLiucheng.is_deleted == "N"
    ).count()
    approved_count = db.query(ShenheLiucheng).filter(
        ShenheLiucheng.shenhe_zhuangtai == "tongguo",
        ShenheLiucheng.is_deleted == "N"
    ).count()
    rejected_count = db.query(ShenheLiucheng).filter(
        ShenheLiucheng.shenhe_zhuangtai == "jujue",
        ShenheLiucheng.is_deleted == "N"
    ).count()
    
    return {
        "total_count": total_count,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "approval_rate": round(approved_count / total_count * 100, 2) if total_count > 0 else 0
    }
