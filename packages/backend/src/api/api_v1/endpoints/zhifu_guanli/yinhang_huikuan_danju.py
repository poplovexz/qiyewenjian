"""
银行汇款单据API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from services.zhifu_guanli.yinhang_huikuan_danju_service import YinhangHuikuanDanjuService
from schemas.zhifu_guanli import (
    YinhangHuikuanDanjuCreate,
    YinhangHuikuanDanjuUpdate,
    YinhangHuikuanDanjuListParams,
    HuikuanDanjuAuditRequest
)

router = APIRouter()


@router.post("/", summary="上传银行汇款单据")
async def upload_huikuan_danju(
    danju_data: YinhangHuikuanDanjuCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    上传银行汇款单据
    
    - **hetong_zhifu_id**: 合同支付ID（必填）
    - **danju_lujing**: 单据文件路径（必填）
    - **huikuan_jine**: 汇款金额（必填）
    - **huikuan_riqi**: 汇款日期（必填）
    - **huikuan_ren**: 汇款人（必填）
    """
    service = YinhangHuikuanDanjuService(db)
    result = service.create_huikuan_danju(danju_data, current_user.id)
    
    return {
        "success": True,
        "message": "汇款单据上传成功",
        "data": result
    }


@router.get("/", summary="获取汇款单据列表")
async def get_huikuan_danju_list(
    page: int = 1,
    size: int = 20,
    hetong_zhifu_id: str = None,
    shenhe_zhuangtai: str = None,
    shangchuan_ren_id: str = None,
    shenhe_ren_id: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取汇款单据列表"""
    params = YinhangHuikuanDanjuListParams(
        page=page,
        size=size,
        hetong_zhifu_id=hetong_zhifu_id,
        shenhe_zhuangtai=shenhe_zhuangtai,
        shangchuan_ren_id=shangchuan_ren_id,
        shenhe_ren_id=shenhe_ren_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = YinhangHuikuanDanjuService(db)
    return service.get_huikuan_danju_list(params)


@router.get("/{danju_id}", summary="获取汇款单据详情")
async def get_huikuan_danju_by_id(
    danju_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取汇款单据详情"""
    service = YinhangHuikuanDanjuService(db)
    result = service.get_huikuan_danju_by_id(danju_id)
    
    return {
        "success": True,
        "data": result
    }


@router.put("/{danju_id}", summary="更新汇款单据")
async def update_huikuan_danju(
    danju_id: str,
    danju_data: YinhangHuikuanDanjuUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新汇款单据"""
    service = YinhangHuikuanDanjuService(db)
    result = service.update_huikuan_danju(danju_id, danju_data, current_user.id)
    
    return {
        "success": True,
        "message": "汇款单据更新成功",
        "data": result
    }


@router.post("/{danju_id}/audit", summary="审核汇款单据")
async def audit_huikuan_danju(
    danju_id: str,
    audit_data: HuikuanDanjuAuditRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    审核汇款单据
    
    - **shenhe_jieguo**: 审核结果（tongguo、jujue）
    - **shenhe_yijian**: 审核意见
    """
    service = YinhangHuikuanDanjuService(db)
    result = service.audit_huikuan_danju(danju_id, audit_data, current_user.id)
    
    return {
        "success": True,
        "message": "汇款单据审核完成",
        "data": result
    }


@router.get("/payment/{hetong_zhifu_id}", summary="根据合同支付ID获取汇款单据")
async def get_danju_by_payment(
    hetong_zhifu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据合同支付ID获取汇款单据"""
    service = YinhangHuikuanDanjuService(db)
    result = service.get_danju_by_payment(hetong_zhifu_id)
    
    return {
        "success": True,
        "data": result
    }


@router.get("/pending-audits/list", summary="获取待审核的汇款单据")
async def get_pending_audit_danju(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取待审核的汇款单据"""
    service = YinhangHuikuanDanjuService(db)
    result = service.get_pending_audit_danju()
    
    return {
        "success": True,
        "data": result
    }


@router.post("/upload-file", summary="上传汇款单据文件")
async def upload_danju_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    上传汇款单据文件
    
    支持的文件格式：PDF、图片（JPG、PNG）
    文件大小限制：10MB
    """
    # 检查文件类型
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/jpg", 
        "image/png"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，请上传PDF或图片文件"
        )
    
    # 检查文件大小（10MB）
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过10MB"
        )
    
    service = YinhangHuikuanDanjuService(db)
    result = service.upload_danju_file(file, current_user.id)
    
    return {
        "success": True,
        "message": "文件上传成功",
        "data": result
    }


@router.get("/statistics/overview", summary="获取汇款单据统计概览")
async def get_danju_statistics(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取汇款单据统计概览"""
    service = YinhangHuikuanDanjuService(db)
    result = service.get_danju_statistics()
    
    return {
        "success": True,
        "data": result
    }
