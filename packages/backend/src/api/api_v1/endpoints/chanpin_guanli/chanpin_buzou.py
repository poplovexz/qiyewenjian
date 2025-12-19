"""
产品步骤管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from schemas.chanpin_guanli import (
    ChanpinBuzouCreate,
    ChanpinBuzouUpdate,
    ChanpinBuzouResponse,
    ChanpinBuzouBatchUpdate
)
from services.chanpin_guanli import ChanpinBuzouService

router = APIRouter()

@router.get("/products/{xiangmu_id}/steps", response_model=List[ChanpinBuzouResponse], summary="获取产品步骤列表")
async def get_buzou_list(
    xiangmu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:read"))
):
    """获取产品步骤列表"""
    try:
        service = ChanpinBuzouService(db)
        result = await service.get_buzou_list(xiangmu_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品步骤列表失败: {str(e)}"
        )

@router.get("/steps/{buzou_id}", response_model=ChanpinBuzouResponse, summary="获取产品步骤详情")
async def get_buzou_detail(
    buzou_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:read"))
):
    """获取产品步骤详情"""
    try:
        service = ChanpinBuzouService(db)
        result = await service.get_buzou_by_id(buzou_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品步骤不存在"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品步骤详情失败: {str(e)}"
        )

@router.post("/steps", response_model=ChanpinBuzouResponse, summary="创建产品步骤")
async def create_buzou(
    buzou_data: ChanpinBuzouCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:update"))
):
    """创建产品步骤"""
    try:
        service = ChanpinBuzouService(db)
        result = await service.create_buzou(
            buzou_data=buzou_data,
            created_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建产品步骤失败: {str(e)}"
        )

@router.put("/steps/{buzou_id}", response_model=ChanpinBuzouResponse, summary="更新产品步骤")
async def update_buzou(
    buzou_id: str,
    buzou_data: ChanpinBuzouUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:update"))
):
    """更新产品步骤"""
    try:
        service = ChanpinBuzouService(db)
        result = await service.update_buzou(
            buzou_id=buzou_id,
            buzou_data=buzou_data,
            updated_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新产品步骤失败: {str(e)}"
        )

@router.delete("/steps/{buzou_id}", summary="删除产品步骤")
async def delete_buzou(
    buzou_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:update"))
):
    """删除产品步骤"""
    try:
        service = ChanpinBuzouService(db)
        await service.delete_buzou(
            buzou_id=buzou_id,
            deleted_by=current_user.yonghu_ming
        )
        return {"message": "产品步骤删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除产品步骤失败: {str(e)}"
        )

@router.put("/products/{xiangmu_id}/steps", response_model=List[ChanpinBuzouResponse], summary="批量更新产品步骤")
async def batch_update_buzou(
    xiangmu_id: str,
    batch_data: ChanpinBuzouBatchUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("product:update"))
):
    """批量更新产品步骤"""
    try:
        service = ChanpinBuzouService(db)
        result = await service.batch_update_buzou(
            xiangmu_id=xiangmu_id,
            buzou_list=batch_data.buzou_list,
            updated_by=current_user.yonghu_ming
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新产品步骤失败: {str(e)}"
        )
