"""
开票申请管理API端点
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.caiwu_guanli.kaipiao_service import KaipiaoService
from schemas.caiwu_guanli.kaipiao_schemas import (
    KaipiaoShenqingCreate,
    KaipiaoShenqingUpdate,
    KaipiaoShenqingResponse,
    KaipiaoShenqingListResponse,
    KaipiaoShenqingListParams,
    KaipiaoAuditRequest,
    KaipiaoProcessRequest,
    KaipiaoStatistics
)

router = APIRouter()


@router.post("/", response_model=KaipiaoShenqingResponse, summary="创建开票申请")
async def create_kaipiao_shenqing(
    shenqing_data: KaipiaoShenqingCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:create"))
):
    """
    创建新的开票申请
    
    - **kehu_id**: 客户ID（必填）
    - **kaipiao_leixing**: 开票类型（必填）
    - **kaipiao_mingcheng**: 开票名称（必填）
    - **kaipiao_jine**: 开票金额（必填）
    - **gouwu_fang_mingcheng**: 购物方名称（必填）
    - **xiaoshou_fang_mingcheng**: 销售方名称（必填）
    - **xiaoshou_fang_shuihao**: 销售方税号（必填）
    """
    service = KaipiaoService(db)
    return service.create_kaipiao_shenqing(shenqing_data, current_user.id)


@router.get("/", response_model=KaipiaoShenqingListResponse, summary="获取开票申请列表")
async def get_kaipiao_shenqing_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    hetong_id: str = Query(None, description="合同ID"),
    kehu_id: str = Query(None, description="客户ID"),
    kaipiao_leixing: str = Query(None, description="开票类型"),
    shenqing_zhuangtai: str = Query(None, description="申请状态"),
    kaipiao_zhuangtai: str = Query(None, description="开票状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:read"))
):
    """
    获取开票申请列表
    
    支持分页、搜索和筛选
    """
    params = KaipiaoShenqingListParams(
        page=page,
        size=size,
        search=search,
        hetong_id=hetong_id,
        kehu_id=kehu_id,
        kaipiao_leixing=kaipiao_leixing,
        shenqing_zhuangtai=shenqing_zhuangtai,
        kaipiao_zhuangtai=kaipiao_zhuangtai
    )
    service = KaipiaoService(db)
    return service.get_kaipiao_shenqing_list(params)


@router.get("/{shenqing_id}", response_model=KaipiaoShenqingResponse, summary="获取开票申请详情")
async def get_kaipiao_shenqing_detail(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:read"))
):
    """
    根据ID获取开票申请详情
    """
    service = KaipiaoService(db)
    return service.get_kaipiao_shenqing_by_id(shenqing_id)


@router.put("/{shenqing_id}", response_model=KaipiaoShenqingResponse, summary="更新开票申请")
async def update_kaipiao_shenqing(
    shenqing_id: str,
    shenqing_data: KaipiaoShenqingUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:update"))
):
    """
    更新开票申请信息
    
    只有草稿和已提交状态的申请可以修改
    """
    service = KaipiaoService(db)
    return service.update_kaipiao_shenqing(shenqing_id, shenqing_data, current_user.id)


@router.post("/{shenqing_id}/submit", response_model=KaipiaoShenqingResponse, summary="提交开票申请")
async def submit_kaipiao_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:submit"))
):
    """
    提交开票申请
    
    将草稿状态的申请提交审核
    """
    service = KaipiaoService(db)
    return service.submit_kaipiao_shenqing(shenqing_id, current_user.id)


@router.post("/audit", response_model=KaipiaoShenqingResponse, summary="审核开票申请")
async def audit_kaipiao_shenqing(
    audit_request: KaipiaoAuditRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:audit"))
):
    """
    审核开票申请
    
    - **shenqing_id**: 申请ID
    - **shenhe_jieguo**: 审核结果（approved/rejected）
    - **shenhe_yijian**: 审核意见
    """
    service = KaipiaoService(db)
    return service.audit_kaipiao_shenqing(
        audit_request.shenqing_id,
        audit_request.shenhe_jieguo,
        audit_request.shenhe_yijian,
        current_user.id
    )


@router.post("/process", response_model=KaipiaoShenqingResponse, summary="处理开票")
async def process_invoice(
    process_request: KaipiaoProcessRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:process"))
):
    """
    处理开票
    
    - **shenqing_id**: 申请ID
    - **fapiao_hao**: 发票号码
    - **fapiao_daima**: 发票代码
    - **fapiao_wenjian_lujing**: 发票文件路径（可选）
    """
    service = KaipiaoService(db)
    return service.process_invoice(
        process_request.shenqing_id,
        process_request.fapiao_hao,
        process_request.fapiao_daima,
        process_request.fapiao_wenjian_lujing,
        current_user.id
    )


@router.get("/statistics/overview", response_model=KaipiaoStatistics, summary="获取开票统计信息")
async def get_kaipiao_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:read"))
):
    """
    获取开票统计信息
    
    包括各状态申请数量和金额统计
    """
    service = KaipiaoService(db)
    return service.get_kaipiao_statistics()


@router.get("/pending/my", response_model=KaipiaoShenqingListResponse, summary="获取我的待处理开票申请")
async def get_my_pending_invoices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户创建的待处理开票申请
    """
    params = KaipiaoShenqingListParams(
        page=page,
        size=size,
        shenqing_zhuangtai="submitted"  # 只显示已提交的申请
    )
    
    service = KaipiaoService(db)
    result = service.get_kaipiao_shenqing_list(params)
    
    # 过滤出当前用户创建的申请
    user_items = [item for item in result.items if item.created_by == current_user.id]
    
    return KaipiaoShenqingListResponse(
        items=user_items,
        total=len(user_items),
        page=params.page,
        size=params.size,
        pages=(len(user_items) + params.size - 1) // params.size
    )


@router.get("/audit/pending", response_model=KaipiaoShenqingListResponse, summary="获取待审核开票申请")
async def get_pending_audit_invoices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:audit"))
):
    """
    获取待审核的开票申请列表
    """
    params = KaipiaoShenqingListParams(
        page=page,
        size=size,
        shenqing_zhuangtai="submitted"
    )
    service = KaipiaoService(db)
    return service.get_kaipiao_shenqing_list(params)


@router.get("/process/pending", response_model=KaipiaoShenqingListResponse, summary="获取待开票申请")
async def get_pending_process_invoices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:process"))
):
    """
    获取待开票的申请列表
    """
    params = KaipiaoShenqingListParams(
        page=page,
        size=size,
        shenqing_zhuangtai="approved"
    )
    service = KaipiaoService(db)
    return service.get_kaipiao_shenqing_list(params)


@router.delete("/{shenqing_id}", summary="删除开票申请")
async def delete_kaipiao_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("invoice:delete"))
):
    """
    删除开票申请（软删除）
    
    只有草稿状态的申请可以删除
    """
    service = KaipiaoService(db)
    kaipiao_shenqing = service.get_kaipiao_shenqing_by_id(shenqing_id)
    
    if kaipiao_shenqing.shenqing_zhuangtai != "draft":
        raise HTTPException(status_code=400, detail="只有草稿状态的申请可以删除")
    
    # 软删除
    from models.caiwu_guanli import KaipiaoShenqing
    kaipiao_obj = db.query(KaipiaoShenqing).filter(KaipiaoShenqing.id == shenqing_id).first()
    kaipiao_obj.is_deleted = "Y"
    kaipiao_obj.updated_by = current_user.id
    kaipiao_obj.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "开票申请已删除"}
