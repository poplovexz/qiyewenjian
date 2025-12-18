"""
报销申请管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.bangong_guanli.baoxiao_service import BaoxiaoService
from schemas.bangong_guanli.baoxiao_schemas import (
    BaoxiaoShenqingCreate,
    BaoxiaoShenqingUpdate,
    BaoxiaoShenqingResponse,
    BaoxiaoShenqingListParams
)

router = APIRouter()


@router.post("/", response_model=BaoxiaoShenqingResponse, summary="创建报销申请")
async def create_baoxiao_shenqing(
    shenqing_data: BaoxiaoShenqingCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    创建报销申请

    移动端和PC端都可以访问，只需要登录即可

    - **baoxiao_leixing**: 报销类型
    - **baoxiao_jine**: 报销金额
    - **baoxiao_shijian**: 报销事项发生时间
    - **baoxiao_yuanyin**: 报销原因说明
    - **fujian_lujing**: 附件路径（可选）
    - **beizhu**: 备注（可选）
    """
    service = BaoxiaoService(db)
    return service.create_baoxiao_shenqing(shenqing_data, current_user.id)


@router.get("/", response_model=dict, summary="获取报销申请列表")
async def get_baoxiao_shenqing_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    shenhe_zhuangtai: str = Query(None, description="审核状态筛选"),
    baoxiao_leixing: str = Query(None, description="报销类型筛选"),
    shenqing_ren_id: str = Query(None, description="申请人ID筛选"),
    search: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取报销申请列表

    移动端和PC端都可以访问，只需要登录即可
    支持分页、筛选和搜索
    """
    params = BaoxiaoShenqingListParams(
        page=page,
        size=size,
        shenhe_zhuangtai=shenhe_zhuangtai,
        baoxiao_leixing=baoxiao_leixing,
        shenqing_ren_id=shenqing_ren_id,
        search=search
    )
    
    service = BaoxiaoService(db)
    items, total = service.get_baoxiao_shenqing_list(params, current_user.id)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/my", response_model=dict, summary="获取我的报销申请列表")
async def get_my_baoxiao_shenqing_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    shenhe_zhuangtai: str = Query(None, description="审核状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("office:baoxiao:read"))
):
    """
    获取当前用户的报销申请列表
    """
    params = BaoxiaoShenqingListParams(
        page=page,
        size=size,
        shenhe_zhuangtai=shenhe_zhuangtai,
        shenqing_ren_id=current_user.id
    )
    
    service = BaoxiaoService(db)
    items, total = service.get_baoxiao_shenqing_list(params, current_user.id)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{shenqing_id}", response_model=BaoxiaoShenqingResponse, summary="获取报销申请详情")
async def get_baoxiao_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    根据ID获取报销申请详情

    移动端和PC端都可以访问，只需要登录即可
    """
    service = BaoxiaoService(db)
    return service.get_baoxiao_shenqing_by_id(shenqing_id)


@router.put("/{shenqing_id}", response_model=BaoxiaoShenqingResponse, summary="更新报销申请")
async def update_baoxiao_shenqing(
    shenqing_id: str,
    update_data: BaoxiaoShenqingUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    更新报销申请

    移动端和PC端都可以访问，只需要登录即可
    只有待审核状态的申请才能修改
    """
    service = BaoxiaoService(db)
    return service.update_baoxiao_shenqing(shenqing_id, update_data, current_user.id)


@router.delete("/{shenqing_id}", summary="删除报销申请")
async def delete_baoxiao_shenqing(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    删除报销申请（软删除）

    移动端和PC端都可以访问，只需要登录即可
    只有待审核状态的申请才能删除
    """
    service = BaoxiaoService(db)
    return service.delete_baoxiao_shenqing(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/submit", summary="提交审批")
async def submit_baoxiao_for_approval(
    shenqing_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    提交报销申请进行审批

    移动端和PC端都可以访问，只需要登录即可
    """
    service = BaoxiaoService(db)
    return service.submit_for_approval(shenqing_id, current_user.id)


@router.post("/{shenqing_id}/approve", summary="审批通过")
async def approve_baoxiao_shenqing(
    shenqing_id: str,
    shenhe_yijian: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    审批通过报销申请

    移动端和PC端都可以访问，只需要登录即可
    """
    service = BaoxiaoService(db)
    return service.approve_application(shenqing_id, current_user.id, shenhe_yijian)


@router.post("/{shenqing_id}/reject", summary="审批拒绝")
async def reject_baoxiao_shenqing(
    shenqing_id: str,
    shenhe_yijian: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    审批拒绝报销申请

    移动端和PC端都可以访问，只需要登录即可
    """
    service = BaoxiaoService(db)
    return service.reject_application(shenqing_id, current_user.id, shenhe_yijian)

