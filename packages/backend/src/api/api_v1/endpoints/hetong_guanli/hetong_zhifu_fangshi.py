"""
合同支付方式管理API接口
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from schemas.hetong_guanli import (
    HetongZhifuFangshiCreate,
    HetongZhifuFangshiUpdate,
    HetongZhifuFangshiResponse,
    HetongZhifuFangshiListResponse
)
from services.hetong_guanli.hetong_zhifu_fangshi_service import HetongZhifuFangshiService

router = APIRouter()


@router.post("/", response_model=HetongZhifuFangshiResponse)
def create_zhifu_fangshi(
    fangshi_data: HetongZhifuFangshiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """创建支付方式"""
    service = HetongZhifuFangshiService(db)
    return service.create_zhifu_fangshi(fangshi_data, current_user.id)


@router.get("/", response_model=HetongZhifuFangshiListResponse)
def get_zhifu_fangshi_list(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    yifang_zhuti_id: Optional[str] = None,
    zhifu_leixing: Optional[str] = None,
    zhifu_zhuangtai: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取支付方式列表"""
    service = HetongZhifuFangshiService(db)
    return service.get_zhifu_fangshi_list(
        page=page,
        size=size,
        search=search,
        yifang_zhuti_id=yifang_zhuti_id,
        zhifu_leixing=zhifu_leixing,
        zhifu_zhuangtai=zhifu_zhuangtai
    )


@router.get("/by-yifang/{yifang_zhuti_id}", response_model=list[HetongZhifuFangshiResponse])
def get_zhifu_fangshi_by_yifang_zhuti(
    yifang_zhuti_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据乙方主体ID获取支付方式列表"""
    service = HetongZhifuFangshiService(db)
    return service.get_zhifu_fangshi_by_yifang_zhuti(yifang_zhuti_id)


@router.get("/default/{yifang_zhuti_id}", response_model=HetongZhifuFangshiResponse)
def get_default_zhifu_fangshi(
    yifang_zhuti_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取乙方主体的默认支付方式"""
    service = HetongZhifuFangshiService(db)
    fangshi = service.get_default_zhifu_fangshi(yifang_zhuti_id)
    if not fangshi:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="未找到默认支付方式")
    return fangshi


@router.patch("/{zhifu_fangshi_id}/set-default", response_model=HetongZhifuFangshiResponse)
def set_default_zhifu_fangshi(
    zhifu_fangshi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """设置默认支付方式"""
    service = HetongZhifuFangshiService(db)
    return service.set_default_zhifu_fangshi(zhifu_fangshi_id, current_user.id)


@router.get("/{fangshi_id}", response_model=HetongZhifuFangshiResponse)
def get_zhifu_fangshi_by_id(
    fangshi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取支付方式"""
    service = HetongZhifuFangshiService(db)
    return service.get_zhifu_fangshi_by_id(fangshi_id)


@router.put("/{fangshi_id}", response_model=HetongZhifuFangshiResponse)
def update_zhifu_fangshi(
    fangshi_id: str,
    fangshi_data: HetongZhifuFangshiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新支付方式"""
    service = HetongZhifuFangshiService(db)
    return service.update_zhifu_fangshi(fangshi_id, fangshi_data)


@router.delete("/{fangshi_id}")
def delete_zhifu_fangshi(
    fangshi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """删除支付方式"""
    service = HetongZhifuFangshiService(db)
    service.delete_zhifu_fangshi(fangshi_id)
    return {"message": "支付方式删除成功"}
