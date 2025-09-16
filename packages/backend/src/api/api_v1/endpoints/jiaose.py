"""
角色管理 API 端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.yonghu_guanli import Yonghu
from ....schemas.yonghu_guanli import (
    JiaoseCreate, JiaoseUpdate, JiaoseResponse, JiaoseList,
    QuanxianResponse
)
from ....services.yonghu_guanli.jiaose_service import JiaoseService

router = APIRouter()


@router.post("/", response_model=JiaoseResponse, status_code=status.HTTP_201_CREATED)
def create_jiaose(
    jiaose_data: JiaoseCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建角色"""
    jiaose_service = JiaoseService(db)
    return jiaose_service.create_jiaose(jiaose_data, current_user.id)


@router.get("/", response_model=JiaoseList)
def get_jiaose_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    zhuangtai: Optional[str] = Query(None, description="角色状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取角色列表"""
    jiaose_service = JiaoseService(db)
    return jiaose_service.get_jiaose_list(skip, limit, search, zhuangtai)


@router.get("/{jiaose_id}", response_model=JiaoseResponse)
def get_jiaose(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取角色详情"""
    jiaose_service = JiaoseService(db)
    jiaose = jiaose_service.get_jiaose_by_id(jiaose_id)
    
    if not jiaose:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return jiaose


@router.put("/{jiaose_id}", response_model=JiaoseResponse)
def update_jiaose(
    jiaose_id: str,
    jiaose_data: JiaoseUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新角色信息"""
    jiaose_service = JiaoseService(db)
    return jiaose_service.update_jiaose(jiaose_id, jiaose_data, current_user.id)


@router.delete("/{jiaose_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_jiaose(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除角色"""
    jiaose_service = JiaoseService(db)
    jiaose_service.delete_jiaose(jiaose_id, current_user.id)


@router.post("/{jiaose_id}/permissions", status_code=status.HTTP_200_OK)
def assign_jiaose_permissions(
    jiaose_id: str,
    quanxian_ids: List[str],
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """为角色分配权限"""
    jiaose_service = JiaoseService(db)
    success = jiaose_service.assign_permissions(jiaose_id, quanxian_ids, current_user.id)
    
    if success:
        return {"message": "权限分配成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限分配失败"
        )


@router.get("/{jiaose_id}/permissions", response_model=List[QuanxianResponse])
def get_jiaose_permissions(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取角色的权限列表"""
    jiaose_service = JiaoseService(db)
    return jiaose_service.get_jiaose_permissions(jiaose_id)
