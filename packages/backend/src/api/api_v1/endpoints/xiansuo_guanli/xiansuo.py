"""
线索管理 API 端点
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security.permissions import require_permission
from src.models.yonghu_guanli import Yonghu
from src.services.xiansuo_guanli import XiansuoService
from src.schemas.xiansuo_guanli import (
    XiansuoCreate,
    XiansuoUpdate,
    XiansuoResponse,
    XiansuoListResponse,
    XiansuoDetailResponse,
    XiansuoStatusUpdate,
    XiansuoAssignUpdate,
    XiansuoStatistics
)

router = APIRouter()


@router.post("/", response_model=XiansuoResponse, summary="创建线索")
async def create_xiansuo(
    xiansuo_data: XiansuoCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:create"))
):
    """
    创建新线索
    
    - **gongsi_mingcheng**: 公司名称（必填）
    - **lianxi_ren**: 联系人（必填）
    - **lianxi_dianhua**: 联系电话
    - **laiyuan_id**: 线索来源ID（必填）
    - **zhiliang_pinggu**: 质量评估（high/medium/low）
    """
    service = XiansuoService(db)
    return service.create_xiansuo(xiansuo_data, current_user.id)


@router.get("/", response_model=XiansuoListResponse, summary="获取线索列表")
async def get_xiansuo_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（编码、公司名称、联系人等）"),
    xiansuo_zhuangtai: Optional[str] = Query(None, description="线索状态筛选"),
    laiyuan_id: Optional[str] = Query(None, description="来源ID筛选"),
    fenpei_ren_id: Optional[str] = Query(None, description="分配人ID筛选"),
    zhiliang_pinggu: Optional[str] = Query(None, description="质量评估筛选"),
    hangye_leixing: Optional[str] = Query(None, description="行业类型筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """
    获取线索列表
    
    支持分页、搜索和多维度筛选
    """
    service = XiansuoService(db)
    return service.get_xiansuo_list(
        page=page,
        size=size,
        search=search,
        xiansuo_zhuangtai=xiansuo_zhuangtai,
        laiyuan_id=laiyuan_id,
        fenpei_ren_id=fenpei_ren_id,
        zhiliang_pinggu=zhiliang_pinggu,
        hangye_leixing=hangye_leixing,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/statistics", response_model=XiansuoStatistics, summary="获取线索统计数据")
async def get_xiansuo_statistics(
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    fenpei_ren_id: Optional[str] = Query(None, description="分配人ID筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """
    获取线索统计数据
    
    包括各状态线索数量、转化率、平均转化周期等
    """
    service = XiansuoService(db)
    return service.get_xiansuo_statistics(
        start_date=start_date,
        end_date=end_date,
        fenpei_ren_id=fenpei_ren_id
    )


@router.get("/{xiansuo_id}", response_model=XiansuoDetailResponse, summary="获取线索详情")
async def get_xiansuo_detail(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:read"))
):
    """根据ID获取线索详情（包含关联数据）"""
    service = XiansuoService(db)
    xiansuo = service.get_xiansuo_detail(xiansuo_id)
    
    if not xiansuo:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    return xiansuo


@router.put("/{xiansuo_id}", response_model=XiansuoResponse, summary="更新线索")
async def update_xiansuo(
    xiansuo_id: str,
    xiansuo_data: XiansuoUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    更新线索信息
    
    - 支持部分字段更新
    - 更新来源时会验证来源是否存在
    """
    service = XiansuoService(db)
    return service.update_xiansuo(xiansuo_id, xiansuo_data, current_user.id)


@router.patch("/{xiansuo_id}/status", response_model=XiansuoResponse, summary="更新线索状态")
async def update_xiansuo_status(
    xiansuo_id: str,
    status_data: XiansuoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    更新线索状态
    
    - 状态变为成交时会自动设置转化信息
    - 会更新来源的转化统计数据
    """
    service = XiansuoService(db)
    return service.update_xiansuo_status(xiansuo_id, status_data, current_user.id)


@router.patch("/{xiansuo_id}/assign", response_model=XiansuoResponse, summary="分配线索")
async def assign_xiansuo(
    xiansuo_id: str,
    assign_data: XiansuoAssignUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:update"))
):
    """
    分配线索给销售人员
    
    - 会验证分配人是否存在
    - 新线索分配后自动变为跟进中状态
    """
    service = XiansuoService(db)
    return service.assign_xiansuo(xiansuo_id, assign_data, current_user.id)


@router.delete("/{xiansuo_id}", summary="删除线索")
async def delete_xiansuo(
    xiansuo_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("xiansuo:delete"))
):
    """
    删除线索（软删除）
    
    - 会同步更新来源的线索统计数据
    """
    service = XiansuoService(db)
    success = service.delete_xiansuo(xiansuo_id, current_user.id)
    
    if success:
        return {"message": "线索删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")
