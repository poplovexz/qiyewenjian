"""
线索来源管理 API 端点
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission, has_permission
from models.yonghu_guanli import Yonghu
from services.xiansuo_guanli import XiansuoLaiyuanService
from schemas.xiansuo_guanli import (
    XiansuoLaiyuanCreate,
    XiansuoLaiyuanUpdate,
    XiansuoLaiyuanResponse,
    XiansuoLaiyuanListResponse
)

router = APIRouter()

@router.post("/", response_model=XiansuoLaiyuanResponse, summary="创建线索来源")
async def create_laiyuan(
    laiyuan_data: XiansuoLaiyuanCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_create"))
):
    """
    创建新的线索来源
    
    - **laiyuan_mingcheng**: 来源名称（必填）
    - **laiyuan_bianma**: 来源编码（必填，唯一）
    - **laiyuan_leixing**: 来源类型（online/offline/referral）
    - **huoqu_chengben**: 获取成本（元）
    """
    service = XiansuoLaiyuanService(db)
    return await service.create_laiyuan(laiyuan_data, current_user.id)

@router.get("/", response_model=XiansuoLaiyuanListResponse, summary="获取线索来源列表")
async def get_laiyuan_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（名称、编码、描述）"),
    laiyuan_leixing: Optional[str] = Query(None, description="来源类型筛选"),
    zhuangtai: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_read"))
):
    """
    获取线索来源列表

    支持分页、搜索和筛选
    数据隔离：普通用户只能查看自己创建的来源，有source_read_all权限的用户可以查看所有来源
    """
    service = XiansuoLaiyuanService(db)

    # 检查是否有全局查看权限
    has_read_all = has_permission(db, current_user, "xiansuo:source_read_all")

    return service.get_laiyuan_list(
        page=page,
        size=size,
        search=search,
        laiyuan_leixing=laiyuan_leixing,
        zhuangtai=zhuangtai,
        current_user_id=current_user.id,
        has_read_all_permission=has_read_all
    )

@router.get("/active", response_model=List[XiansuoLaiyuanResponse], summary="获取启用的线索来源")
async def get_active_laiyuan_list(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_read"))
):
    """获取所有启用状态的线索来源"""
    service = XiansuoLaiyuanService(db)
    return await service.get_active_laiyuan_list()

@router.get("/{laiyuan_id}", response_model=XiansuoLaiyuanResponse, summary="获取线索来源详情")
async def get_laiyuan_detail(
    laiyuan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_read"))
):
    """根据ID获取线索来源详情"""
    service = XiansuoLaiyuanService(db)
    laiyuan = service.get_laiyuan_by_id(laiyuan_id)
    
    if not laiyuan:
        raise HTTPException(status_code=404, detail="线索来源不存在")
    
    return laiyuan

@router.put("/{laiyuan_id}", response_model=XiansuoLaiyuanResponse, summary="更新线索来源")
async def update_laiyuan(
    laiyuan_id: str,
    laiyuan_data: XiansuoLaiyuanUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_update"))
):
    """
    更新线索来源信息

    - 支持部分字段更新
    - 编码更新时会验证唯一性
    """
    service = XiansuoLaiyuanService(db)
    return await service.update_laiyuan(laiyuan_id, laiyuan_data, current_user.id)

@router.delete("/{laiyuan_id}", summary="删除线索来源")
async def delete_laiyuan(
    laiyuan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:source_delete"))
):
    """
    删除线索来源（软删除）
    
    - 如果该来源下有线索，则无法删除
    """
    service = XiansuoLaiyuanService(db)
    success = await service.delete_laiyuan(laiyuan_id, current_user.id)
    
    if success:
        return {"message": "线索来源删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")
