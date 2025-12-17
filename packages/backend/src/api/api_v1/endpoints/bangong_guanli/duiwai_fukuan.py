"""
对外付款申请管理API端点（简化版）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.bangong_guanli.duiwai_fukuan_service import DuiwaiFukuanService
from schemas.bangong_guanli.duiwai_fukuan_schemas import (
    DuiwaiFukuanShenqingCreate,
    DuiwaiFukuanShenqingUpdate,
    DuiwaiFukuanShenqingResponse,
    DuiwaiFukuanShenqingListParams
)

router = APIRouter()


@router.post("/", response_model=DuiwaiFukuanShenqingResponse, summary="创建对外付款申请")
async def create_duiwai_fukuan_shenqing(
    shenqing_data: DuiwaiFukuanShenqingCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建对外付款申请"""
    service = DuiwaiFukuanService(db)
    return service.create_duiwai_fukuan_shenqing(shenqing_data, current_user.id)


@router.get("/", response_model=dict, summary="获取对外付款申请列表")
async def get_duiwai_fukuan_shenqing_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    shenhe_zhuangtai: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取对外付款申请列表"""
    params = DuiwaiFukuanShenqingListParams(page=page, size=size, shenhe_zhuangtai=shenhe_zhuangtai)
    service = DuiwaiFukuanService(db)
    items, total = service.get_duiwai_fukuan_shenqing_list(params)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{shenqing_id}", response_model=DuiwaiFukuanShenqingResponse, summary="获取对外付款申请详情")
async def get_duiwai_fukuan_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取对外付款申请详情"""
    service = DuiwaiFukuanService(db)
    return service.get_duiwai_fukuan_shenqing_by_id(shenqing_id)


@router.put("/{shenqing_id}", response_model=DuiwaiFukuanShenqingResponse, summary="更新对外付款申请")
async def update_duiwai_fukuan_shenqing(
    shenqing_id: str,
    update_data: DuiwaiFukuanShenqingUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新对外付款申请"""
    service = DuiwaiFukuanService(db)
    return service.update_duiwai_fukuan_shenqing(shenqing_id, update_data, current_user.id)


@router.delete("/{shenqing_id}", summary="删除对外付款申请")
async def delete_duiwai_fukuan_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除对外付款申请"""
    service = DuiwaiFukuanService(db)
    return service.delete_duiwai_fukuan_shenqing(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/submit", summary="提交审批")
async def submit_duiwai_fukuan_for_approval(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """提交对外付款申请进行审批"""
    service = DuiwaiFukuanService(db)
    return service.submit_for_approval(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/approve", summary="审批通过")
async def approve_duiwai_fukuan_shenqing(
    shenqing_id: str,
    shenhe_yijian: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批通过对外付款申请"""
    service = DuiwaiFukuanService(db)
    return service.approve_application(shenqing_id, current_user.id, shenhe_yijian)


@router.post("/{shenqing_id}/reject", summary="审批拒绝")
async def reject_duiwai_fukuan_shenqing(
    shenqing_id: str,
    shenhe_yijian: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批拒绝对外付款申请"""
    service = DuiwaiFukuanService(db)
    return service.reject_application(shenqing_id, current_user.id, shenhe_yijian)
