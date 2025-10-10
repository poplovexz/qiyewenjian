"""
合规事项模板管理API接口
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, check_permission
from models.yonghu_guanli import Yonghu
from services.heguishixiang_guanli import HeguishixiangMobanService
from schemas.heguishixiang_guanli.heguishixiang_moban_schemas import (
    HeguishixiangMobanCreate,
    HeguishixiangMobanUpdate,
    HeguishixiangMobanResponse,
    HeguishixiangMobanListParams,
    HeguishixiangMobanListResponse,
    HeguishixiangMobanOptionsResponse
)

router = APIRouter()


@router.post("/", response_model=HeguishixiangMobanResponse, summary="创建合规事项模板")
async def create_heguishixiang_moban(
    moban_data: HeguishixiangMobanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(check_permission("compliance:template:create"))
):
    """
    创建合规事项模板
    
    需要权限：compliance:template:create
    """
    service = HeguishixiangMobanService(db)
    return service.create_moban(moban_data, current_user.id)


@router.get("/", response_model=HeguishixiangMobanListResponse, summary="获取合规事项模板列表")
async def get_heguishixiang_moban_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    shixiang_leixing: str = Query(None, description="事项类型"),
    shenbao_zhouqi: str = Query(None, description="申报周期"),
    moban_zhuangtai: str = Query(None, description="模板状态"),
    fengxian_dengji: str = Query(None, description="风险等级"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(check_permission("compliance:template:read"))
):
    """
    获取合规事项模板列表
    
    需要权限：compliance:template:read
    """
    params = HeguishixiangMobanListParams(
        page=page,
        size=size,
        search=search,
        shixiang_leixing=shixiang_leixing,
        shenbao_zhouqi=shenbao_zhouqi,
        moban_zhuangtai=moban_zhuangtai,
        fengxian_dengji=fengxian_dengji
    )
    service = HeguishixiangMobanService(db)
    return service.get_moban_list(params)


@router.get("/options", response_model=HeguishixiangMobanOptionsResponse, summary="获取合规事项模板选项")
async def get_heguishixiang_moban_options(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取合规事项模板选项
    """
    service = HeguishixiangMobanService(db)
    return service.get_moban_options()


@router.get("/active", response_model=List[HeguishixiangMobanResponse], summary="获取启用的合规事项模板")
async def get_active_heguishixiang_mobans(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取所有启用的合规事项模板
    """
    service = HeguishixiangMobanService(db)
    return service.get_active_mobans()


@router.get("/{moban_id}", response_model=HeguishixiangMobanResponse, summary="获取合规事项模板详情")
async def get_heguishixiang_moban_detail(
    moban_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(check_permission("compliance:template:read"))
):
    """
    根据ID获取合规事项模板详情
    
    需要权限：compliance:template:read
    """
    service = HeguishixiangMobanService(db)
    return service.get_moban_by_id(moban_id)


@router.put("/{moban_id}", response_model=HeguishixiangMobanResponse, summary="更新合规事项模板")
async def update_heguishixiang_moban(
    moban_id: str,
    moban_data: HeguishixiangMobanUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(check_permission("compliance:template:update"))
):
    """
    更新合规事项模板
    
    需要权限：compliance:template:update
    """
    service = HeguishixiangMobanService(db)
    return service.update_moban(moban_id, moban_data, current_user.id)


@router.delete("/{moban_id}", summary="删除合规事项模板")
async def delete_heguishixiang_moban(
    moban_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(check_permission("compliance:template:delete"))
):
    """
    删除合规事项模板（软删除）
    
    需要权限：compliance:template:delete
    """
    service = HeguishixiangMobanService(db)
    service.delete_moban(moban_id, current_user.id)
    return {"message": "合规事项模板删除成功"}
