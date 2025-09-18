"""
审核规则配置API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.yonghu_guanli import Yonghu
from src.services.shenhe_guanli import ShenheGuizeService
from src.schemas.shenhe_guanli import (
    ShenheGuizeCreate,
    ShenheGuizeUpdate,
    ShenheGuizeResponse,
    ShenheGuizeListParams
)

router = APIRouter()


@router.post("/", response_model=ShenheGuizeResponse, summary="创建审核规则")
async def create_shenhe_guize(
    guize_data: ShenheGuizeCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    创建新的审核规则
    
    - **guize_mingcheng**: 规则名称（必填）
    - **guize_leixing**: 规则类型（必填）
    - **chufa_tiaojian**: 触发条件配置（JSON格式）
    - **shenhe_liucheng_peizhi**: 审核流程配置（JSON格式）
    """
    service = ShenheGuizeService(db)
    return service.create_shenhe_guize(guize_data, current_user.id)


@router.get("/", summary="获取审核规则列表")
async def get_shenhe_guize_list(
    page: int = 1,
    size: int = 20,
    search: str = None,
    guize_leixing: str = None,
    shi_qiyong: str = None,
    sort_by: str = "paixu",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取审核规则列表"""
    params = ShenheGuizeListParams(
        page=page,
        size=size,
        search=search,
        guize_leixing=guize_leixing,
        shi_qiyong=shi_qiyong,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = ShenheGuizeService(db)
    return service.get_shenhe_guize_list(params)


@router.get("/{guize_id}", response_model=ShenheGuizeResponse, summary="获取审核规则详情")
async def get_shenhe_guize_by_id(
    guize_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取审核规则详情"""
    service = ShenheGuizeService(db)
    return service.get_shenhe_guize_by_id(guize_id)


@router.put("/{guize_id}", response_model=ShenheGuizeResponse, summary="更新审核规则")
async def update_shenhe_guize(
    guize_id: str,
    guize_data: ShenheGuizeUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新审核规则"""
    service = ShenheGuizeService(db)
    return service.update_shenhe_guize(guize_id, guize_data, current_user.id)


@router.delete("/{guize_id}", summary="删除审核规则")
async def delete_shenhe_guize(
    guize_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除审核规则"""
    service = ShenheGuizeService(db)
    success = service.delete_shenhe_guize(guize_id)
    return {"success": success, "message": "审核规则删除成功"}


@router.get("/type/{guize_leixing}", summary="根据类型获取启用的审核规则")
async def get_active_rules_by_type(
    guize_leixing: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据类型获取启用的审核规则"""
    service = ShenheGuizeService(db)
    return service.get_active_rules_by_type(guize_leixing)
