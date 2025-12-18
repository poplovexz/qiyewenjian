"""
任务项管理 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from services.fuwu_guanli.fuwu_gongdan_service import FuwuGongdanService
from schemas.fuwu_guanli.fuwu_gongdan_schemas import (
    TaskItemListResponse,
    TaskItemStatistics,
    FuwuGongdanXiangmuResponse
)

router = APIRouter()


@router.get("/my-tasks", response_model=TaskItemListResponse, summary="获取我的任务项列表")
def get_my_task_items(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    xiangmu_zhuangtai: Optional[str] = Query(None, description="任务项状态筛选"),
    gongdan_zhuangtai: Optional[str] = Query(None, description="工单状态筛选"),
    fuwu_leixing: Optional[str] = Query(None, description="服务类型筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户的任务项列表
    
    - **page**: 页码
    - **size**: 每页数量
    - **xiangmu_zhuangtai**: 任务项状态筛选（pending/in_progress/completed/skipped）
    - **gongdan_zhuangtai**: 工单状态筛选
    - **fuwu_leixing**: 服务类型筛选
    """
    service = FuwuGongdanService(db)
    return service.get_my_task_items(
        zhixing_ren_id=current_user.id,
        page=page,
        size=size,
        xiangmu_zhuangtai=xiangmu_zhuangtai,
        gongdan_zhuangtai=gongdan_zhuangtai,
        fuwu_leixing=fuwu_leixing
    )


@router.post("/{item_id}/start", response_model=FuwuGongdanXiangmuResponse, summary="开始任务项")
def start_task_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    开始执行任务项
    
    - **item_id**: 任务项ID
    
    将任务项状态从 pending 改为 in_progress，并记录开始时间
    """
    service = FuwuGongdanService(db)
    return service.start_task_item(
        item_id=item_id,
        zhixing_ren_id=current_user.id
    )


@router.post("/{item_id}/complete", response_model=FuwuGongdanXiangmuResponse, summary="完成任务项")
def complete_task_item(
    item_id: str,
    shiji_gongshi: Decimal = Query(..., ge=0, description="实际工时"),
    beizhu: Optional[str] = Query(None, description="备注"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    完成任务项
    
    - **item_id**: 任务项ID
    - **shiji_gongshi**: 实际工时（小时）
    - **beizhu**: 备注说明
    
    将任务项状态改为 completed，记录实际工时和结束时间
    """
    service = FuwuGongdanService(db)
    return service.complete_task_item(
        item_id=item_id,
        zhixing_ren_id=current_user.id,
        shiji_gongshi=shiji_gongshi,
        beizhu=beizhu
    )


@router.post("/{item_id}/pause", response_model=FuwuGongdanXiangmuResponse, summary="暂停任务项")
def pause_task_item(
    item_id: str,
    beizhu: Optional[str] = Query(None, description="暂停原因"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    暂停任务项
    
    - **item_id**: 任务项ID
    - **beizhu**: 暂停原因
    
    将任务项状态从 in_progress 改回 pending
    """
    service = FuwuGongdanService(db)
    return service.pause_task_item(
        item_id=item_id,
        zhixing_ren_id=current_user.id,
        beizhu=beizhu
    )


@router.get("/statistics", response_model=TaskItemStatistics, summary="获取任务项统计")
def get_task_item_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户的任务项统计信息
    
    包括：
    - 总任务数
    - 各状态任务数量
    - 总计划工时
    - 总实际工时
    - 平均完成率
    """
    service = FuwuGongdanService(db)
    return service.get_task_item_statistics(zhixing_ren_id=current_user.id)

