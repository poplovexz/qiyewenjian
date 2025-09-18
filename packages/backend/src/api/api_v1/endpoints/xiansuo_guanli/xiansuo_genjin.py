"""
线索跟进记录管理 API 端点
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.xiansuo_guanli import XiansuoGenjinService
from src.schemas.xiansuo_guanli import (
    XiansuoGenjinCreate,
    XiansuoGenjinUpdate,
    XiansuoGenjinResponse,
    XiansuoGenjinListResponse
)

router = APIRouter()


@router.post("/", response_model=XiansuoGenjinResponse, summary="创建线索跟进记录")
async def create_genjin(
    genjin_data: XiansuoGenjinCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_create"))
):
    """
    创建新的线索跟进记录
    
    - **xiansuo_id**: 线索ID（必填）
    - **genjin_fangshi**: 跟进方式（phone/email/wechat/visit/other）
    - **genjin_neirong**: 跟进内容（必填）
    - **kehu_fankui**: 客户反馈
    - **kehu_taidu**: 客户态度（positive/neutral/negative）
    """
    service = XiansuoGenjinService(db)
    return service.create_genjin(genjin_data, current_user.id)


@router.get("/", response_model=XiansuoGenjinListResponse, summary="获取线索跟进记录列表")
async def get_genjin_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    xiansuo_id: Optional[str] = Query(None, description="线索ID筛选"),
    genjin_ren_id: Optional[str] = Query(None, description="跟进人ID筛选"),
    genjin_fangshi: Optional[str] = Query(None, description="跟进方式筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_read"))
):
    """
    获取线索跟进记录列表
    
    支持分页、搜索和筛选
    """
    service = XiansuoGenjinService(db)
    return service.get_genjin_list(
        page=page,
        size=size,
        xiansuo_id=xiansuo_id,
        genjin_ren_id=genjin_ren_id,
        genjin_fangshi=genjin_fangshi,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/xiansuo/{xiansuo_id}", response_model=List[XiansuoGenjinResponse], summary="获取指定线索的跟进记录")
async def get_xiansuo_genjin_list(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_read"))
):
    """获取指定线索的所有跟进记录"""
    service = XiansuoGenjinService(db)
    return service.get_xiansuo_genjin_list(xiansuo_id)


@router.get("/{genjin_id}", response_model=XiansuoGenjinResponse, summary="获取跟进记录详情")
async def get_genjin_detail(
    genjin_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_read"))
):
    """根据ID获取跟进记录详情"""
    service = XiansuoGenjinService(db)
    genjin = service.get_genjin_by_id(genjin_id)
    
    if not genjin:
        raise HTTPException(status_code=404, detail="跟进记录不存在")
    
    return genjin


@router.put("/{genjin_id}", response_model=XiansuoGenjinResponse, summary="更新跟进记录")
async def update_genjin(
    genjin_id: str,
    genjin_data: XiansuoGenjinUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_update"))
):
    """
    更新跟进记录信息
    
    - 支持部分字段更新
    - 更新下次跟进时间会同步更新线索表
    """
    service = XiansuoGenjinService(db)
    return service.update_genjin(genjin_id, genjin_data, current_user.id)


@router.delete("/{genjin_id}", summary="删除跟进记录")
async def delete_genjin(
    genjin_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:followup_delete"))
):
    """
    删除跟进记录（软删除）
    
    - 会同步更新线索的跟进次数
    """
    service = XiansuoGenjinService(db)
    success = service.delete_genjin(genjin_id, current_user.id)
    
    if success:
        return {"message": "跟进记录删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")
