"""
服务工单管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from services.fuwu_guanli import FuwuGongdanService
from schemas.fuwu_guanli.fuwu_gongdan_schemas import (
    FuwuGongdanCreate,
    FuwuGongdanUpdate,
    FuwuGongdanResponse,
    FuwuGongdanDetailResponse,
    FuwuGongdanListResponse,
    FuwuGongdanListParams,
    FuwuGongdanStatistics,
    FuwuGongdanRizhiCreate,
    FuwuGongdanRizhiResponse,
    FuwuGongdanXiangmuResponse
)

router = APIRouter()


@router.post("/", response_model=FuwuGongdanDetailResponse, summary="创建服务工单")
def create_gongdan(
    gongdan_data: FuwuGongdanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建服务工单"""
    service = FuwuGongdanService(db)
    return service.create_gongdan(gongdan_data, current_user.id)


@router.post("/from-contract/{hetong_id}", response_model=FuwuGongdanDetailResponse, summary="基于合同创建服务工单")
def create_gongdan_from_hetong(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """基于合同创建服务工单"""
    service = FuwuGongdanService(db)
    return service.create_gongdan_from_hetong(hetong_id, current_user.id)


@router.get("/", response_model=FuwuGongdanListResponse, summary="获取服务工单列表")
def get_gongdan_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    gongdan_bianhao: Optional[str] = Query(None, description="工单编号"),
    gongdan_biaoti: Optional[str] = Query(None, description="工单标题"),
    fuwu_leixing: Optional[str] = Query(None, description="服务类型"),
    gongdan_zhuangtai: Optional[str] = Query(None, description="工单状态"),
    youxian_ji: Optional[str] = Query(None, description="优先级"),
    zhixing_ren_id: Optional[str] = Query(None, description="执行人ID"),
    kehu_id: Optional[str] = Query(None, description="客户ID"),
    hetong_id: Optional[str] = Query(None, description="合同ID"),
    is_overdue: Optional[bool] = Query(None, description="是否逾期"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取服务工单列表"""
    params = FuwuGongdanListParams(
        page=page,
        size=size,
        gongdan_bianhao=gongdan_bianhao,
        gongdan_biaoti=gongdan_biaoti,
        fuwu_leixing=fuwu_leixing,
        gongdan_zhuangtai=gongdan_zhuangtai,
        youxian_ji=youxian_ji,
        zhixing_ren_id=zhixing_ren_id,
        kehu_id=kehu_id,
        hetong_id=hetong_id,
        is_overdue=is_overdue
    )
    
    service = FuwuGongdanService(db)
    return service.get_gongdan_list(params)


@router.get("/{gongdan_id}", response_model=FuwuGongdanDetailResponse, summary="获取服务工单详情")
def get_gongdan_detail(
    gongdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取服务工单详情"""
    service = FuwuGongdanService(db)
    return service.get_gongdan_detail(gongdan_id)


@router.put("/{gongdan_id}", response_model=FuwuGongdanDetailResponse, summary="更新服务工单")
def update_gongdan(
    gongdan_id: str,
    gongdan_data: FuwuGongdanUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新服务工单"""
    service = FuwuGongdanService(db)
    return service.update_gongdan(gongdan_id, gongdan_data, current_user.id)


@router.post("/{gongdan_id}/assign", response_model=FuwuGongdanDetailResponse, summary="分配工单")
def assign_gongdan(
    gongdan_id: str,
    zhixing_ren_id: str,
    fenpei_beizhu: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """分配工单"""
    service = FuwuGongdanService(db)
    return service.assign_gongdan(gongdan_id, zhixing_ren_id, fenpei_beizhu, current_user.id)


@router.post("/{gongdan_id}/start", response_model=FuwuGongdanDetailResponse, summary="开始工单")
def start_gongdan(
    gongdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """开始工单"""
    service = FuwuGongdanService(db)
    return service.start_gongdan(gongdan_id, current_user.id)


@router.post("/{gongdan_id}/complete", response_model=FuwuGongdanDetailResponse, summary="完成工单")
def complete_gongdan(
    gongdan_id: str,
    wancheng_qingkuang: str,
    jiaofei_wenjian: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """完成工单"""
    service = FuwuGongdanService(db)
    return service.complete_gongdan(gongdan_id, wancheng_qingkuang, jiaofei_wenjian, current_user.id)


@router.post("/{gongdan_id}/cancel", response_model=FuwuGongdanDetailResponse, summary="取消工单")
def cancel_gongdan(
    gongdan_id: str,
    cancel_reason: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """取消工单"""
    service = FuwuGongdanService(db)
    return service.cancel_gongdan(gongdan_id, cancel_reason, current_user.id)


@router.post("/{gongdan_id}/comments", response_model=FuwuGongdanRizhiResponse, summary="添加工单评论")
def add_gongdan_comment(
    gongdan_id: str,
    comment_data: FuwuGongdanRizhiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """添加工单评论"""
    service = FuwuGongdanService(db)
    return service.add_gongdan_comment(
        gongdan_id, 
        comment_data.caozuo_neirong, 
        current_user.id,
        comment_data.fujian_lujing
    )


@router.get("/statistics/overview", response_model=FuwuGongdanStatistics, summary="获取工单统计信息")
def get_gongdan_statistics(
    kehu_id: Optional[str] = Query(None, description="客户ID"),
    zhixing_ren_id: Optional[str] = Query(None, description="执行人ID"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取工单统计信息"""
    service = FuwuGongdanService(db)
    return service.get_gongdan_statistics(kehu_id, zhixing_ren_id)


@router.post("/{gongdan_id}/items/{item_id}/assign", response_model=FuwuGongdanXiangmuResponse, summary="分配工单任务项")
def assign_task_item(
    gongdan_id: str,
    item_id: str,
    zhixing_ren_id: str = Query(..., description="执行人ID"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """分配工单任务项给执行人

    Args:
        gongdan_id: 工单ID
        item_id: 任务项ID
        zhixing_ren_id: 执行人ID

    Returns:
        更新后的任务项信息
    """
    service = FuwuGongdanService(db)
    return service.assign_task_item(
        gongdan_id=gongdan_id,
        item_id=item_id,
        zhixing_ren_id=zhixing_ren_id,
        operator_id=current_user.id
    )
