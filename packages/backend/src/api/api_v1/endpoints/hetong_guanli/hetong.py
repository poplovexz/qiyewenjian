"""
合同管理API接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from schemas.hetong_guanli import (
    HetongCreate,
    HetongUpdate,
    HetongResponse,
    HetongListResponse,
    HetongPreviewRequest,
    HetongPreviewResponse,
    HetongSignRequest
)
from services.hetong_guanli.hetong_service import HetongService

router = APIRouter()


@router.post("/", response_model=HetongResponse)
def create_hetong(
    hetong_data: HetongCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建合同"""
    service = HetongService(db)
    return service.create_hetong(hetong_data, current_user.id)


@router.post("/from-quote/{baojia_id}", response_model=HetongResponse)
def create_hetong_from_baojia(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """基于报价自动生成合同"""
    service = HetongService(db)
    return service.create_hetong_from_baojia(baojia_id, current_user.id)


@router.post("/from-quote-direct", response_model=HetongResponse)
def create_hetong_from_quote_direct(
    request: dict,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """直接从报价生成合同（支持金额修改）"""
    service = HetongService(db)
    return service.create_hetong_from_quote_direct(
        baojia_id=request.get("baojia_id"),
        created_by=current_user.id,
        custom_amount=request.get("custom_amount"),
        change_reason=request.get("change_reason")
    )


@router.get("/", response_model=HetongListResponse)
def get_hetong_list(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    hetong_zhuangtai: Optional[str] = None,
    kehu_id: Optional[str] = None,
    hetong_laiyuan: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取合同列表"""
    service = HetongService(db)
    return service.get_hetong_list(
        page=page,
        size=size,
        search=search,
        hetong_zhuangtai=hetong_zhuangtai,
        kehu_id=kehu_id,
        hetong_laiyuan=hetong_laiyuan
    )


@router.get("/{hetong_id}", response_model=HetongResponse)
def get_hetong_by_id(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取合同"""
    service = HetongService(db)
    return service.get_hetong_by_id(hetong_id)


@router.put("/{hetong_id}", response_model=HetongResponse)
def update_hetong(
    hetong_id: str,
    hetong_data: HetongUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新合同"""
    service = HetongService(db)
    return service.update_hetong(hetong_id, hetong_data)


@router.delete("/{hetong_id}")
def delete_hetong(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除合同"""
    service = HetongService(db)
    service.delete_hetong(hetong_id)
    return {"message": "合同删除成功"}


@router.post("/preview", response_model=HetongPreviewResponse)
def preview_hetong(
    preview_request: HetongPreviewRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """预览合同内容"""
    service = HetongService(db)
    return service.preview_hetong(preview_request)


@router.post("/{hetong_id}/sign", response_model=HetongResponse)
def sign_hetong(
    hetong_id: str,
    sign_request: HetongSignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """签署合同"""
    # 获取客户端IP
    client_ip = request.client.host
    
    service = HetongService(db)
    return service.sign_hetong(hetong_id, sign_request, current_user.id, client_ip)


@router.get("/by-quote/{baojia_id}", response_model=HetongResponse)
def get_hetong_by_baojia_id(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据报价ID获取合同"""
    service = HetongService(db)
    hetong = service.get_hetong_by_baojia_id(baojia_id)
    if not hetong:
        raise HTTPException(status_code=404, detail="该报价尚未生成合同")
    return hetong
