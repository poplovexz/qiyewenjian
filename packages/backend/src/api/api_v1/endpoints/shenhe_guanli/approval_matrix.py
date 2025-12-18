"""
审批权责矩阵API端点
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.security.permissions import check_permission
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu, YonghuJiaose
from services.shenhe_guanli.approval_matrix_service import ApprovalMatrixService

router = APIRouter()


class ApproverAssignRequest(BaseModel):
    """审批人分配请求模型"""
    role_code: str = Field(..., description="角色代码")
    amount: float = Field(default=0, description="金额")
    department: Optional[str] = Field(None, description="部门")


class ApprovalChainRequest(BaseModel):
    """审批链请求模型"""
    rule_type: str = Field(..., description="规则类型")
    amount: float = Field(default=0, description="金额")


class ApproverValidationRequest(BaseModel):
    """审批人权限验证请求模型"""
    user_id: str = Field(..., description="用户ID")
    role_code: str = Field(..., description="角色代码")
    amount: float = Field(default=0, description="金额")


@router.get("/matrix", summary="获取审批权责矩阵")
@check_permission("audit_config")
async def get_approval_matrix(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取完整的审批权责矩阵
    
    返回所有角色、用户映射关系和审批权限配置
    """
    try:
        service = ApprovalMatrixService(db)
        matrix = service.get_approval_matrix()
        return matrix
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审批矩阵失败: {str(e)}")


@router.post("/assign-approver", summary="分配审批人")
@check_permission("audit_config")
async def assign_approver(
    request: ApproverAssignRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据角色和条件自动分配审批人
    
    - **role_code**: 角色代码
    - **amount**: 金额（用于权限判断）
    - **department**: 部门（优先匹配同部门）
    """
    try:
        service = ApprovalMatrixService(db)
        approver_id = service.assign_approver(
            role_code=request.role_code,
            amount=request.amount,
            department=request.department
        )
        
        if approver_id:
            # 获取审批人信息
            approver = db.query(Yonghu).filter(Yonghu.id == approver_id).first()
            return {
                "success": True,
                "approver": {
                    "id": approver.id,
                    "name": approver.yonghu_ming,
                    "email": approver.youxiang,
                    "department": getattr(approver, 'bumen', ''),
                    "position": getattr(approver, 'zhiwei', '')
                }
            }
        else:
            return {
                "success": False,
                "message": f"未找到角色 {request.role_code} 的可用审批人"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配审批人失败: {str(e)}")


@router.post("/approval-chain", summary="获取审批链")
@check_permission("audit_config")
async def get_approval_chain(
    request: ApprovalChainRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据规则类型和金额获取完整的审批链
    
    - **rule_type**: 规则类型
    - **amount**: 金额
    """
    try:
        service = ApprovalMatrixService(db)
        chain = service.get_approval_chain(request.rule_type, request.amount)
        
        return {
            "rule_type": request.rule_type,
            "amount": request.amount,
            "chain_length": len(chain),
            "approval_chain": chain
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审批链失败: {str(e)}")


@router.post("/validate-approver", summary="验证审批人权限")
@check_permission("audit_config")
async def validate_approver_authority(
    request: ApproverValidationRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    验证指定用户是否有审批权限
    
    - **user_id**: 用户ID
    - **role_code**: 角色代码
    - **amount**: 金额
    """
    try:
        service = ApprovalMatrixService(db)
        has_authority = service.validate_approver_authority(
            user_id=request.user_id,
            role_code=request.role_code,
            amount=request.amount
        )
        
        return {
            "user_id": request.user_id,
            "role_code": request.role_code,
            "amount": request.amount,
            "has_authority": has_authority,
            "message": "有审批权限" if has_authority else "无审批权限或权限不足"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证审批权限失败: {str(e)}")


@router.get("/roles", summary="获取审批角色列表")
@check_permission("audit_config")
async def get_approval_roles(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有可用的审批角色"""
    try:
        from models.yonghu_guanli import Jiaose
        
        roles = db.query(Jiaose).filter(Jiaose.is_deleted == "N").all()
        
        role_list = []
        for role in roles:
            # 获取角色下的用户数量
            user_count = db.query(Yonghu).join(YonghuJiaose).filter(
                YonghuJiaose.jiaose_id == role.id,
                Yonghu.is_deleted == "N",
                Yonghu.zhuangtai == "active"
            ).count()
            
            service = ApprovalMatrixService(db)
            authority = service._get_role_approval_authority(role.jiaose_bianma)
            
            role_list.append({
                "id": role.id,
                "name": role.jiaose_ming,
                "code": role.jiaose_bianma,
                "description": role.miaoshu,
                "user_count": user_count,
                "max_amount": authority.get("max_amount", 0),
                "authority_description": authority.get("description", "")
            })
        
        return {"roles": role_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审批角色失败: {str(e)}")


@router.get("/departments", summary="获取部门列表")
@check_permission("audit_config")
async def get_departments(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有部门列表"""
    try:
        # 查询所有不同的部门
        departments = db.query(Yonghu.bumen).filter(
            Yonghu.bumen.isnot(None),
            Yonghu.bumen != "",
            Yonghu.is_deleted == "N"
        ).distinct().all()
        
        dept_list = []
        for (dept_name,) in departments:
            # 统计部门人数
            user_count = db.query(Yonghu).filter(
                Yonghu.bumen == dept_name,
                Yonghu.is_deleted == "N",
                Yonghu.zhuangtai == "active"
            ).count()
            
            dept_list.append({
                "name": dept_name,
                "user_count": user_count
            })
        
        return {"departments": dept_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取部门列表失败: {str(e)}")


@router.get("/approval-levels/{rule_type}", summary="获取规则类型的审批级别")
@check_permission("audit_config")
async def get_approval_levels_by_rule_type(
    rule_type: str,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定规则类型的审批级别配置"""
    try:
        service = ApprovalMatrixService(db)
        levels = service._get_approval_levels()
        
        rule_config = levels.get(rule_type)
        if not rule_config:
            raise HTTPException(status_code=404, detail=f"未找到规则类型 {rule_type} 的配置")
        
        return {
            "rule_type": rule_type,
            "config": rule_config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审批级别失败: {str(e)}")
