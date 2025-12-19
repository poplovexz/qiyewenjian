"""
工作交接单管理API端点（简化版）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.bangong_guanli.gongzuo_jiaojie_service import GongzuoJiaojieService
from schemas.bangong_guanli.gongzuo_jiaojie_schemas import (
    GongzuoJiaojieCreate,
    GongzuoJiaojieUpdate,
    GongzuoJiaojieResponse,
    GongzuoJiaojieListParams
)

router = APIRouter()

@router.post("/", response_model=GongzuoJiaojieResponse, summary="创建工作交接单")
async def create_gongzuo_jiaojie(
    jiaojie_data: GongzuoJiaojieCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建工作交接单"""
    service = GongzuoJiaojieService(db)
    return service.create_gongzuo_jiaojie(jiaojie_data, current_user.id)

@router.get("/", response_model=dict, summary="获取工作交接单列表")
async def get_gongzuo_jiaojie_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    shenhe_zhuangtai: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取工作交接单列表"""
    params = GongzuoJiaojieListParams(page=page, size=size, shenhe_zhuangtai=shenhe_zhuangtai)
    service = GongzuoJiaojieService(db)
    items, total = service.get_gongzuo_jiaojie_list(params)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/{jiaojie_id}", response_model=GongzuoJiaojieResponse, summary="获取工作交接单详情")
async def get_gongzuo_jiaojie(
    jiaojie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取工作交接单详情"""
    service = GongzuoJiaojieService(db)
    return service.get_gongzuo_jiaojie_by_id(jiaojie_id)

@router.put("/{jiaojie_id}", response_model=GongzuoJiaojieResponse, summary="更新工作交接单")
async def update_gongzuo_jiaojie(
    jiaojie_id: str,
    update_data: GongzuoJiaojieUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新工作交接单"""
    service = GongzuoJiaojieService(db)
    return service.update_gongzuo_jiaojie(jiaojie_id, update_data, current_user.id)

@router.delete("/{jiaojie_id}", summary="删除工作交接单")
async def delete_gongzuo_jiaojie(
    jiaojie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除工作交接单"""
    service = GongzuoJiaojieService(db)
    return service.delete_gongzuo_jiaojie(jiaojie_id, current_user.id)

@router.post("/{jiaojie_id}/submit", summary="提交审批")
async def submit_gongzuo_jiaojie_for_approval(
    jiaojie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """提交工作交接单进行审批"""
    service = GongzuoJiaojieService(db)
    return service.submit_for_approval(jiaojie_id, current_user.id)

@router.post("/{jiaojie_id}/approve", summary="审批通过")
async def approve_gongzuo_jiaojie(
    jiaojie_id: str,
    shenhe_yijian: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批通过工作交接单"""
    service = GongzuoJiaojieService(db)
    return service.approve_application(jiaojie_id, current_user.id, shenhe_yijian)

@router.post("/{jiaojie_id}/reject", summary="审批拒绝")
async def reject_gongzuo_jiaojie(
    jiaojie_id: str,
    shenhe_yijian: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批拒绝工作交接单"""
    service = GongzuoJiaojieService(db)
    return service.reject_application(jiaojie_id, current_user.id, shenhe_yijian)
