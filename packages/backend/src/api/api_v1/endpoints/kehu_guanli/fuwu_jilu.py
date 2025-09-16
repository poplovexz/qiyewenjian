"""
服务记录管理 API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.kehu_guanli import FuwuJiluService
from src.schemas.kehu_guanli.fuwu_jilu_schemas import (
    FuwuJiluCreate,
    FuwuJiluUpdate,
    FuwuJiluResponse,
    FuwuJiluListResponse
)

router = APIRouter()


@router.post("/", response_model=FuwuJiluResponse, summary="创建服务记录")
async def create_fuwu_jilu(
    fuwu_jilu_data: FuwuJiluCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("service_record:create"))
):
    """
    创建新的服务记录
    
    - **kehu_id**: 客户ID（必填）
    - **goutong_fangshi**: 沟通方式（phone/email/online/meeting）
    - **goutong_neirong**: 沟通内容（必填）
    - **wenti_leixing**: 问题类型（zhangwu/shuiwu/zixun/other）
    """
    service = FuwuJiluService(db)
    return service.create_fuwu_jilu(fuwu_jilu_data, current_user.id)


@router.get("/", response_model=FuwuJiluListResponse, summary="获取服务记录列表")
async def get_fuwu_jilu_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=1000, description="每页数量"),
    kehu_id: Optional[str] = Query(None, description="客户ID筛选"),
    goutong_fangshi: Optional[str] = Query(None, description="沟通方式筛选"),
    wenti_leixing: Optional[str] = Query(None, description="问题类型筛选"),
    chuli_zhuangtai: Optional[str] = Query(None, description="处理状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取服务记录列表
    
    支持分页、多条件筛选和搜索
    """
    service = FuwuJiluService(db)
    return service.get_fuwu_jilu_list(
        page=page,
        size=size,
        kehu_id=kehu_id,
        goutong_fangshi=goutong_fangshi,
        wenti_leixing=wenti_leixing,
        chuli_zhuangtai=chuli_zhuangtai,
        search=search
    )


@router.get("/{fuwu_jilu_id}", response_model=FuwuJiluResponse, summary="获取服务记录详情")
async def get_fuwu_jilu_detail(
    fuwu_jilu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    根据ID获取服务记录详细信息
    """
    service = FuwuJiluService(db)
    fuwu_jilu = service.get_fuwu_jilu_by_id(fuwu_jilu_id)
    
    if not fuwu_jilu:
        raise HTTPException(status_code=404, detail="服务记录不存在")
    
    return fuwu_jilu


@router.put("/{fuwu_jilu_id}", response_model=FuwuJiluResponse, summary="更新服务记录")
async def update_fuwu_jilu(
    fuwu_jilu_id: str,
    fuwu_jilu_data: FuwuJiluUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    更新服务记录信息
    
    支持部分字段更新
    """
    service = FuwuJiluService(db)
    return service.update_fuwu_jilu(fuwu_jilu_id, fuwu_jilu_data, current_user.id)


@router.delete("/{fuwu_jilu_id}", summary="删除服务记录")
async def delete_fuwu_jilu(
    fuwu_jilu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    删除服务记录（软删除）
    """
    service = FuwuJiluService(db)
    success = service.delete_fuwu_jilu(fuwu_jilu_id, current_user.id)
    
    return {"message": "服务记录删除成功" if success else "服务记录删除失败"}


@router.get("/kehu/{kehu_id}/records", response_model=FuwuJiluListResponse, summary="获取客户服务记录")
async def get_kehu_fuwu_jilu_list(
    kehu_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=500, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取指定客户的所有服务记录
    """
    service = FuwuJiluService(db)
    return service.get_kehu_fuwu_jilu_list(kehu_id, page, size)


@router.patch("/{fuwu_jilu_id}/status", response_model=FuwuJiluResponse, summary="更新处理状态")
async def update_chuli_zhuangtai(
    fuwu_jilu_id: str,
    new_status: str = Query(..., description="新状态（pending/processing/completed/cancelled）"),
    chuli_jieguo: Optional[str] = Query(None, description="处理结果"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    更新服务记录的处理状态
    
    - **pending**: 待处理
    - **processing**: 处理中
    - **completed**: 已完成
    - **cancelled**: 已取消
    """
    service = FuwuJiluService(db)
    return service.update_chuli_zhuangtai(fuwu_jilu_id, new_status, chuli_jieguo, current_user.id)
