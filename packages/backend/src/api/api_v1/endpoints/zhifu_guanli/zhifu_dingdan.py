"""
支付订单管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from models.zhifu_guanli import ZhifuDingdan
from services.zhifu_guanli.zhifu_dingdan_service import ZhifuDingdanService
from schemas.zhifu_guanli.zhifu_dingdan_schemas import (
    ZhifuDingdanCreate,
    ZhifuDingdanUpdate,
    ZhifuDingdanResponse,
    ZhifuDingdanListResponse,
    ZhifuDingdanListParams,
    ZhifuDingdanStatistics
)

router = APIRouter()


@router.post("/", response_model=ZhifuDingdanResponse, summary="创建支付订单")
async def create_zhifu_dingdan(
    dingdan_data: ZhifuDingdanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:create"))
):
    """
    创建新的支付订单
    
    - **hetong_id**: 合同ID（必填）
    - **kehu_id**: 客户ID（必填）
    - **dingdan_mingcheng**: 订单名称（必填）
    - **dingdan_jine**: 订单金额（必填）
    - **yingfu_jine**: 应付金额（必填）
    - **zhifu_leixing**: 支付类型（必填）
    """
    service = ZhifuDingdanService(db)
    return service.create_zhifu_dingdan(dingdan_data, current_user.id)


@router.get("/", response_model=ZhifuDingdanListResponse, summary="获取支付订单列表")
async def get_zhifu_dingdan_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    hetong_id: str = Query(None, description="合同ID"),
    kehu_id: str = Query(None, description="客户ID"),
    zhifu_leixing: str = Query(None, description="支付类型"),
    zhifu_zhuangtai: str = Query(None, description="支付状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:read"))
):
    """
    获取支付订单列表
    
    支持分页、搜索和筛选
    """
    params = ZhifuDingdanListParams(
        page=page,
        size=size,
        search=search,
        hetong_id=hetong_id,
        kehu_id=kehu_id,
        zhifu_leixing=zhifu_leixing,
        zhifu_zhuangtai=zhifu_zhuangtai
    )
    service = ZhifuDingdanService(db)
    return service.get_zhifu_dingdan_list(params)


@router.get("/statistics", response_model=ZhifuDingdanStatistics, summary="获取支付订单统计")
async def get_zhifu_dingdan_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:read"))
):
    """
    获取支付订单统计信息
    
    包括总订单数、各状态订单数、金额统计等
    """
    service = ZhifuDingdanService(db)
    return service.get_zhifu_dingdan_statistics()


@router.get("/{dingdan_id}", response_model=ZhifuDingdanResponse, summary="获取支付订单详情")
async def get_zhifu_dingdan_detail(
    dingdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:read"))
):
    """
    根据ID获取支付订单详情
    """
    service = ZhifuDingdanService(db)
    return service.get_zhifu_dingdan_by_id(dingdan_id)


@router.put("/{dingdan_id}", response_model=ZhifuDingdanResponse, summary="更新支付订单")
async def update_zhifu_dingdan(
    dingdan_id: str,
    dingdan_data: ZhifuDingdanUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:update"))
):
    """
    更新支付订单信息
    
    可以更新订单状态、支付信息等
    """
    service = ZhifuDingdanService(db)
    return service.update_zhifu_dingdan(dingdan_id, dingdan_data, current_user.id)


@router.delete("/{dingdan_id}", summary="删除支付订单")
async def delete_zhifu_dingdan(
    dingdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:delete"))
):
    """
    删除支付订单（软删除）
    """
    service = ZhifuDingdanService(db)
    zhifu_dingdan = service.get_zhifu_dingdan_by_id(dingdan_id)
    
    # 执行软删除
    db.query(ZhifuDingdan).filter(ZhifuDingdan.id == dingdan_id).update({
        "is_deleted": "Y",
        "updated_by": current_user.id,
        "updated_at": datetime.now()
    })
    db.commit()
    
    return {"message": "支付订单删除成功"}


@router.post("/{dingdan_id}/cancel", response_model=ZhifuDingdanResponse, summary="取消支付订单")
async def cancel_zhifu_dingdan(
    dingdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:update"))
):
    """
    取消支付订单
    """
    service = ZhifuDingdanService(db)
    
    # 更新订单状态为已取消
    update_data = ZhifuDingdanUpdate(zhifu_zhuangtai="cancelled")
    return service.update_zhifu_dingdan(dingdan_id, update_data, current_user.id)
