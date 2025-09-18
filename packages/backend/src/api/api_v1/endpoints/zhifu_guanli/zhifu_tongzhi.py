"""
支付通知管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from src.core.database import get_db
from src.core.security.permissions import require_permission
from src.core.security import get_current_user
from src.models.yonghu_guanli import Yonghu
from src.models.zhifu_guanli import ZhifuTongzhi
from src.services.zhifu_guanli.zhifu_tongzhi_service import ZhifuTongzhiService
from src.schemas.zhifu_guanli.zhifu_tongzhi_schemas import (
    ZhifuTongzhiCreate,
    ZhifuTongzhiUpdate,
    ZhifuTongzhiResponse,
    ZhifuTongzhiListResponse,
    ZhifuTongzhiListParams
)

router = APIRouter()


@router.post("/", response_model=ZhifuTongzhiResponse, summary="创建支付通知")
async def create_zhifu_tongzhi(
    tongzhi_data: ZhifuTongzhiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("notification:create"))
):
    """
    创建新的支付通知
    
    - **jieshou_ren_id**: 接收人ID（必填）
    - **tongzhi_leixing**: 通知类型（必填）
    - **tongzhi_biaoti**: 通知标题（必填）
    - **tongzhi_neirong**: 通知内容（必填）
    """
    service = ZhifuTongzhiService(db)
    return service.create_zhifu_tongzhi(tongzhi_data, current_user.id)


@router.get("/", response_model=ZhifuTongzhiListResponse, summary="获取支付通知列表")
async def get_zhifu_tongzhi_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    jieshou_ren_id: str = Query(None, description="接收人ID"),
    tongzhi_leixing: str = Query(None, description="通知类型"),
    tongzhi_zhuangtai: str = Query(None, description="通知状态"),
    youxian_ji: str = Query(None, description="优先级"),
    fasong_qudao: str = Query(None, description="发送渠道"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("notification:read"))
):
    """
    获取支付通知列表
    
    支持分页、搜索和筛选
    """
    params = ZhifuTongzhiListParams(
        page=page,
        size=size,
        search=search,
        jieshou_ren_id=jieshou_ren_id,
        tongzhi_leixing=tongzhi_leixing,
        tongzhi_zhuangtai=tongzhi_zhuangtai,
        youxian_ji=youxian_ji,
        fasong_qudao=fasong_qudao
    )
    service = ZhifuTongzhiService(db)
    return service.get_zhifu_tongzhi_list(params)


@router.get("/my", response_model=ZhifuTongzhiListResponse, summary="获取我的通知列表")
async def get_my_tongzhi_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    tongzhi_leixing: str = Query(None, description="通知类型"),
    tongzhi_zhuangtai: str = Query(None, description="通知状态"),
    youxian_ji: str = Query(None, description="优先级"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户的通知列表
    """
    params = ZhifuTongzhiListParams(
        page=page,
        size=size,
        search=search,
        jieshou_ren_id=current_user.id,
        tongzhi_leixing=tongzhi_leixing,
        tongzhi_zhuangtai=tongzhi_zhuangtai,
        youxian_ji=youxian_ji
    )
    service = ZhifuTongzhiService(db)
    return service.get_zhifu_tongzhi_list(params)


@router.get("/my/unread-count", summary="获取未读通知数量")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户的未读通知数量
    """
    service = ZhifuTongzhiService(db)
    count = service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.get("/{tongzhi_id}", response_model=ZhifuTongzhiResponse, summary="获取支付通知详情")
async def get_zhifu_tongzhi_detail(
    tongzhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("notification:read"))
):
    """
    根据ID获取支付通知详情
    """
    service = ZhifuTongzhiService(db)
    return service.get_zhifu_tongzhi_by_id(tongzhi_id)


@router.put("/{tongzhi_id}", response_model=ZhifuTongzhiResponse, summary="更新支付通知")
async def update_zhifu_tongzhi(
    tongzhi_id: str,
    tongzhi_data: ZhifuTongzhiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("notification:update"))
):
    """
    更新支付通知信息
    """
    service = ZhifuTongzhiService(db)
    return service.update_zhifu_tongzhi(tongzhi_id, tongzhi_data, current_user.id)


@router.post("/{tongzhi_id}/read", response_model=ZhifuTongzhiResponse, summary="标记通知为已读")
async def mark_tongzhi_as_read(
    tongzhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    标记通知为已读
    
    只能标记发送给当前用户的通知
    """
    service = ZhifuTongzhiService(db)
    return service.mark_as_read(tongzhi_id, current_user.id)


@router.delete("/{tongzhi_id}", summary="删除支付通知")
async def delete_zhifu_tongzhi(
    tongzhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("notification:delete"))
):
    """
    删除支付通知（软删除）
    """
    service = ZhifuTongzhiService(db)
    zhifu_tongzhi = service.get_zhifu_tongzhi_by_id(tongzhi_id)
    
    # 执行软删除
    db.query(ZhifuTongzhi).filter(ZhifuTongzhi.id == tongzhi_id).update({
        "is_deleted": "Y",
        "updated_by": current_user.id,
        "updated_at": datetime.now()
    })
    db.commit()
    
    return {"message": "支付通知删除成功"}
