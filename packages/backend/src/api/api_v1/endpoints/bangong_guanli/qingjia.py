"""
请假申请管理API端点（简化版）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.bangong_guanli.qingjia_service import QingjiaService
from schemas.bangong_guanli.qingjia_schemas import (
    QingjiaShenqingCreate,
    QingjiaShenqingUpdate,
    QingjiaShenqingResponse,
    QingjiaShenqingListParams
)

router = APIRouter()


@router.post("/", response_model=QingjiaShenqingResponse, summary="创建请假申请")
async def create_qingjia_shenqing(
    shenqing_data: QingjiaShenqingCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建请假申请"""
    service = QingjiaService(db)
    return service.create_qingjia_shenqing(shenqing_data, current_user.id)


@router.get("/", response_model=dict, summary="获取请假申请列表")
async def get_qingjia_shenqing_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    shenhe_zhuangtai: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取请假申请列表"""
    params = QingjiaShenqingListParams(page=page, size=size, shenhe_zhuangtai=shenhe_zhuangtai)
    service = QingjiaService(db)
    items, total = service.get_qingjia_shenqing_list(params)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{shenqing_id}", response_model=QingjiaShenqingResponse, summary="获取请假申请详情")
async def get_qingjia_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取请假申请详情"""
    service = QingjiaService(db)
    return service.get_qingjia_shenqing_by_id(shenqing_id)


@router.put("/{shenqing_id}", response_model=QingjiaShenqingResponse, summary="更新请假申请")
async def update_qingjia_shenqing(
    shenqing_id: str,
    update_data: QingjiaShenqingUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新请假申请"""
    service = QingjiaService(db)
    return service.update_qingjia_shenqing(shenqing_id, update_data, current_user.id)


@router.delete("/{shenqing_id}", summary="删除请假申请")
async def delete_qingjia_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除请假申请"""
    service = QingjiaService(db)
    return service.delete_qingjia_shenqing(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/submit", summary="提交审批")
async def submit_qingjia_for_approval(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """提交请假申请进行审批"""
    service = QingjiaService(db)
    return service.submit_for_approval(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/approve", summary="审批通过")
async def approve_qingjia_shenqing(
    shenqing_id: str,
    shenhe_yijian: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批通过请假申请"""
    service = QingjiaService(db)
    return service.approve_application(shenqing_id, current_user.id, shenhe_yijian)


@router.post("/{shenqing_id}/reject", summary="审批拒绝")
async def reject_qingjia_shenqing(
    shenqing_id: str,
    shenhe_yijian: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """审批拒绝请假申请"""
    service = QingjiaService(db)
    return service.reject_application(shenqing_id, current_user.id, shenhe_yijian)
