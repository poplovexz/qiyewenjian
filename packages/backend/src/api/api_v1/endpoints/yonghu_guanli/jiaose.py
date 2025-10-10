"""
角色管理API端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli.yonghu import Yonghu
from schemas.yonghu_guanli.jiaose_schemas import (
    JiaoseCreate,
    JiaoseUpdate,
    JiaoseResponse,
    JiaoseListResponse,
    JiaoseStatusUpdate,
    JiaosePermissionUpdate
)
from services.yonghu_guanli.jiaose_service import JiaoseService

router = APIRouter()


@router.get("/", response_model=JiaoseListResponse, summary="获取角色列表")
async def get_jiaose_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    zhuangtai: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:read"))
):
    """获取角色列表"""
    try:
        result = await JiaoseService.get_jiaose_list(
            db=db,
            page=page,
            size=size,
            search=search,
            zhuangtai=zhuangtai
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色列表失败: {str(e)}"
        )


@router.get("/{jiaose_id}", response_model=JiaoseResponse, summary="获取角色详情")
async def get_jiaose_detail(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:read"))
):
    """获取角色详情"""
    try:
        jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return jiaose
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色详情失败: {str(e)}"
        )


@router.post("/", response_model=JiaoseResponse, summary="创建角色")
async def create_jiaose(
    jiaose_data: JiaoseCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:create"))
):
    """创建新角色"""
    try:
        # 检查角色编码是否已存在
        existing_jiaose = await JiaoseService.get_jiaose_by_bianma(
            db=db, 
            jiaose_bianma=jiaose_data.jiaose_bianma
        )
        if existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色编码已存在"
            )
        
        jiaose = await JiaoseService.create_jiaose(
            db=db,
            jiaose_data=jiaose_data,
            created_by=current_user.yonghu_ming
        )
        return jiaose
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建角色失败: {str(e)}"
        )


@router.put("/{jiaose_id}", response_model=JiaoseResponse, summary="更新角色")
async def update_jiaose(
    jiaose_id: str,
    jiaose_data: JiaoseUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:update"))
):
    """更新角色信息"""
    try:
        # 检查角色是否存在
        existing_jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 如果更新角色编码，检查是否重复
        if jiaose_data.jiaose_bianma and jiaose_data.jiaose_bianma != existing_jiaose.jiaose_bianma:
            duplicate_jiaose = await JiaoseService.get_jiaose_by_bianma(
                db=db, 
                jiaose_bianma=jiaose_data.jiaose_bianma
            )
            if duplicate_jiaose:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色编码已存在"
                )
        
        jiaose = await JiaoseService.update_jiaose(
            db=db,
            jiaose_id=jiaose_id,
            jiaose_data=jiaose_data,
            updated_by=current_user.yonghu_ming
        )
        return jiaose
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色失败: {str(e)}"
        )


@router.delete("/{jiaose_id}", summary="删除角色")
async def delete_jiaose(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:delete"))
):
    """删除角色"""
    try:
        # 检查角色是否存在
        existing_jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查是否有用户使用此角色
        user_count = await JiaoseService.get_jiaose_user_count(db=db, jiaose_id=jiaose_id)
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除角色，还有 {user_count} 个用户使用此角色"
            )
        
        await JiaoseService.delete_jiaose(db=db, jiaose_id=jiaose_id)
        return {"message": "角色删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除角色失败: {str(e)}"
        )


@router.patch("/{jiaose_id}/status", response_model=JiaoseResponse, summary="更新角色状态")
async def update_jiaose_status(
    jiaose_id: str,
    status_data: JiaoseStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:update"))
):
    """更新角色状态（启用/禁用）"""
    try:
        # 检查角色是否存在
        existing_jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        jiaose = await JiaoseService.update_jiaose_status(
            db=db,
            jiaose_id=jiaose_id,
            zhuangtai=status_data.zhuangtai,
            reason=status_data.reason,
            updated_by=current_user.yonghu_ming
        )
        return jiaose
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色状态失败: {str(e)}"
        )


@router.get("/{jiaose_id}/permissions", summary="获取角色权限")
async def get_jiaose_permissions(
    jiaose_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:read"))
):
    """获取角色的所有权限"""
    try:
        # 检查角色是否存在
        existing_jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        permissions = await JiaoseService.get_jiaose_permissions(db=db, jiaose_id=jiaose_id)
        return {"permissions": permissions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色权限失败: {str(e)}"
        )


@router.put("/{jiaose_id}/permissions", summary="更新角色权限")
async def update_jiaose_permissions(
    jiaose_id: str,
    permission_data: JiaosePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("role:permission_manage"))
):
    """更新角色权限（批量分配/移除权限）"""
    try:
        # 检查角色是否存在
        existing_jiaose = await JiaoseService.get_jiaose_by_id(db=db, jiaose_id=jiaose_id)
        if not existing_jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        await JiaoseService.update_jiaose_permissions(
            db=db,
            jiaose_id=jiaose_id,
            permission_ids=permission_data.permission_ids,
            updated_by=current_user.yonghu_ming
        )
        return {"message": "角色权限更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色权限失败: {str(e)}"
        )
