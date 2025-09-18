"""
线索状态管理 API 端点
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.xiansuo_guanli import XiansuoZhuangtaiService
from src.schemas.xiansuo_guanli import (
    XiansuoZhuangtaiCreate,
    XiansuoZhuangtaiUpdate,
    XiansuoZhuangtaiResponse,
    XiansuoZhuangtaiListResponse
)

router = APIRouter()


@router.post("/", response_model=XiansuoZhuangtaiResponse, summary="创建线索状态")
async def create_zhuangtai(
    zhuangtai_data: XiansuoZhuangtaiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_create"))
):
    """
    创建新的线索状态
    
    - **zhuangtai_mingcheng**: 状态名称（必填）
    - **zhuangtai_bianma**: 状态编码（必填，唯一）
    - **zhuangtai_leixing**: 状态类型（initial/processing/success/failed）
    """
    service = XiansuoZhuangtaiService(db)
    return service.create_zhuangtai(zhuangtai_data, current_user.id)


@router.get("/", response_model=XiansuoZhuangtaiListResponse, summary="获取线索状态列表")
async def get_zhuangtai_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（名称、编码、描述）"),
    zhuangtai_leixing: Optional[str] = Query(None, description="状态类型筛选"),
    zhuangtai: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_read"))
):
    """
    获取线索状态列表
    
    支持分页、搜索和筛选
    """
    service = XiansuoZhuangtaiService(db)
    return service.get_zhuangtai_list(
        page=page,
        size=size,
        search=search,
        zhuangtai_leixing=zhuangtai_leixing,
        zhuangtai=zhuangtai
    )


@router.get("/active", response_model=List[XiansuoZhuangtaiResponse], summary="获取启用的线索状态")
async def get_active_zhuangtai_list(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_read"))
):
    """获取所有启用状态的线索状态"""
    service = XiansuoZhuangtaiService(db)
    return service.get_active_zhuangtai_list()


@router.get("/{zhuangtai_id}", response_model=XiansuoZhuangtaiResponse, summary="获取线索状态详情")
async def get_zhuangtai_detail(
    zhuangtai_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_read"))
):
    """根据ID获取线索状态详情"""
    service = XiansuoZhuangtaiService(db)
    zhuangtai = service.get_zhuangtai_by_id(zhuangtai_id)
    
    if not zhuangtai:
        raise HTTPException(status_code=404, detail="线索状态不存在")
    
    return zhuangtai


@router.put("/{zhuangtai_id}", response_model=XiansuoZhuangtaiResponse, summary="更新线索状态")
async def update_zhuangtai(
    zhuangtai_id: str,
    zhuangtai_data: XiansuoZhuangtaiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_update"))
):
    """
    更新线索状态信息

    - 支持部分字段更新
    - 编码更新时会验证唯一性
    """
    service = XiansuoZhuangtaiService(db)
    return service.update_zhuangtai(zhuangtai_id, zhuangtai_data, current_user.id)


@router.delete("/{zhuangtai_id}", summary="删除线索状态")
async def delete_zhuangtai(
    zhuangtai_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:status_delete"))
):
    """
    删除线索状态（软删除）
    
    - 如果该状态下有线索，则无法删除
    """
    service = XiansuoZhuangtaiService(db)
    success = service.delete_zhuangtai(zhuangtai_id, current_user.id)
    
    if success:
        return {"message": "线索状态删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")
