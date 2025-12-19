"""
成本记录管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.caiwu_guanli.chengben_service import ChengbenService
from schemas.caiwu_guanli.chengben_schemas import (
    ChengbenJiluCreate,
    ChengbenJiluUpdate,
    ChengbenJiluResponse,
    ChengbenJiluListResponse,
    ChengbenJiluListParams,
    ChengbenAuditRequest,
    ChengbenRecordRequest,
    ChengbenStatistics,
    ChengbenAnalysis
)

router = APIRouter()

@router.post("/", response_model=ChengbenJiluResponse, summary="创建成本记录")
async def create_chengben_jilu(
    jilu_data: ChengbenJiluCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:create"))
):
    """
    创建新的成本记录
    
    - **chengben_mingcheng**: 成本名称（必填）
    - **chengben_leixing**: 成本类型（必填）
    - **chengben_fenlei**: 成本分类（必填）
    - **chengben_jine**: 成本金额（必填）
    - **fasheng_shijian**: 发生时间（必填）
    """
    service = ChengbenService(db)
    return service.create_chengben_jilu(jilu_data, current_user.id)

@router.get("/", response_model=ChengbenJiluListResponse, summary="获取成本记录列表")
async def get_chengben_jilu_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    hetong_id: str = Query(None, description="合同ID"),
    xiangmu_id: str = Query(None, description="项目ID"),
    bumen_id: str = Query(None, description="部门ID"),
    chengben_leixing: str = Query(None, description="成本类型"),
    chengben_fenlei: str = Query(None, description="成本分类"),
    shenhe_zhuangtai: str = Query(None, description="审核状态"),
    fapiao_zhuangtai: str = Query(None, description="发票状态"),
    zhuangtai: str = Query(None, description="状态"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:read"))
):
    """
    获取成本记录列表
    
    支持分页、搜索和筛选
    """
    params = ChengbenJiluListParams(
        page=page,
        size=size,
        search=search,
        hetong_id=hetong_id,
        xiangmu_id=xiangmu_id,
        bumen_id=bumen_id,
        chengben_leixing=chengben_leixing,
        chengben_fenlei=chengben_fenlei,
        shenhe_zhuangtai=shenhe_zhuangtai,
        fapiao_zhuangtai=fapiao_zhuangtai,
        zhuangtai=zhuangtai
    )
    service = ChengbenService(db)
    return service.get_chengben_jilu_list(params)

@router.get("/{jilu_id}", response_model=ChengbenJiluResponse, summary="获取成本记录详情")
async def get_chengben_jilu_detail(
    jilu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:read"))
):
    """
    根据ID获取成本记录详情
    """
    service = ChengbenService(db)
    return service.get_chengben_jilu_by_id(jilu_id)

@router.put("/{jilu_id}", response_model=ChengbenJiluResponse, summary="更新成本记录")
async def update_chengben_jilu(
    jilu_id: str,
    jilu_data: ChengbenJiluUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:update"))
):
    """
    更新成本记录信息
    
    只有草稿和已提交状态的记录可以修改
    """
    service = ChengbenService(db)
    return service.update_chengben_jilu(jilu_id, jilu_data, current_user.id)

@router.post("/{jilu_id}/submit", response_model=ChengbenJiluResponse, summary="提交成本记录")
async def submit_chengben_jilu(
    jilu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:submit"))
):
    """
    提交成本记录
    
    将草稿状态的记录提交审核
    """
    service = ChengbenService(db)
    return service.submit_chengben_jilu(jilu_id, current_user.id)

@router.post("/audit", response_model=ChengbenJiluResponse, summary="审核成本记录")
async def audit_chengben_jilu(
    audit_request: ChengbenAuditRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:audit"))
):
    """
    审核成本记录
    
    - **jilu_id**: 记录ID
    - **shenhe_jieguo**: 审核结果（approved/rejected）
    - **shenhe_yijian**: 审核意见
    """
    service = ChengbenService(db)
    return service.audit_chengben_jilu(
        audit_request.jilu_id,
        audit_request.shenhe_jieguo,
        audit_request.shenhe_yijian,
        current_user.id
    )

@router.post("/record", response_model=ChengbenJiluResponse, summary="成本入账")
async def record_chengben(
    record_request: ChengbenRecordRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:record"))
):
    """
    成本入账
    
    - **jilu_id**: 记录ID
    - **shiji_jine**: 实际金额
    - **jizhangjian**: 记账时间（可选）
    - **kuaiji_kemu**: 会计科目（可选）
    - **chengben_zhongxin**: 成本中心（可选）
    """
    service = ChengbenService(db)
    return service.record_chengben(
        record_request.jilu_id,
        record_request.shiji_jine,
        record_request.jizhangjian,
        record_request.kuaiji_kemu,
        record_request.chengben_zhongxin,
        current_user.id
    )

@router.get("/statistics/overview", response_model=ChengbenStatistics, summary="获取成本统计信息")
async def get_chengben_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:read"))
):
    """
    获取成本统计信息
    
    包括各状态记录数量和金额统计
    """
    service = ChengbenService(db)
    return service.get_chengben_statistics()

@router.get("/analysis/overview", response_model=ChengbenAnalysis, summary="获取成本分析")
async def get_chengben_analysis(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:read"))
):
    """
    获取成本分析
    
    包括按类型、分类、部门、项目的分析和趋势分析
    """
    service = ChengbenService(db)
    return service.get_chengben_analysis()

@router.get("/pending/my", response_model=ChengbenJiluListResponse, summary="获取我的待处理成本记录")
async def get_my_pending_costs(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取当前用户创建的待处理成本记录
    """
    params = ChengbenJiluListParams(
        page=page,
        size=size,
        shenhe_zhuangtai="submitted"  # 只显示已提交的记录
    )
    
    service = ChengbenService(db)
    result = service.get_chengben_jilu_list(params)
    
    # 过滤出当前用户创建的记录
    user_items = [item for item in result.items if item.created_by == current_user.id]
    
    return ChengbenJiluListResponse(
        items=user_items,
        total=len(user_items),
        page=params.page,
        size=params.size,
        pages=(len(user_items) + params.size - 1) // params.size
    )

