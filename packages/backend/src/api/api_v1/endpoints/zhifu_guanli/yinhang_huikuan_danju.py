"""
银行汇款单据API
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

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


class UploadVoucherRequest(BaseModel):
    """上传凭证请求"""
    voucher_url: str = Field(..., description="凭证图片URL")
    beizhu: Optional[str] = Field(None, description="备注")
    # 汇款信息字段（业务员根据凭证填写）
    huikuan_ren: str = Field(..., description="汇款人姓名")
    huikuan_yinhang: str = Field(..., description="汇款银行")
    huikuan_zhanghu: Optional[str] = Field(None, description="汇款账户")
    huikuan_riqi: str = Field(..., description="汇款日期")

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
    hetong_id: str = None,
    shenhe_zhuangtai: str = None,
    huikuan_yinhang: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取汇款单据列表"""
    service = YinhangHuikuanDanjuService(db)
    return service.get_yinhang_huikuan_danju_list(
        page=page,
        size=size,
        hetong_id=hetong_id,
        shenhe_zhuangtai=shenhe_zhuangtai,
        huikuan_yinhang=huikuan_yinhang
    )


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


@router.post("/{danju_id}/upload-voucher", summary="上传汇款凭证")
async def upload_voucher(
    danju_id: str,
    request_data: UploadVoucherRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    业务员上传汇款凭证并填写汇款信息

    - **voucher_url**: 凭证图片URL
    - **huikuan_ren**: 汇款人姓名
    - **huikuan_yinhang**: 汇款银行
    - **huikuan_zhanghu**: 汇款账户（选填）
    - **huikuan_riqi**: 汇款日期
    - **beizhu**: 备注（选填）
    """
    service = YinhangHuikuanDanjuService(db)
    result = service.upload_voucher(
        danju_id=danju_id,
        voucher_url=request_data.voucher_url,
        uploader_id=current_user.id,
        beizhu=request_data.beizhu,
        huikuan_ren=request_data.huikuan_ren,
        huikuan_yinhang=request_data.huikuan_yinhang,
        huikuan_zhanghu=request_data.huikuan_zhanghu,
        huikuan_riqi=request_data.huikuan_riqi
    )

    return result


@router.post("/{danju_id}/audit-voucher", summary="审核汇款凭证")
async def audit_voucher(
    danju_id: str,
    audit_result: str,
    audit_opinion: str,
    actual_amount: float = None,
    arrival_time: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    财务审核汇款凭证

    - **audit_result**: 审核结果（approved/rejected）
    - **audit_opinion**: 审核意见
    - **actual_amount**: 实际到账金额
    - **arrival_time**: 到账时间
    """
    from datetime import datetime

    service = YinhangHuikuanDanjuService(db)

    # 转换到账时间
    arrival_datetime = None
    if arrival_time:
        arrival_datetime = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))

    result = service.audit_voucher(
        danju_id,
        audit_result,
        audit_opinion,
        current_user.id,
        actual_amount,
        arrival_datetime
    )

    return result


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
