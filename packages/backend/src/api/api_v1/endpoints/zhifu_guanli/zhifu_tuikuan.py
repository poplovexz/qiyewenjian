"""
退款管理API端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.zhifu_guanli.zhifu_tuikuan_service import ZhifuTuikuanService
from schemas.zhifu_guanli.zhifu_tuikuan_schemas import (
    ZhifuTuikuanCreate,
    ZhifuTuikuanResponse,
    ZhifuTuikuanListResponse
)

router = APIRouter()


@router.post("/", response_model=ZhifuTuikuanResponse, summary="创建退款申请")
def create_refund(
    tuikuan_data: ZhifuTuikuanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("zhifu:tuikuan:create"))
):
    """
    创建退款申请
    
    权限要求：zhifu:tuikuan:create
    
    参数：
    - zhifu_dingdan_id: 支付订单ID
    - tuikuan_jine: 退款金额
    - tuikuan_yuanyin: 退款原因（可选）
    
    返回：
    - 退款记录信息
    """
    service = ZhifuTuikuanService(db)
    return service.create_refund(tuikuan_data, current_user.id)


@router.get("/", response_model=ZhifuTuikuanListResponse, summary="获取退款列表")
def get_refund_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tuikuan_zhuangtai: Optional[str] = Query(None, description="退款状态筛选"),
    tuikuan_pingtai: Optional[str] = Query(None, description="退款平台筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("zhifu:tuikuan:list"))
):
    """
    获取退款列表
    
    权限要求：zhifu:tuikuan:list
    
    参数：
    - page: 页码（默认1）
    - page_size: 每页数量（默认20，最大100）
    - tuikuan_zhuangtai: 退款状态筛选（可选）
    - tuikuan_pingtai: 退款平台筛选（可选）
    - search: 搜索关键词（可选）
    
    返回：
    - 退款列表和分页信息
    """
    service = ZhifuTuikuanService(db)
    return service.get_refund_list(
        page=page,
        page_size=page_size,
        tuikuan_zhuangtai=tuikuan_zhuangtai,
        tuikuan_pingtai=tuikuan_pingtai,
        search=search
    )


@router.get("/{tuikuan_id}", response_model=ZhifuTuikuanResponse, summary="获取退款详情")
def get_refund_detail(
    tuikuan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("zhifu:tuikuan:view"))
):
    """
    获取退款详情
    
    权限要求：zhifu:tuikuan:view
    
    参数：
    - tuikuan_id: 退款ID
    
    返回：
    - 退款详细信息
    """
    service = ZhifuTuikuanService(db)
    return service.get_refund_by_id(tuikuan_id)

