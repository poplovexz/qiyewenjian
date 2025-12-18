"""
审核工作流 API 端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import check_permission
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.shenhe_guanli.audit_workflow_service import AuditWorkflowService
from schemas.shenhe_guanli.audit_workflow_schemas import (
    AuditWorkflowCreate,
    AuditWorkflowUpdate,
    AuditWorkflowResponse,
    AuditWorkflowListParams
)
from typing import Dict, Any

router = APIRouter()

@router.get("/pending/my", response_model=List[dict])
@check_permission("audit:read")
async def get_my_pending_audits(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """获取我的待审核任务"""
    try:
        from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
        from models.shenhe_guanli.shenhe_jilu import ShenheJilu
        from sqlalchemy.orm import joinedload

        # 查询当前用户待审核的记录
        # 1. 查找当前用户作为审核人的待处理审核记录
        pending_records = db.query(ShenheJilu).join(
            ShenheLiucheng, ShenheJilu.liucheng_id == ShenheLiucheng.id
        ).filter(
            ShenheJilu.shenhe_ren_id == current_user.id,
            ShenheJilu.jilu_zhuangtai == "daichuli",
            ShenheJilu.is_deleted == "N",
            ShenheLiucheng.is_deleted == "N"
        ).options(
            joinedload(ShenheJilu.shenhe_liucheng)
        ).order_by(
            ShenheJilu.created_at.desc()
        ).offset((page - 1) * size).limit(size).all()

        # 转换为响应格式
        result = []
        for record in pending_records:
            workflow = record.shenhe_liucheng

            # 获取关联对象信息
            related_info = None
            if workflow.guanlian_id:
                # 根据审核类型查询关联对象
                if workflow.shenhe_leixing == "hetong_jine_xiuzheng":
                    # 合同金额修正审核，关联的可能是合同ID或报价ID
                    # 先尝试作为合同ID查询
                    from models.hetong_guanli.hetong import Hetong
                    hetong = db.query(Hetong).filter(
                        Hetong.id == workflow.guanlian_id,
                        Hetong.is_deleted == "N"
                    ).first()

                    if hetong:
                        related_info = {
                            "id": hetong.id,
                            "name": hetong.hetong_bianhao or hetong.hetong_mingcheng or "未知合同",
                            "type": "contract"
                        }
                    else:
                        # 如果不是合同ID，尝试作为报价ID查询
                        from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
                        baojia = db.query(XiansuoBaojia).filter(
                            XiansuoBaojia.id == workflow.guanlian_id,
                            XiansuoBaojia.is_deleted == "N"
                        ).first()

                        if baojia:
                            # 获取线索信息
                            from models.xiansuo_guanli.xiansuo import Xiansuo
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
                "step_id": record.id,  # 前端需要
                "workflow_id": workflow.id,
                "title": f"{workflow.shenhe_leixing} - 步骤{record.buzhou_bianhao}",
                "type": workflow.shenhe_leixing,
                "audit_type": workflow.shenhe_leixing,  # 前端需要
                "status": "pending",
                "created_at": workflow.shenqing_shijian.isoformat() if workflow.shenqing_shijian else workflow.created_at.isoformat(),
                "priority": "high",
                "description": workflow.shenqing_yuanyin or "无描述",
                "applicant": workflow.shenqing_ren_id,
                "applicant_reason": workflow.shenqing_yuanyin or "无",  # 前端需要
                "step_name": record.buzhou_mingcheng,
                "step_number": record.buzhou_bianhao,
                "workflow_number": workflow.liucheng_bianhao,
                "expected_time": record.qiwang_chuli_shijian.isoformat() if record.qiwang_chuli_shijian else None,  # 前端需要
                "related_info": related_info  # 前端需要
            })

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取待审核任务失败: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
@check_permission("audit_config")
async def get_workflows(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """获取审核工作流列表"""
    try:
        params = AuditWorkflowListParams(
            page=page,
            size=size,
            status=status,
            audit_type=audit_type,
            search=search
        )

        service = AuditWorkflowService(db)
        return service.get_workflow_list(params)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流列表失败: {str(e)}")

@router.post("/", response_model=AuditWorkflowResponse)
@check_permission("audit_config")
async def create_workflow(
    workflow_data: AuditWorkflowCreate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建审核工作流"""
    try:
        service = AuditWorkflowService(db)
        return service.create_workflow_template(workflow_data, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建工作流失败: {str(e)}")

@router.get("/template/{workflow_id}", response_model=AuditWorkflowResponse)
@check_permission("audit_config")
async def get_workflow_template(
    workflow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作流模板详情"""
    try:
        service = AuditWorkflowService(db)
        return service.get_workflow_by_id(workflow_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流模板失败: {str(e)}")

@router.put("/{workflow_id}", response_model=AuditWorkflowResponse)
@check_permission("audit_config")
async def update_workflow(
    workflow_id: str,
    workflow_data: AuditWorkflowUpdate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新审核工作流"""
    try:
        service = AuditWorkflowService(db)
        return service.update_workflow_template(workflow_id, workflow_data, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新工作流失败: {str(e)}")

@router.delete("/{workflow_id}")
@check_permission("audit_config")
async def delete_workflow(
    workflow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除审核工作流"""
    try:
        service = AuditWorkflowService(db)
        success = service.delete_workflow_template(workflow_id)
        return {"success": success, "message": f"工作流 {workflow_id} 已删除"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除工作流失败: {str(e)}")

@router.get("/{workflow_id}", response_model=Dict[str, Any])
@check_permission("audit:read")
async def get_workflow(
    workflow_id: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个审核流程详情"""
    try:
        from models.shenhe_guanli.shenhe_liucheng import ShenheLiucheng
        from models.shenhe_guanli.shenhe_jilu import ShenheJilu
        from models.yonghu_guanli.yonghu import Yonghu as YonghuModel
        from sqlalchemy.orm import joinedload

        # 查询审核流程
        workflow = db.query(ShenheLiucheng).filter(
            ShenheLiucheng.id == workflow_id,
            ShenheLiucheng.is_deleted == "N"
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="审核流程不存在")

        # 查询审核记录
        records = db.query(ShenheJilu).filter(
            ShenheJilu.liucheng_id == workflow_id,
            ShenheJilu.is_deleted == "N"
        ).order_by(ShenheJilu.buzhou_bianhao).all()

        # 查询申请人信息
        applicant = db.query(YonghuModel).filter(
            YonghuModel.id == workflow.shenqing_ren_id
        ).first()

        # 构建审核步骤信息（使用前端期望的字段名）
        steps = []
        for record in records:
            # 查询审核人信息
            auditor = db.query(YonghuModel).filter(
                YonghuModel.id == record.shenhe_ren_id
            ).first()

            steps.append({
                "id": record.id,
                "buzhou_bianhao": record.buzhou_bianhao,  # 前端期望
                "buzhou_mingcheng": record.buzhou_mingcheng,  # 前端期望
                "shenhe_ren_id": record.shenhe_ren_id,  # 前端期望
                "shenhe_ren_mingcheng": auditor.xingming if auditor else "未知",  # 前端期望
                "jilu_zhuangtai": record.jilu_zhuangtai,  # 前端期望
                "shenhe_jieguo": record.shenhe_jieguo,  # 前端期望
                "shenhe_yijian": record.shenhe_yijian,  # 前端期望
                "shenhe_shijian": record.shenhe_shijian.isoformat() if record.shenhe_shijian else None,  # 前端期望
                "qiwang_shijian": record.qiwang_chuli_shijian.isoformat() if record.qiwang_chuli_shijian else None,  # 前端期望（注意字段名）
                "created_at": record.created_at.isoformat() if record.created_at else None,  # 前端期望
                "fujian_lujing": getattr(record, 'fujian_lujing', None),  # 前端期望
                "fujian_miaoshu": getattr(record, 'fujian_miaoshu', None)  # 前端期望
            })

        # 获取关联对象信息（复用之前的逻辑）
        related_info = None
        if (
            workflow.guanlian_id
            and workflow.shenhe_leixing == "hetong_jine_xiuzheng"
        ):
            from models.hetong_guanli.hetong import Hetong
            hetong = db.query(Hetong).filter(
                Hetong.id == workflow.guanlian_id,
                Hetong.is_deleted == "N"
            ).first()

            if hetong:
                related_info = {
                    "id": hetong.id,
                    "name": hetong.hetong_bianhao or hetong.hetong_mingcheng or "未知合同",
                    "type": "contract"
                }
            else:
                from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
                baojia = db.query(XiansuoBaojia).filter(
                    XiansuoBaojia.id == workflow.guanlian_id,
                    XiansuoBaojia.is_deleted == "N"
                ).first()

                if baojia:
                    from models.xiansuo_guanli.xiansuo import Xiansuo
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

        # 返回数据（使用前端期望的字段名）
        return {
            "id": workflow.id,
            "workflow_number": workflow.liucheng_bianhao,
            "audit_type": workflow.shenhe_leixing,
            "status": workflow.shenhe_zhuangtai,
            "shenhe_zhuangtai": workflow.shenhe_zhuangtai,  # 前端期望
            "current_step": workflow.dangqian_buzhou,
            "total_steps": workflow.zonggong_buzhou,
            "applicant_id": workflow.shenqing_ren_id,
            "submitter": applicant.xingming if applicant else "未知",  # 前端期望
            "shenqing_yuanyin": workflow.shenqing_yuanyin or "无",  # 前端期望
            "created_at": workflow.shenqing_shijian.isoformat() if workflow.shenqing_shijian else workflow.created_at.isoformat(),  # 前端期望
            "wancheng_shijian": workflow.wancheng_shijian.isoformat() if workflow.wancheng_shijian else None,  # 前端期望
            "related_info": related_info,
            "shenhe_jilu": steps,  # 前端期望的字段名（审核记录）
            "beizhu": workflow.beizhu
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取审核流程详情失败: {str(e)}")
