"""
线索报价管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.xiansuo_guanli.xiansuo_baojia_service import XiansuoBaojiaService
from src.schemas.xiansuo_guanli.xiansuo_baojia_schemas import (
    XiansuoBaojiaCreate,
    XiansuoBaojiaUpdate,
    XiansuoBaojiaResponse,
    XiansuoBaojiaDetailResponse,
    XiansuoBaojiaListResponse,
    XiansuoBaojiaListParams,
    XiansuoBaojiaStatistics,
    ChanpinDataForBaojia
)

router = APIRouter()


@router.post("/", response_model=XiansuoBaojiaResponse)
async def create_baojia(
    baojia_data: XiansuoBaojiaCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_create"))
):
    """创建线索报价"""
    service = XiansuoBaojiaService(db)
    return await service.create_baojia(baojia_data, current_user.id)


@router.get("/", response_model=XiansuoBaojiaListResponse)
async def get_baojia_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    xiansuo_id: str = Query(None, description="线索ID"),
    baojia_zhuangtai: str = Query(None, description="报价状态"),
    search: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_read"))
):
    """获取报价列表"""
    
    params = XiansuoBaojiaListParams(
        page=page,
        size=size,
        xiansuo_id=xiansuo_id,
        baojia_zhuangtai=baojia_zhuangtai,
        search=search
    )
    
    service = XiansuoBaojiaService(db)
    return await service.get_baojia_list(params)


@router.get("/statistics", response_model=XiansuoBaojiaStatistics)
async def get_baojia_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_statistics"))
):
    """获取报价统计"""
    service = XiansuoBaojiaService(db)
    return await service.get_baojia_statistics()


@router.get("/product-data", response_model=ChanpinDataForBaojia)
async def get_product_data_for_baojia(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_create"))
):
    """获取报价用产品数据"""
    service = XiansuoBaojiaService(db)
    return await service.get_chanpin_data_for_baojia()


@router.get("/xiansuo/{xiansuo_id}", response_model=List[XiansuoBaojiaResponse])
async def get_xiansuo_baojia_list(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_read"))
):
    """获取指定线索的报价列表"""
    service = XiansuoBaojiaService(db)
    return await service.get_baojia_by_xiansuo(xiansuo_id)


@router.get("/{baojia_id}", response_model=XiansuoBaojiaResponse)
async def get_baojia_detail(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_read"))
):
    """获取报价详情"""
    service = XiansuoBaojiaService(db)
    return await service.get_baojia_detail(baojia_id)


@router.get("/{baojia_id}/detail", response_model=XiansuoBaojiaDetailResponse, summary="获取报价详情（包含线索信息）")
async def get_baojia_detail_with_xiansuo(
    baojia_id: str,
    db: Session = Depends(get_db)
):
    """
    获取报价详情（包含线索信息）

    此端点用于客户端查看报价单，无需认证
    包含完整的线索信息用于显示客户信息
    """
    service = XiansuoBaojiaService(db)
    return await service.get_baojia_detail_with_xiansuo(baojia_id)


@router.put("/{baojia_id}", response_model=XiansuoBaojiaResponse)
async def update_baojia(
    baojia_id: str,
    baojia_data: XiansuoBaojiaUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_update"))
):
    """更新报价"""
    service = XiansuoBaojiaService(db)
    return await service.update_baojia(baojia_id, baojia_data, current_user.id)


@router.patch("/{baojia_id}/status", response_model=XiansuoBaojiaResponse)
async def update_baojia_status(
    baojia_id: str,
    new_status: str = Query(..., description="新状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_status_update"))
):
    """更新报价状态"""
    service = XiansuoBaojiaService(db)
    return await service.update_baojia_status(baojia_id, new_status, current_user.id)


@router.delete("/{baojia_id}")
async def delete_baojia(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_delete"))
):
    """删除报价"""
    service = XiansuoBaojiaService(db)
    success = await service.delete_baojia(baojia_id, current_user.id)

    if success:
        return {"message": "报价删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )


@router.post("/{baojia_id}/confirm", response_model=XiansuoBaojiaResponse)
async def confirm_baojia(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_status_update"))
):
    """确认报价"""
    service = XiansuoBaojiaService(db)
    return await service.confirm_baojia(baojia_id, current_user.id)


@router.post("/{baojia_id}/reject", response_model=XiansuoBaojiaResponse)
async def reject_baojia(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_status_update"))
):
    """拒绝报价"""
    service = XiansuoBaojiaService(db)
    return await service.reject_baojia(baojia_id, current_user.id)


@router.post("/check-expired")
async def check_expired_baojia(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:baojia_manage"))
):
    """检查并更新过期报价"""
    service = XiansuoBaojiaService(db)
    count = await service.check_expired_baojia()

    return {
        "message": f"已更新 {count} 个过期报价",
        "expired_count": count
    }
