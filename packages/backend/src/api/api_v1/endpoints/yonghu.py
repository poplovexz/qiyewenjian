"""
用户管理 API 端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from schemas.yonghu_guanli import (
    YonghuCreate, YonghuUpdate, YonghuResponse, YonghuList,
    JiaoseResponse, QuanxianResponse
)
from services.yonghu_guanli.yonghu_service import YonghuService

router = APIRouter()


@router.post("/", response_model=YonghuResponse, status_code=status.HTTP_201_CREATED)
def create_yonghu(
    yonghu_data: YonghuCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:create"))
):
    """创建用户"""
    yonghu_service = YonghuService(db)
    return yonghu_service.create_yonghu(yonghu_data, current_user.id)


@router.get("/", response_model=YonghuList)
def get_yonghu_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    zhuangtai: Optional[str] = Query(None, description="用户状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:read"))
):
    """获取用户列表"""
    yonghu_service = YonghuService(db)
    return yonghu_service.get_yonghu_list(page, size, search, zhuangtai)


@router.get("/{yonghu_id}", response_model=YonghuResponse)
def get_yonghu(
    yonghu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:read"))
):
    """获取用户详情"""
    yonghu_service = YonghuService(db)
    yonghu = yonghu_service.get_yonghu_by_id(yonghu_id)

    if not yonghu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return yonghu


@router.put("/{yonghu_id}", response_model=YonghuResponse)
def update_yonghu(
    yonghu_id: str,
    yonghu_data: YonghuUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:update"))
):
    """更新用户信息"""
    yonghu_service = YonghuService(db)
    return yonghu_service.update_yonghu(yonghu_id, yonghu_data, current_user.id)


@router.delete("/{yonghu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_yonghu(
    yonghu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:delete"))
):
    """删除用户"""
    yonghu_service = YonghuService(db)
    yonghu_service.delete_yonghu(yonghu_id, current_user.id)


@router.post("/{yonghu_id}/roles", status_code=status.HTTP_200_OK)
def assign_yonghu_roles(
    yonghu_id: str,
    jiaose_ids: List[str],
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:role_manage"))
):
    """为用户分配角色"""
    yonghu_service = YonghuService(db)
    success = yonghu_service.assign_roles(yonghu_id, jiaose_ids, current_user.id)

    if success:
        return {"message": "角色分配成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色分配失败"
        )


@router.get("/{yonghu_id}/roles", response_model=List[JiaoseResponse])
def get_yonghu_roles(
    yonghu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:read"))
):
    """获取用户的角色列表"""
    yonghu_service = YonghuService(db)
    return yonghu_service.get_yonghu_roles(yonghu_id)


@router.get("/{yonghu_id}/permissions", response_model=List[QuanxianResponse])
def get_yonghu_permissions(
    yonghu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("user:read"))
):
    """获取用户的权限列表"""
    yonghu_service = YonghuService(db)
    return yonghu_service.get_yonghu_permissions(yonghu_id)
