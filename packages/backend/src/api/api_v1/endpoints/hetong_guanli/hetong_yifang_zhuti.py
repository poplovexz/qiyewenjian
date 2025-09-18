"""
合同乙方主体管理API接口
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.yonghu_guanli import Yonghu
from src.schemas.hetong_guanli import (
    HetongYifangZhutiCreate,
    HetongYifangZhutiUpdate,
    HetongYifangZhutiResponse,
    HetongYifangZhutiListResponse
)
from src.services.hetong_guanli.hetong_yifang_zhuti_service import HetongYifangZhutiService

router = APIRouter()


@router.post("/", response_model=HetongYifangZhutiResponse)
def create_yifang_zhuti(
    zhuti_data: HetongYifangZhutiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建乙方主体"""
    service = HetongYifangZhutiService(db)
    return service.create_yifang_zhuti(zhuti_data, current_user.id)


@router.get("/", response_model=HetongYifangZhutiListResponse)
def get_yifang_zhuti_list(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    zhuti_leixing: Optional[str] = None,
    zhuti_zhuangtai: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取乙方主体列表"""
    service = HetongYifangZhutiService(db)
    return service.get_yifang_zhuti_list(
        page=page,
        size=size,
        search=search,
        zhuti_leixing=zhuti_leixing,
        zhuti_zhuangtai=zhuti_zhuangtai
    )


@router.get("/active", response_model=list[HetongYifangZhutiResponse])
def get_active_yifang_zhuti_list(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取所有启用状态的乙方主体（用于下拉选择）"""
    service = HetongYifangZhutiService(db)
    return service.get_active_yifang_zhuti_list()


@router.get("/{zhuti_id}", response_model=HetongYifangZhutiResponse)
def get_yifang_zhuti_by_id(
    zhuti_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取乙方主体"""
    service = HetongYifangZhutiService(db)
    return service.get_yifang_zhuti_by_id(zhuti_id)


@router.put("/{zhuti_id}", response_model=HetongYifangZhutiResponse)
def update_yifang_zhuti(
    zhuti_id: str,
    zhuti_data: HetongYifangZhutiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新乙方主体"""
    service = HetongYifangZhutiService(db)
    return service.update_yifang_zhuti(zhuti_id, zhuti_data)


@router.delete("/{zhuti_id}")
def delete_yifang_zhuti(
    zhuti_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除乙方主体"""
    service = HetongYifangZhutiService(db)
    service.delete_yifang_zhuti(zhuti_id)
    return {"message": "乙方主体删除成功"}