@router.get("/audit/pending", response_model=ChengbenJiluListResponse, summary="获取待审核成本记录")
async def get_pending_audit_costs(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:audit"))
):
    """
    获取待审核的成本记录列表
    """
    params = ChengbenJiluListParams(
        page=page,
        size=size,
        shenhe_zhuangtai="submitted"
    )
    service = ChengbenService(db)
    return service.get_chengben_jilu_list(params)

@router.get("/record/pending", response_model=ChengbenJiluListResponse, summary="获取待入账成本记录")
async def get_pending_record_costs(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:record"))
):
    """
    获取待入账的成本记录列表
    """
    params = ChengbenJiluListParams(
        page=page,
        size=size,
        shenhe_zhuangtai="approved"
    )
    service = ChengbenService(db)
    return service.get_chengben_jilu_list(params)

@router.delete("/{jilu_id}", summary="删除成本记录")
async def delete_chengben_jilu(
    jilu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("cost:delete"))
):
    """
    删除成本记录（软删除）
    
    只有草稿状态的记录可以删除
    """
    service = ChengbenService(db)
    chengben_jilu = service.get_chengben_jilu_by_id(jilu_id)
    
    if chengben_jilu.shenhe_zhuangtai != "draft":
        raise HTTPException(status_code=400, detail="只有草稿状态的记录可以删除")
    
    # 软删除
    from models.caiwu_guanli import ChengbenJilu
    chengben_obj = db.query(ChengbenJilu).filter(ChengbenJilu.id == jilu_id).first()
    chengben_obj.is_deleted = "Y"
    chengben_obj.updated_by = current_user.id
    chengben_obj.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "成本记录已删除"}
