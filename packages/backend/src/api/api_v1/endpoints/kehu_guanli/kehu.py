"""
客户管理 API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.kehu_guanli import KehuService
from src.schemas.kehu_guanli.kehu_schemas import (
    KehuCreate,
    KehuUpdate,
    KehuResponse,
    KehuListResponse
)

router = APIRouter()


@router.post("/", response_model=KehuResponse, summary="创建客户")
async def create_kehu(
    kehu_data: KehuCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:create"))
):
    """
    创建新客户
    
    - **gongsi_mingcheng**: 公司名称（必填）
    - **tongyi_shehui_xinyong_daima**: 统一社会信用代码（必填，18位）
    - **faren_xingming**: 法人姓名（必填）
    - **kehu_zhuangtai**: 客户状态（active/renewing/terminated）
    """
    service = KehuService(db)
    return service.create_kehu(kehu_data, current_user.id)


@router.get("/", response_model=KehuListResponse, summary="获取客户列表")
async def get_kehu_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=1000, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（公司名称、信用代码、法人姓名等）"),
    kehu_zhuangtai: Optional[str] = Query(None, description="客户状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:read"))
):
    """
    获取客户列表
    
    支持分页、搜索和状态筛选
    """
    service = KehuService(db)
    return service.get_kehu_list(
        page=page,
        size=size,
        search=search,
        kehu_zhuangtai=kehu_zhuangtai
    )


@router.get("/{kehu_id}", response_model=KehuResponse, summary="获取客户详情")
async def get_kehu_detail(
    kehu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:read"))
):
    """
    根据ID获取客户详细信息
    """
    service = KehuService(db)
    kehu = service.get_kehu_by_id(kehu_id)
    
    if not kehu:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    return kehu


@router.put("/{kehu_id}", response_model=KehuResponse, summary="更新客户信息")
async def update_kehu(
    kehu_id: str,
    kehu_data: KehuUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:update"))
):
    """
    更新客户信息
    
    支持部分字段更新
    """
    service = KehuService(db)
    return service.update_kehu(kehu_id, kehu_data, current_user.id)


@router.delete("/{kehu_id}", summary="删除客户")
async def delete_kehu(
    kehu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:delete"))
):
    """
    删除客户（软删除）
    """
    service = KehuService(db)
    success = service.delete_kehu(kehu_id, current_user.id)
    
    return {"message": "客户删除成功" if success else "客户删除失败"}


@router.patch("/{kehu_id}/status", response_model=KehuResponse, summary="更新客户状态")
async def update_kehu_status(
    kehu_id: str,
    new_status: str = Query(..., description="新状态（active/renewing/terminated）"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("customer:status_manage"))
):
    """
    更新客户状态
    
    - **active**: 活跃
    - **renewing**: 续约中
    - **terminated**: 已终止
    """
    service = KehuService(db)
    return service.update_kehu_status(kehu_id, new_status, current_user.id)
