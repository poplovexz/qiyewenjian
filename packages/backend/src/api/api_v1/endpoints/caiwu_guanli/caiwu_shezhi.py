"""
财务设置API端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.caiwu_guanli.caiwu_shezhi_service import CaiwuShezhiService
from schemas.caiwu_guanli.caiwu_shezhi_schemas import (
    ShoufukuanQudaoCreate,
    ShoufukuanQudaoUpdate,
    ShoufukuanQudaoResponse,
    ShoufukuanQudaoListResponse,
    ShouruLeibieCreate,
    ShouruLeibieUpdate,
    ShouruLeibieResponse,
    ShouruLeibieListResponse,
    BaoxiaoLeibieCreate,
    BaoxiaoLeibieUpdate,
    BaoxiaoLeibieResponse,
    BaoxiaoLeibieListResponse,
    ZhichuLeibieCreate,
    ZhichuLeibieUpdate,
    ZhichuLeibieResponse,
    ZhichuLeibieListResponse
)

router = APIRouter()

# ==================== 收付款渠道 ====================
@router.post("/qudao", response_model=ShoufukuanQudaoResponse, summary="创建收付款渠道")
async def create_qudao(
    qudao_data: ShoufukuanQudaoCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:create"))
):
    """创建收付款渠道"""
    service = CaiwuShezhiService(db)
    return service.create_qudao(qudao_data, current_user.id)

@router.get("/qudao", response_model=ShoufukuanQudaoListResponse, summary="获取收付款渠道列表")
async def get_qudao_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    leixing: Optional[str] = Query(None, description="渠道类型"),
    db: Session = Depends(get_db)
):
    """获取收付款渠道列表"""
    service = CaiwuShezhiService(db)
    return service.get_qudao_list(page, size, leixing)

@router.get("/qudao/{qudao_id}", response_model=ShoufukuanQudaoResponse, summary="获取收付款渠道详情")
async def get_qudao_detail(
    qudao_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取收付款渠道详情"""
    service = CaiwuShezhiService(db)
    return service.get_qudao_by_id(qudao_id)

@router.put("/qudao/{qudao_id}", response_model=ShoufukuanQudaoResponse, summary="更新收付款渠道")
async def update_qudao(
    qudao_id: str,
    qudao_data: ShoufukuanQudaoUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:update"))
):
    """更新收付款渠道"""
    service = CaiwuShezhiService(db)
    return service.update_qudao(qudao_id, qudao_data, current_user.id)

@router.delete("/qudao/{qudao_id}", summary="删除收付款渠道")
async def delete_qudao(
    qudao_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:delete"))
):
    """删除收付款渠道"""
    service = CaiwuShezhiService(db)
    service.delete_qudao(qudao_id)
    return {"message": "删除成功"}

# ==================== 收入类别 ====================
@router.post("/shouru-leibie", response_model=ShouruLeibieResponse, summary="创建收入类别")
async def create_shouru_leibie(
    leibie_data: ShouruLeibieCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:create"))
):
    """创建收入类别"""
    service = CaiwuShezhiService(db)
    return service.create_shouru_leibie(leibie_data, current_user.id)

@router.get("/shouru-leibie", response_model=ShouruLeibieListResponse, summary="获取收入类别列表")
async def get_shouru_leibie_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取收入类别列表"""
    service = CaiwuShezhiService(db)
    return service.get_shouru_leibie_list(page, size)

@router.put("/shouru-leibie/{leibie_id}", response_model=ShouruLeibieResponse, summary="更新收入类别")
async def update_shouru_leibie(
    leibie_id: str,
    leibie_data: ShouruLeibieUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:update"))
):
    """更新收入类别"""
    service = CaiwuShezhiService(db)
    return service.update_shouru_leibie(leibie_id, leibie_data, current_user.id)

@router.delete("/shouru-leibie/{leibie_id}", summary="删除收入类别")
async def delete_shouru_leibie(
    leibie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:delete"))
):
    """删除收入类别"""
    service = CaiwuShezhiService(db)
    service.delete_shouru_leibie(leibie_id)
    return {"message": "删除成功"}

# ==================== 报销类别 ====================
@router.post("/baoxiao-leibie", response_model=BaoxiaoLeibieResponse, summary="创建报销类别")
async def create_baoxiao_leibie(
    leibie_data: BaoxiaoLeibieCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:create"))
):
    """创建报销类别"""
    service = CaiwuShezhiService(db)
    return service.create_baoxiao_leibie(leibie_data, current_user.id)

@router.get("/baoxiao-leibie", response_model=BaoxiaoLeibieListResponse, summary="获取报销类别列表")
async def get_baoxiao_leibie_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(100, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取报销类别列表"""
    service = CaiwuShezhiService(db)
    return service.get_baoxiao_leibie_list(page, size)

@router.put("/baoxiao-leibie/{leibie_id}", response_model=BaoxiaoLeibieResponse, summary="更新报销类别")
async def update_baoxiao_leibie(
    leibie_id: str,
    leibie_data: BaoxiaoLeibieUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:update"))
):
    """更新报销类别"""
    service = CaiwuShezhiService(db)
    return service.update_baoxiao_leibie(leibie_id, leibie_data, current_user.id)

@router.delete("/baoxiao-leibie/{leibie_id}", summary="删除报销类别")
async def delete_baoxiao_leibie(
    leibie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:delete"))
):
    """删除报销类别"""
    service = CaiwuShezhiService(db)
    service.delete_baoxiao_leibie(leibie_id)
    return {"message": "删除成功"}

# ==================== 支出类别 ====================
@router.post("/zhichu-leibie", response_model=ZhichuLeibieResponse, summary="创建支出类别")
async def create_zhichu_leibie(
    leibie_data: ZhichuLeibieCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:create"))
):
    """创建支出类别"""
    service = CaiwuShezhiService(db)
    return service.create_zhichu_leibie(leibie_data, current_user.id)

@router.get("/zhichu-leibie", response_model=ZhichuLeibieListResponse, summary="获取支出类别列表")
async def get_zhichu_leibie_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(200, ge=1, le=500, description="每页数量"),
    fenlei: Optional[str] = Query(None, description="分类"),
    db: Session = Depends(get_db)
):
    """获取支出类别列表"""
    service = CaiwuShezhiService(db)
    return service.get_zhichu_leibie_list(page, size, fenlei)

@router.put("/zhichu-leibie/{leibie_id}", response_model=ZhichuLeibieResponse, summary="更新支出类别")
async def update_zhichu_leibie(
    leibie_id: str,
    leibie_data: ZhichuLeibieUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:update"))
):
    """更新支出类别"""
    service = CaiwuShezhiService(db)
    return service.update_zhichu_leibie(leibie_id, leibie_data, current_user.id)

@router.delete("/zhichu-leibie/{leibie_id}", summary="删除支出类别")
async def delete_zhichu_leibie(
    leibie_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("finance_settings:delete"))
):
    """删除支出类别"""
    service = CaiwuShezhiService(db)
    service.delete_zhichu_leibie(leibie_id)
    return {"message": "删除成功"}
