"""
合同模板管理 API 端点
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.hetong_guanli import HetongMobanService
from schemas.hetong_guanli.hetong_moban_schemas import (
    HetongMobanCreate,
    HetongMobanUpdate,
    HetongMobanResponse,
    HetongMobanListResponse
)

router = APIRouter()


@router.post("/", response_model=HetongMobanResponse, summary="创建合同模板")
async def create_hetong_moban(
    moban_data: HetongMobanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:create"))
):
    """
    创建新的合同模板
    
    - **moban_mingcheng**: 模板名称（必填）
    - **moban_bianma**: 模板编码（必填，唯一）
    - **hetong_leixing**: 合同类型（必填）
    - **moban_neirong**: 模板内容（必填，支持HTML和变量占位符）
    - **bianliang_peizhi**: 变量配置（JSON格式）
    """
    service = HetongMobanService(db)
    return service.create_hetong_moban(moban_data, current_user.id)


@router.get("/", response_model=HetongMobanListResponse, summary="获取合同模板列表")
async def get_hetong_moban_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    hetong_leixing: Optional[str] = Query(None, description="合同类型筛选"),
    moban_zhuangtai: Optional[str] = Query(None, description="模板状态筛选"),
    moban_fenlei: Optional[str] = Query(None, description="模板分类筛选"),
    shi_dangqian_banben: Optional[str] = Query(None, description="是否当前版本筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:read"))
):
    """
    获取合同模板列表，支持分页、搜索和筛选
    """
    service = HetongMobanService(db)
    return service.get_hetong_moban_list(
        page=page,
        size=size,
        search=search,
        hetong_leixing=hetong_leixing,
        moban_zhuangtai=moban_zhuangtai,
        moban_fenlei=moban_fenlei,
        shi_dangqian_banben=shi_dangqian_banben
    )


@router.get("/{moban_id}", response_model=HetongMobanResponse, summary="获取合同模板详情")
async def get_hetong_moban_detail(
    moban_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:read"))
):
    """
    根据ID获取合同模板详情
    """
    service = HetongMobanService(db)
    return service.get_hetong_moban_by_id(moban_id)


@router.put("/{moban_id}", response_model=HetongMobanResponse, summary="更新合同模板")
async def update_hetong_moban(
    moban_id: str,
    moban_data: HetongMobanUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:update"))
):
    """
    更新合同模板信息
    """
    service = HetongMobanService(db)
    return service.update_hetong_moban(moban_id, moban_data)


@router.delete("/{moban_id}", summary="删除合同模板")
async def delete_hetong_moban(
    moban_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:delete"))
):
    """
    删除合同模板（软删除）
    """
    service = HetongMobanService(db)
    service.delete_hetong_moban(moban_id)
    return {"message": "合同模板删除成功"}


@router.patch("/{moban_id}/status", response_model=HetongMobanResponse, summary="更新模板状态")
async def update_moban_status(
    moban_id: str,
    new_status: str = Query(..., description="新状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:update"))
):
    """
    更新合同模板状态
    
    - **new_status**: 新状态（draft/active/archived）
    """
    service = HetongMobanService(db)
    return service.update_moban_status(moban_id, new_status)


@router.post("/{moban_id}/preview", summary="预览合同模板")
async def preview_hetong_moban(
    moban_id: str,
    bianliang_zhis: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:read"))
):
    """
    预览合同模板，替换变量后返回最终内容
    """
    service = HetongMobanService(db)
    content = service.preview_hetong_moban(moban_id, bianliang_zhis)
    return {"content": content}


@router.get("/{moban_id}/variables", summary="获取模板变量配置")
async def get_moban_variables(
    moban_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:read"))
):
    """
    获取合同模板的变量配置
    """
    service = HetongMobanService(db)
    variables = service.get_moban_bianliang(moban_id)
    return {"variables": variables}


@router.get("/statistics/overview", summary="获取合同模板统计信息")
async def get_hetong_moban_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("contract_template:read"))
):
    """
    获取合同模板统计信息
    """
    service = HetongMobanService(db)
    return service.get_hetong_moban_statistics()
