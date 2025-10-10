"""
支付订单审核API端点
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.security.jwt_handler import get_current_user
from core.security.audit_permissions import require_audit_permission, require_amount_approval_authority
from models.yonghu_guanli import Yonghu
from services.shenhe_guanli.payment_audit_service import PaymentAuditService

router = APIRouter()


class PaymentAuditTriggerRequest(BaseModel):
    """触发支付审核请求模型"""
    payment_order_id: str = Field(..., description="支付订单ID")
    trigger_reason: Optional[str] = Field(None, description="触发原因")


class PaymentApprovalRequest(BaseModel):
    """支付审批请求模型"""
    audit_record_id: str = Field(..., description="审核记录ID")
    approval_comment: Optional[str] = Field(None, description="审批意见")
    approval_data: Optional[Dict[str, Any]] = Field(None, description="审批数据")


class PaymentRejectionRequest(BaseModel):
    """支付拒绝请求模型"""
    audit_record_id: str = Field(..., description="审核记录ID")
    rejection_reason: str = Field(..., description="拒绝原因")


class FlowAuditTriggerRequest(BaseModel):
    """触发流水审核请求模型"""
    flow_id: str = Field(..., description="支付流水ID")
    trigger_reason: Optional[str] = Field(None, description="触发原因")


class FlowApprovalRequest(BaseModel):
    """流水审批请求模型"""
    audit_record_id: str = Field(..., description="审核记录ID")
    approval_comment: Optional[str] = Field(None, description="审批意见")
    approval_data: Optional[Dict[str, Any]] = Field(None, description="审批数据")


class FlowRejectionRequest(BaseModel):
    """流水拒绝请求模型"""
    audit_record_id: str = Field(..., description="审核记录ID")
    rejection_reason: str = Field(..., description="拒绝原因")


@router.post("/trigger", summary="触发支付订单审核")
@require_audit_permission("audit_record:create")
async def trigger_payment_audit(
    request: PaymentAuditTriggerRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    触发支付订单审核流程
    
    - **payment_order_id**: 支付订单ID
    - **trigger_reason**: 触发原因（可选）
    """
    try:
        service = PaymentAuditService(db)
        result = service.trigger_payment_audit(
            payment_order_id=request.payment_order_id,
            trigger_user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发支付审核失败: {str(e)}")


@router.post("/approve", summary="审批支付订单")
@require_audit_permission("approval:approve")
async def approve_payment(
    request: PaymentApprovalRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审批通过支付订单
    
    - **audit_record_id**: 审核记录ID
    - **approval_comment**: 审批意见
    - **approval_data**: 审批数据
    """
    try:
        service = PaymentAuditService(db)
        result = service.approve_payment(
            audit_record_id=request.audit_record_id,
            approver_id=current_user.id,
            approval_comment=request.approval_comment,
            approval_data=request.approval_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"支付审批失败: {str(e)}")


@router.post("/reject", summary="拒绝支付订单")
@require_audit_permission("approval:reject")
async def reject_payment(
    request: PaymentRejectionRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    拒绝支付订单
    
    - **audit_record_id**: 审核记录ID
    - **rejection_reason**: 拒绝原因
    """
    try:
        service = PaymentAuditService(db)
        result = service.reject_payment(
            audit_record_id=request.audit_record_id,
            approver_id=current_user.id,
            rejection_reason=request.rejection_reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"支付拒绝失败: {str(e)}")


@router.get("/status/{payment_order_id}", summary="获取支付订单审核状态")
@require_audit_permission("audit_record:read")
async def get_payment_audit_status(
    payment_order_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支付订单的审核状态
    
    - **payment_order_id**: 支付订单ID
    """
    try:
        service = PaymentAuditService(db)
        result = service.get_payment_audit_status(payment_order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核状态失败: {str(e)}")


@router.get("/pending/my", summary="获取我的待审批支付订单")
@require_audit_permission("audit_record:read")
async def get_my_pending_payment_audits(
    page: int = 1,
    size: int = 20,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的待审批支付订单列表"""
    try:
        from models.shenhe_guanli import ShenheJilu
        from models.zhifu_guanli import ZhifuDingdan
        
        # 查询待审批的支付订单
        query = db.query(ShenheJilu).join(ZhifuDingdan, ShenheJilu.yewu_id == ZhifuDingdan.id).filter(
            ShenheJilu.yewu_leixing == "payment_order",
            ShenheJilu.dangqian_shenpi_ren == current_user.id,
            ShenheJilu.shenhe_zhuangtai.in_(["pending", "in_progress"]),
            ShenheJilu.is_deleted == "N"
        )
        
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * size
        records = query.offset(offset).limit(size).all()
        
        # 构建返回数据
        items = []
        for record in records:
            payment_order = db.query(ZhifuDingdan).filter(ZhifuDingdan.id == record.yewu_id).first()
            if payment_order:
                items.append({
                    "audit_record_id": record.id,
                    "payment_order_id": payment_order.id,
                    "order_name": payment_order.dingdan_mingcheng,
                    "payment_amount": float(payment_order.dingdan_jine),
                    "payment_type": payment_order.zhifu_leixing,
                    "audit_status": record.shenhe_zhuangtai,
                    "created_at": record.created_at,
                    "applicant_id": record.shenqing_ren
                })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待审批列表失败: {str(e)}")


@router.get("/history/{payment_order_id}", summary="获取支付订单审核历史")
@require_audit_permission("audit_record:read")
async def get_payment_audit_history(
    payment_order_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支付订单的审核历史记录
    
    - **payment_order_id**: 支付订单ID
    """
    try:
        from models.shenhe_guanli import ShenheJilu, ShenheJiluBuzou
        
        # 获取审核记录
        audit_records = db.query(ShenheJilu).filter(
            ShenheJilu.yewu_id == payment_order_id,
            ShenheJilu.yewu_leixing == "payment_order",
            ShenheJilu.is_deleted == "N"
        ).order_by(ShenheJilu.created_at.desc()).all()
        
        history = []
        for record in audit_records:
            # 获取审核步骤
            steps = db.query(ShenheJiluBuzou).filter(
                ShenheJiluBuzou.shenhe_jilu_id == record.id,
                ShenheJiluBuzou.is_deleted == "N"
            ).order_by(ShenheJiluBuzou.buzou_paixu).all()
            
            step_details = []
            for step in steps:
                step_details.append({
                    "step_order": step.buzou_paixu,
                    "step_name": step.buzou_mingcheng,
                    "approver_id": step.shenpi_ren,
                    "approval_status": step.shenpi_zhuangtai,
                    "approval_comment": step.shenpi_yijian,
                    "approval_time": step.shenpi_shijian,
                    "created_at": step.created_at
                })
            
            history.append({
                "audit_record_id": record.id,
                "audit_status": record.shenhe_zhuangtai,
                "applicant_id": record.shenqing_ren,
                "created_at": record.created_at,
                "completed_at": record.wancheng_shijian,
                "steps": step_details
            })
        
        return {
            "payment_order_id": payment_order_id,
            "audit_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核历史失败: {str(e)}")


@router.post("/batch/trigger", summary="批量触发支付审核")
@require_audit_permission("audit_record:create")
async def batch_trigger_payment_audit(
    payment_order_ids: list[str],
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量触发支付订单审核
    
    - **payment_order_ids**: 支付订单ID列表
    """
    try:
        service = PaymentAuditService(db)
        results = []
        
        for payment_order_id in payment_order_ids:
            try:
                result = service.trigger_payment_audit(
                    payment_order_id=payment_order_id,
                    trigger_user_id=current_user.id
                )
                results.append({
                    "payment_order_id": payment_order_id,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "payment_order_id": payment_order_id,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r["success"]])
        
        return {
            "total_count": len(payment_order_ids),
            "success_count": success_count,
            "failed_count": len(payment_order_ids) - success_count,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量触发审核失败: {str(e)}")


# 支付流水审核相关端点
@router.post("/flow/trigger", summary="触发支付流水审核")
@require_audit_permission("audit_record:create")
async def trigger_flow_audit(
    request: FlowAuditTriggerRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    触发支付流水审核流程

    - **flow_id**: 支付流水ID
    - **trigger_reason**: 触发原因（可选）
    """
    try:
        service = PaymentAuditService(db)
        result = service.trigger_flow_audit(
            flow_id=request.flow_id,
            trigger_user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发流水审核失败: {str(e)}")


@router.post("/flow/approve", summary="审批支付流水")
@require_audit_permission("approval:approve")
async def approve_flow(
    request: FlowApprovalRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审批通过支付流水

    - **audit_record_id**: 审核记录ID
    - **approval_comment**: 审批意见
    - **approval_data**: 审批数据
    """
    try:
        service = PaymentAuditService(db)
        result = service.approve_flow(
            audit_record_id=request.audit_record_id,
            approver_id=current_user.id,
            approval_comment=request.approval_comment,
            approval_data=request.approval_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流水审批失败: {str(e)}")


@router.post("/flow/reject", summary="拒绝支付流水")
@require_audit_permission("approval:reject")
async def reject_flow(
    request: FlowRejectionRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    拒绝支付流水

    - **audit_record_id**: 审核记录ID
    - **rejection_reason**: 拒绝原因
    """
    try:
        service = PaymentAuditService(db)
        result = service.reject_flow(
            audit_record_id=request.audit_record_id,
            approver_id=current_user.id,
            rejection_reason=request.rejection_reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流水拒绝失败: {str(e)}")


@router.get("/flow/status/{flow_id}", summary="获取支付流水审核状态")
@require_audit_permission("audit_record:read")
async def get_flow_audit_status(
    flow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支付流水的审核状态

    - **flow_id**: 支付流水ID
    """
    try:
        service = PaymentAuditService(db)
        result = service.get_flow_audit_status(flow_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取流水审核状态失败: {str(e)}")


@router.get("/flow/pending/my", summary="获取我的待审批支付流水")
@require_audit_permission("audit_record:read")
async def get_my_pending_flow_audits(
    page: int = 1,
    size: int = 20,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的待审批支付流水列表"""
    try:
        from models.shenhe_guanli import ShenheJilu
        from models.zhifu_guanli import ZhifuLiushui

        # 查询待审批的支付流水
        query = db.query(ShenheJilu).join(ZhifuLiushui, ShenheJilu.yewu_id == ZhifuLiushui.id).filter(
            ShenheJilu.yewu_leixing == "payment_flow",
            ShenheJilu.dangqian_shenpi_ren == current_user.id,
            ShenheJilu.shenhe_zhuangtai.in_(["pending", "in_progress"]),
            ShenheJilu.is_deleted == "N"
        )

        total = query.count()

        # 分页查询
        offset = (page - 1) * size
        records = query.offset(offset).limit(size).all()

        # 构建返回数据
        items = []
        for record in records:
            payment_flow = db.query(ZhifuLiushui).filter(ZhifuLiushui.id == record.yewu_id).first()
            if payment_flow:
                items.append({
                    "audit_record_id": record.id,
                    "flow_id": payment_flow.id,
                    "flow_number": payment_flow.liushui_bianhao,
                    "transaction_amount": float(payment_flow.jiaoyijine),
                    "flow_type": payment_flow.liushui_leixing,
                    "payment_method": payment_flow.zhifu_fangshi,
                    "audit_status": record.shenhe_zhuangtai,
                    "created_at": record.created_at,
                    "applicant_id": record.shenqing_ren
                })

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待审批流水列表失败: {str(e)}")
