"""
审核记录 API 端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.security.permissions import check_permission
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu

router = APIRouter()


class AuditActionRequest(BaseModel):
    """审核操作请求模型"""
    comment: Optional[str] = Field(None, description="审核意见")
    approver: Optional[str] = Field(None, description="审核人")

@router.get("/my-processed")
@check_permission("audit:read")
async def get_my_processed_audits(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我已处理的审核任务"""
    try:
        from models.shenhe_guanli.shenhe_jilu import ShenheJilu
        from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
        from models.hetong_guanli.hetong import Hetong
        from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
        from models.xiansuo_guanli.xiansuo import Xiansuo

        # 查询我已处理的审核记录
        records = db.query(ShenheJilu).filter(
            ShenheJilu.shenhe_ren_id == current_user.id,
            ShenheJilu.jilu_zhuangtai == "yichuli",
            ShenheJilu.is_deleted == "N"
        ).order_by(ShenheJilu.shenhe_shijian.desc()).limit(50).all()

        result = []
        for record in records:
            workflow = record.shenhe_liucheng

            # 查询关联对象信息
            related_info = None
            if workflow.guanlian_id:
                # 尝试作为合同ID查询
                hetong = db.query(Hetong).filter(
                    Hetong.id == workflow.guanlian_id,
                    Hetong.is_deleted == "N"
                ).first()

                if hetong:
                    related_info = {
                        "id": hetong.id,
                        "name": hetong.hetong_bianhao or hetong.hetong_mingcheng,
                        "type": "contract"
                    }
                else:
                    # 尝试作为报价ID查询
                    baojia = db.query(XiansuoBaojia).filter(
                        XiansuoBaojia.id == workflow.guanlian_id,
                        XiansuoBaojia.is_deleted == "N"
                    ).first()

                    if baojia:
                        xiansuo = db.query(Xiansuo).filter(
                            Xiansuo.id == baojia.xiansuo_id,
                            Xiansuo.is_deleted == "N"
                        ).first()

                        company_name = xiansuo.gongsi_mingcheng if xiansuo else "未知公司"
                        related_info = {
                            "id": baojia.id,
                            "name": f"{company_name} - 报价 ¥{baojia.zongji_jine}",
                            "type": "quote"
                        }

            result.append({
                "id": record.id,
                "step_id": record.id,
                "workflow_id": workflow.id,
                "workflow_number": workflow.liucheng_bianhao,
                "audit_type": workflow.shenhe_leixing,
                "step_name": record.buzhou_mingcheng,
                "applicant_reason": workflow.shenqing_yuanyin,
                "related_info": related_info,
                "shenhe_jieguo": record.shenhe_jieguo,
                "shenhe_yijian": record.shenhe_yijian,
                "shenhe_shijian": record.shenhe_shijian.isoformat() if record.shenhe_shijian else None,
                "created_at": record.created_at.isoformat() if record.created_at else None
            })

        return {"items": result, "total": len(result)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取已处理任务失败: {str(e)}")


@router.get("/statistics/my")
@check_permission("audit:read")
async def get_my_audit_statistics(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的审核统计信息"""
    try:
        # 模拟统计数据
        statistics = {
            "pending_count": 3,  # 待审核数量
            "approved_count": 15,  # 已通过数量
            "rejected_count": 2,  # 已拒绝数量
            "total_count": 20,  # 总数量
            "this_week": {
                "pending": 3,
                "approved": 8,
                "rejected": 1
            },
            "this_month": {
                "pending": 3,
                "approved": 15,
                "rejected": 2
            },
            "by_type": {
                "contract_audit": {
                    "pending": 1,
                    "approved": 8,
                    "rejected": 1
                },
                "quote_audit": {
                    "pending": 1,
                    "approved": 5,
                    "rejected": 0
                },
                "discount_audit": {
                    "pending": 1,
                    "approved": 2,
                    "rejected": 1
                }
            }
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核统计失败: {str(e)}")

@router.get("/")
@check_permission("audit:read")
async def get_audit_records(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None)
):
    """获取审核记录列表"""
    try:
        # 模拟审核记录数据
        mock_records = [
            {
                "id": "rec-1",
                "audit_id": "audit-1",
                "title": "合同金额修改审核",
                "type": "contract_audit",
                "status": "approved",
                "applicant": "张三",
                "applicant_id": "user-1",
                "approver": "李经理",
                "approver_id": "user-2",
                "created_at": "2024-01-15T10:30:00",
                "processed_at": "2024-01-15T14:20:00",
                "comment": "金额调整合理，同意修改",
                "priority": "high"
            },
            {
                "id": "rec-2",
                "audit_id": "audit-2",
                "title": "报价单审核",
                "type": "quote_audit",
                "status": "pending",
                "applicant": "李四",
                "applicant_id": "user-3",
                "approver": "王经理",
                "approver_id": "user-4",
                "created_at": "2024-01-15T09:15:00",
                "processed_at": None,
                "comment": None,
                "priority": "medium"
            },
            {
                "id": "rec-3",
                "audit_id": "audit-3",
                "title": "特殊折扣申请",
                "type": "discount_audit",
                "status": "rejected",
                "applicant": "王五",
                "applicant_id": "user-5",
                "approver": "赵总",
                "approver_id": "user-6",
                "created_at": "2024-01-14T16:45:00",
                "processed_at": "2024-01-15T08:30:00",
                "comment": "折扣幅度过大，不予批准",
                "priority": "low"
            }
        ]
        
        # 状态过滤
        if status:
            mock_records = [rec for rec in mock_records if rec["status"] == status]
        
        # 类型过滤
        if audit_type:
            mock_records = [rec for rec in mock_records if rec["type"] == audit_type]
        
        # 分页
        start = (page - 1) * size
        end = start + size
        paginated_records = mock_records[start:end]
        
        return {
            "items": paginated_records,
            "total": len(mock_records),
            "page": page,
            "size": size,
            "pages": (len(mock_records) + size - 1) // size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核记录失败: {str(e)}")

@router.post("/{record_id}/approve")
@check_permission("audit:process")
async def approve_audit(
    record_id: str,
    request: AuditActionRequest = Body(...),
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审核通过"""
    try:
        from models.shenhe_guanli.shenhe_jilu import ShenheJilu
        from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
        from datetime import datetime

        comment = request.comment

        # 1. 查询审核记录
        record = db.query(ShenheJilu).filter(
            ShenheJilu.id == record_id,
            ShenheJilu.is_deleted == "N"
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="审核记录不存在")

        # 2. 验证审核人权限
        if record.shenhe_ren_id != current_user.id:
            raise HTTPException(status_code=403, detail="您没有权限审核此任务")

        # 3. 更新审核记录
        record.jilu_zhuangtai = "yichuli"
        record.shenhe_jieguo = "tongguo"
        record.shenhe_yijian = comment or "审核通过"
        record.shenhe_shijian = datetime.now()
        record.updated_at = datetime.now()

        # 4. 更新审核流程状态
        workflow = record.shenhe_liucheng
        workflow.shenhe_zhuangtai = "yitongguo"
        workflow.wancheng_shijian = datetime.now()
        workflow.updated_at = datetime.now()

        # 5. 如果是合同审核，更新合同状态
        if workflow.shenhe_leixing == "hetong_jine_xiuzheng":
            from models.hetong_guanli.hetong import Hetong

            # 查询关联的合同
            hetong = db.query(Hetong).filter(
                Hetong.id == workflow.guanlian_id,
                Hetong.is_deleted == "N"
            ).first()

            if hetong:
                # 更新合同状态为生效
                hetong.hetong_zhuangtai = "active"
                hetong.updated_at = datetime.now()
                print(f"✅ 审核通过，合同 {hetong.hetong_bianhao} 状态更新为 active")

        db.commit()

        result = {
            "id": record_id,
            "status": "approved",
            "approver": current_user.yonghu_ming,
            "approver_id": current_user.id,
            "processed_at": datetime.now().isoformat(),
            "comment": comment or "审核通过"
        }

        return {"message": "审核通过", "data": result}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"审核通过操作失败: {str(e)}")

@router.post("/{record_id}/reject")
@check_permission("audit:process")
async def reject_audit(
    record_id: str,
    request: AuditActionRequest = Body(...),
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审核拒绝"""
    try:
        from models.shenhe_guanli.shenhe_jilu import ShenheJilu
        from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
        from datetime import datetime

        comment = request.comment or "审核拒绝"

        # 1. 查询审核记录
        record = db.query(ShenheJilu).filter(
            ShenheJilu.id == record_id,
            ShenheJilu.is_deleted == "N"
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="审核记录不存在")

        # 2. 验证审核人权限
        if record.shenhe_ren_id != current_user.id:
            raise HTTPException(status_code=403, detail="您没有权限审核此任务")

        # 3. 更新审核记录
        record.jilu_zhuangtai = "yichuli"
        record.shenhe_jieguo = "bohui"
        record.shenhe_yijian = comment
        record.shenhe_shijian = datetime.now()
        record.updated_at = datetime.now()

        # 4. 更新审核流程状态
        workflow = record.shenhe_liucheng
        workflow.shenhe_zhuangtai = "yibohui"
        workflow.wancheng_shijian = datetime.now()
        workflow.updated_at = datetime.now()

        # 5. 如果是合同审核，软删除合同
        if workflow.shenhe_leixing == "hetong_jine_xiuzheng":
            from models.hetong_guanli.hetong import Hetong

            # 查询关联的合同
            hetong = db.query(Hetong).filter(
                Hetong.id == workflow.guanlian_id,
                Hetong.is_deleted == "N"
            ).first()

            if hetong:
                # 审核拒绝，软删除合同（不再显示在列表中）
                hetong.is_deleted = "Y"
                hetong.hetong_zhuangtai = "rejected"  # 保留状态记录
                hetong.updated_at = datetime.now()
                print(f"❌ 审核拒绝，合同 {hetong.hetong_bianhao} 已删除（软删除）")

        db.commit()

        result = {
            "id": record_id,
            "status": "rejected",
            "approver": current_user.yonghu_ming,
            "approver_id": current_user.id,
            "processed_at": datetime.now().isoformat(),
            "comment": comment
        }

        return {"message": "审核拒绝", "data": result}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"审核拒绝操作失败: {str(e)}")

@router.post("/{record_id}/transfer")
@check_permission("audit:process")
async def transfer_audit(
    record_id: str,
    target_user_id: str,
    comment: Optional[str] = None,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """转派审核"""
    try:
        # 模拟转派操作
        result = {
            "id": record_id,
            "status": "transferred",
            "from_user": current_user.yonghu_ming,
            "from_user_id": current_user.id,
            "to_user_id": target_user_id,
            "transferred_at": "2024-01-15T15:30:00",
            "comment": comment or "审核转派"
        }
        
        return {"message": "审核转派成功", "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审核转派操作失败: {str(e)}")

@router.get("/{record_id}")
@check_permission("audit:read")
async def get_audit_record(
    record_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个审核记录详情"""
    try:
        # 模拟获取审核记录详情
        record = {
            "id": record_id,
            "audit_id": "audit-1",
            "title": "合同金额修改审核",
            "type": "contract_audit",
            "status": "approved",
            "applicant": "张三",
            "applicant_id": "user-1",
            "approver": "李经理",
            "approver_id": "user-2",
            "created_at": "2024-01-15T10:30:00",
            "processed_at": "2024-01-15T14:20:00",
            "comment": "金额调整合理，同意修改",
            "priority": "high",
            "details": {
                "original_amount": 10000,
                "new_amount": 8000,
                "reason": "客户预算调整",
                "contract_id": "contract-123"
            },
            "workflow": {
                "id": "wf-1",
                "name": "合同审核流程",
                "current_step": 2,
                "total_steps": 3
            }
        }
        
        return record
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核记录详情失败: {str(e)}")
