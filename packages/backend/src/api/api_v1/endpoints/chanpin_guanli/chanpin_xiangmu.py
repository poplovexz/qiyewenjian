"""
产品项目管理API端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from schemas.chanpin_guanli import (
    ChanpinXiangmuCreate,
    ChanpinXiangmuUpdate,
    ChanpinXiangmuResponse,
    ChanpinXiangmuListResponse,
    ChanpinXiangmuDetailResponse
)
from services.chanpin_guanli import ChanpinXiangmuService


router = APIRouter()


@router.get("/", response_model=ChanpinXiangmuListResponse, summary="获取产品项目列表")
async def get_xiangmu_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    fenlei_id: Optional[str] = Query(None, description="分类ID筛选"),
    chanpin_leixing: Optional[str] = Query(None, description="产品类型筛选"),
    zhuangtai: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:read"))
):
    """获取产品项目列表"""
    try:
        service = ChanpinXiangmuService(db)
        result = await service.get_xiangmu_list(
            page=page,
            size=size,
            search=search,
            fenlei_id=fenlei_id,
            chanpin_leixing=chanpin_leixing,
            zhuangtai=zhuangtai
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品项目列表失败: {str(e)}"
        )


@router.get("/{xiangmu_id}", response_model=ChanpinXiangmuResponse, summary="获取产品项目详情")
async def get_xiangmu_detail(
    xiangmu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:read"))
):
    """获取产品项目详情"""
    try:
        service = ChanpinXiangmuService(db)
        result = await service.get_xiangmu_by_id(xiangmu_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品项目不存在"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品项目详情失败: {str(e)}"
        )


@router.get("/{xiangmu_id}/detail", response_model=ChanpinXiangmuDetailResponse, summary="获取产品项目完整详情")
async def get_xiangmu_full_detail(
    xiangmu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:read"))
):
    """获取产品项目完整详情（包含步骤列表）"""
    try:
        service = ChanpinXiangmuService(db)
        result = await service.get_xiangmu_detail(xiangmu_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品项目不存在"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品项目完整详情失败: {str(e)}"
        )


@router.post("/", response_model=ChanpinXiangmuResponse, summary="创建产品项目")
async def create_xiangmu(
    xiangmu_data: ChanpinXiangmuCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:create"))
):
    """创建产品项目"""
    try:
        service = ChanpinXiangmuService(db)
        result = await service.create_xiangmu(
            xiangmu_data=xiangmu_data,
            created_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建产品项目失败: {str(e)}"
        )


@router.put("/{xiangmu_id}", response_model=ChanpinXiangmuResponse, summary="更新产品项目")
async def update_xiangmu(
    xiangmu_id: str,
    xiangmu_data: ChanpinXiangmuUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:update"))
):
    """更新产品项目"""
    try:
        service = ChanpinXiangmuService(db)
        result = await service.update_xiangmu(
            xiangmu_id=xiangmu_id,
            xiangmu_data=xiangmu_data,
            updated_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新产品项目失败: {str(e)}"
        )


@router.delete("/{xiangmu_id}", summary="删除产品项目")
async def delete_xiangmu(
    xiangmu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:delete"))
):
    """删除产品项目"""
    try:
        service = ChanpinXiangmuService(db)
        await service.delete_xiangmu(
            xiangmu_id=xiangmu_id,
            deleted_by=current_user.yonghu_ming
        )
        return {"message": "产品项目删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除产品项目失败: {str(e)}"
        )
