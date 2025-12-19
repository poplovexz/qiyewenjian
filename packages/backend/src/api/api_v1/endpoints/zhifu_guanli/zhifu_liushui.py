"""
支付流水管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from models.zhifu_guanli import ZhifuLiushui
from services.zhifu_guanli.zhifu_liushui_service import ZhifuLiushuiService
from schemas.zhifu_guanli.zhifu_liushui_schemas import (
    ZhifuLiushuiCreate,
    ZhifuLiushuiUpdate,
    ZhifuLiushuiResponse,
    ZhifuLiushuiListResponse,
    ZhifuLiushuiListParams
)

router = APIRouter()

@router.post("/", response_model=ZhifuLiushuiResponse, summary="创建支付流水")
async def create_zhifu_liushui(
    liushui_data: ZhifuLiushuiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:create"))
):
    """
    创建新的支付流水
    
    - **zhifu_dingdan_id**: 支付订单ID（必填）
    - **kehu_id**: 客户ID（必填）
    - **liushui_leixing**: 流水类型（必填）
    - **jiaoyijine**: 交易金额（必填）
    - **zhifu_fangshi**: 支付方式（必填）
    """
    service = ZhifuLiushuiService(db)
    return service.create_zhifu_liushui(liushui_data, current_user.id)

@router.get("/", response_model=ZhifuLiushuiListResponse, summary="获取支付流水列表")
async def get_zhifu_liushui_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    zhifu_dingdan_id: str = Query(None, description="支付订单ID"),
    kehu_id: str = Query(None, description="客户ID"),
    liushui_leixing: str = Query(None, description="流水类型"),
    zhifu_fangshi: str = Query(None, description="支付方式"),
    liushui_zhuangtai: str = Query(None, description="流水状态"),
    duizhang_zhuangtai: str = Query(None, description="对账状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:read"))
):
    """
    获取支付流水列表
    
    支持分页、搜索和筛选
    """
    params = ZhifuLiushuiListParams(
        page=page,
        size=size,
        search=search,
        zhifu_dingdan_id=zhifu_dingdan_id,
        kehu_id=kehu_id,
        liushui_leixing=liushui_leixing,
        zhifu_fangshi=zhifu_fangshi,
        liushui_zhuangtai=liushui_zhuangtai,
        duizhang_zhuangtai=duizhang_zhuangtai
    )
    service = ZhifuLiushuiService(db)
    return service.get_zhifu_liushui_list(params)

@router.get("/{liushui_id}", response_model=ZhifuLiushuiResponse, summary="获取支付流水详情")
async def get_zhifu_liushui_detail(
    liushui_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:read"))
):
    """
    根据ID获取支付流水详情
    """
    service = ZhifuLiushuiService(db)
    return service.get_zhifu_liushui_by_id(liushui_id)

@router.put("/{liushui_id}", response_model=ZhifuLiushuiResponse, summary="更新支付流水")
async def update_zhifu_liushui(
    liushui_id: str,
    liushui_data: ZhifuLiushuiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:update"))
):
    """
    更新支付流水信息
    
    可以更新流水状态、对账状态等
    """
    service = ZhifuLiushuiService(db)
    return service.update_zhifu_liushui(liushui_id, liushui_data, current_user.id)

@router.post("/{liushui_id}/confirm", response_model=ZhifuLiushuiResponse, summary="财务确认流水")
async def confirm_zhifu_liushui(
    liushui_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance:confirm"))
):
    """
    财务确认支付流水
    
    将流水标记为已对账状态
    """
    service = ZhifuLiushuiService(db)
    return service.confirm_liushui_by_finance(liushui_id, current_user.id)

@router.delete("/{liushui_id}", summary="删除支付流水")
async def delete_zhifu_liushui(
    liushui_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment:delete"))
):
    """
    删除支付流水（软删除）
    """
    service = ZhifuLiushuiService(db)
    zhifu_liushui = service.get_zhifu_liushui_by_id(liushui_id)
    
    # 执行软删除
    db.query(ZhifuLiushui).filter(ZhifuLiushui.id == liushui_id).update({
        "is_deleted": "Y",
        "updated_by": current_user.id,
        "updated_at": datetime.now()
    })
    db.commit()
    
    return {"message": "支付流水删除成功"}
