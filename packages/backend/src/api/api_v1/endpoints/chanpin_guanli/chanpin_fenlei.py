"""
产品分类管理API端点
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from schemas.chanpin_guanli import (
    ChanpinFenleiCreate,
    ChanpinFenleiUpdate,
    ChanpinFenleiResponse,
    ChanpinFenleiListResponse,
    ChanpinFenleiOption
)
from services.chanpin_guanli import ChanpinFenleiService

router = APIRouter()

@router.get("/", response_model=ChanpinFenleiListResponse, summary="获取产品分类列表")
async def get_fenlei_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    chanpin_leixing: Optional[str] = Query(None, description="产品类型筛选"),
    zhuangtai: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:read"))
):
    """获取产品分类列表"""
    try:
        service = ChanpinFenleiService(db)
        result = await service.get_fenlei_list(
            page=page,
            size=size,
            search=search,
            chanpin_leixing=chanpin_leixing,
            zhuangtai=zhuangtai
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品分类列表失败: {str(e)}"
        )

@router.get("/options", response_model=List[ChanpinFenleiOption], summary="获取产品分类选项")
async def get_fenlei_options(
    chanpin_leixing: Optional[str] = Query(None, description="产品类型筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:read"))
):
    """获取产品分类选项（用于下拉选择）"""
    try:
        service = ChanpinFenleiService(db)
        result = await service.get_fenlei_options(chanpin_leixing=chanpin_leixing)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品分类选项失败: {str(e)}"
        )

@router.get("/{fenlei_id}", response_model=ChanpinFenleiResponse, summary="获取产品分类详情")
async def get_fenlei_detail(
    fenlei_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:read"))
):
    """获取产品分类详情"""
    try:
        service = ChanpinFenleiService(db)
        result = await service.get_fenlei_by_id(fenlei_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品分类不存在"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品分类详情失败: {str(e)}"
        )

@router.post("/", response_model=ChanpinFenleiResponse, summary="创建产品分类")
async def create_fenlei(
    fenlei_data: ChanpinFenleiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:create"))
):
    """创建产品分类"""
    try:
        service = ChanpinFenleiService(db)
        result = await service.create_fenlei(
            fenlei_data=fenlei_data,
            created_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建产品分类失败: {str(e)}"
        )

@router.put("/{fenlei_id}", response_model=ChanpinFenleiResponse, summary="更新产品分类")
async def update_fenlei(
    fenlei_id: str,
    fenlei_data: ChanpinFenleiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:update"))
):
    """更新产品分类"""
    try:
        service = ChanpinFenleiService(db)
        result = await service.update_fenlei(
            fenlei_id=fenlei_id,
            fenlei_data=fenlei_data,
            updated_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新产品分类失败: {str(e)}"
        )

@router.delete("/{fenlei_id}", summary="删除产品分类")
async def delete_fenlei(
    fenlei_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product_category:delete"))
):
    """删除产品分类"""
    try:
        service = ChanpinFenleiService(db)
        await service.delete_fenlei(
            fenlei_id=fenlei_id,
            deleted_by=current_user.yonghu_ming
        )
        return {"message": "产品分类删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除产品分类失败: {str(e)}"
        )
