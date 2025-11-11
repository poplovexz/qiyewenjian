"""
采购申请管理API端点（简化版）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.bangong_guanli.caigou_service import CaigouService
from schemas.bangong_guanli.caigou_schemas import (
    CaigouShenqingCreate,
    CaigouShenqingUpdate,
    CaigouShenqingResponse,
    CaigouShenqingListParams
)

router = APIRouter()


@router.post("/", response_model=CaigouShenqingResponse, summary="创建采购申请")
async def create_caigou_shenqing(
    shenqing_data: CaigouShenqingCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建采购申请"""
    service = CaigouService(db)
    return service.create_caigou_shenqing(shenqing_data, current_user.id)


@router.get("/", response_model=dict, summary="获取采购申请列表")
async def get_caigou_shenqing_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    shenhe_zhuangtai: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取采购申请列表"""
    params = CaigouShenqingListParams(page=page, size=size, shenhe_zhuangtai=shenhe_zhuangtai)
    service = CaigouService(db)
    items, total = service.get_caigou_shenqing_list(params)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{shenqing_id}", response_model=CaigouShenqingResponse, summary="获取采购申请详情")
async def get_caigou_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取采购申请详情"""
    service = CaigouService(db)
    return service.get_caigou_shenqing_by_id(shenqing_id)


@router.put("/{shenqing_id}", response_model=CaigouShenqingResponse, summary="更新采购申请")
async def update_caigou_shenqing(
    shenqing_id: str,
    update_data: CaigouShenqingUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新采购申请"""
    service = CaigouService(db)
    return service.update_caigou_shenqing(shenqing_id, update_data, current_user.id)


@router.delete("/{shenqing_id}", summary="删除采购申请")
async def delete_caigou_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除采购申请"""
    service = CaigouService(db)
    return service.delete_caigou_shenqing(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/submit", summary="提交审批")
async def submit_caigou_for_approval(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """提交采购申请进行审批"""
    service = CaigouService(db)
    return service.submit_for_approval(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/approve", summary="审批通过")
async def approve_caigou_shenqing(
    shenqing_id: str,
    shenhe_yijian: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批通过采购申请"""
    service = CaigouService(db)
    return service.approve_application(shenqing_id, current_user.id, shenhe_yijian)


@router.post("/{shenqing_id}/reject", summary="审批拒绝")
async def reject_caigou_shenqing(
    shenqing_id: str,
    shenhe_yijian: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批拒绝采购申请"""
    service = CaigouService(db)
    return service.reject_application(shenqing_id, current_user.id, shenhe_yijian)
