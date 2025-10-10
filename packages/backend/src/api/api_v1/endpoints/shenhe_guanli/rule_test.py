"""
规则测试API端点
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.security.permissions import check_permission
from core.security.jwt_handler import get_current_user
from core.security.audit_permissions import require_audit_permission
from models.yonghu_guanli import Yonghu
from services.shenhe_guanli.rule_test_service import RuleTestService

router = APIRouter()


class RuleTestRequest(BaseModel):
    """规则测试请求模型"""
    rule_id: str = Field(..., description="规则ID")
    test_data: Dict[str, Any] = Field(..., description="测试数据")


class MultiRuleTestRequest(BaseModel):
    """多规则测试请求模型"""
    rule_type: str = Field(..., description="规则类型")
    test_data: Dict[str, Any] = Field(..., description="测试数据")


@router.post("/single", summary="测试单个规则")
@require_audit_permission("audit_rule:test")
async def test_single_rule(
    request: RuleTestRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试单个审核规则
    
    - **rule_id**: 要测试的规则ID
    - **test_data**: 测试数据，包含触发条件所需的字段
    """
    try:
        service = RuleTestService(db)
        result = service.test_rule_trigger(request.rule_id, request.test_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"规则测试失败: {str(e)}")


@router.post("/multiple", summary="测试多个规则")
@check_permission("audit_config")
async def test_multiple_rules(
    request: MultiRuleTestRequest,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试指定类型的所有规则
    
    - **rule_type**: 规则类型
    - **test_data**: 测试数据
    """
    try:
        service = RuleTestService(db)
        result = service.test_multiple_rules(request.rule_type, request.test_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多规则测试失败: {str(e)}")


@router.get("/templates", summary="获取测试模板")
@check_permission("audit_config")
async def get_test_templates(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取规则测试模板"""
    try:
        service = RuleTestService(db)
        templates = service.get_test_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试模板失败: {str(e)}")


@router.post("/batch", summary="批量测试规则")
@check_permission("audit_config")
async def batch_test_rules(
    test_cases: List[Dict[str, Any]],
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量测试多个规则和数据组合
    
    - **test_cases**: 测试用例列表，每个用例包含rule_id和test_data
    """
    try:
        service = RuleTestService(db)
        results = []
        
        for case in test_cases:
            rule_id = case.get("rule_id")
            test_data = case.get("test_data", {})
            
            if not rule_id:
                results.append({
                    "error": "缺少rule_id",
                    "test_data": test_data
                })
                continue
            
            try:
                result = service.test_rule_trigger(rule_id, test_data)
                results.append(result)
            except Exception as e:
                results.append({
                    "rule_id": rule_id,
                    "test_data": test_data,
                    "error": str(e),
                    "triggered": False
                })
        
        return {
            "total_cases": len(test_cases),
            "successful_tests": len([r for r in results if "error" not in r]),
            "failed_tests": len([r for r in results if "error" in r]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量测试失败: {str(e)}")


@router.get("/rule-types", summary="获取可测试的规则类型")
@check_permission("audit_config")
async def get_testable_rule_types(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统中可测试的规则类型"""
    try:
        from models.shenhe_guanli import ShenheGuize
        
        # 查询所有启用的规则类型
        rule_types = db.query(ShenheGuize.guize_leixing).filter(
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).distinct().all()
        
        type_info = []
        for (rule_type,) in rule_types:
            # 统计每种类型的规则数量
            count = db.query(ShenheGuize).filter(
                ShenheGuize.guize_leixing == rule_type,
                ShenheGuize.shi_qiyong == "Y",
                ShenheGuize.is_deleted == "N"
            ).count()
            
            type_info.append({
                "type": rule_type,
                "count": count,
                "description": get_rule_type_description(rule_type)
            })
        
        return {"rule_types": type_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规则类型失败: {str(e)}")


def get_rule_type_description(rule_type: str) -> str:
    """获取规则类型描述"""
    descriptions = {
        "hetong_jine_xiuzheng": "合同金额修正审核",
        "baojia_shenhe": "报价审核",
        "zhifu_shenhe": "支付审核",
        "hetong_shenhe": "合同审核",
        "workflow_template": "工作流模板",
        "amount_change": "金额变更审核",
        "discount_rate": "折扣率审核",
        "contract_amount": "合同金额审核",
        "quote_amount": "报价金额审核"
    }
    return descriptions.get(rule_type, rule_type)


@router.post("/simulate-workflow", summary="模拟工作流执行")
@check_permission("audit_config")
async def simulate_workflow_execution(
    rule_id: str,
    test_data: Dict[str, Any],
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    模拟工作流执行过程
    
    - **rule_id**: 规则ID
    - **test_data**: 测试数据
    """
    try:
        service = RuleTestService(db)
        
        # 先测试规则触发
        test_result = service.test_rule_trigger(rule_id, test_data)
        
        if not test_result["triggered"]:
            return {
                "simulated": False,
                "reason": "规则未触发",
                "test_result": test_result
            }
        
        # 模拟工作流执行
        workflow_preview = test_result.get("workflow_preview", {})
        steps = workflow_preview.get("steps", [])
        
        # 模拟每个步骤的执行
        simulated_execution = []
        for step in steps:
            if step.get("applicable", True):
                simulated_execution.append({
                    "step": step["step"],
                    "name": step["name"],
                    "role": step["role"],
                    "status": "pending",
                    "estimated_completion": "24小时内",
                    "simulated_result": "通过"  # 模拟结果
                })
        
        return {
            "simulated": True,
            "test_result": test_result,
            "workflow_execution": {
                "total_steps": len(simulated_execution),
                "estimated_duration": f"{len(simulated_execution) * 24}小时",
                "steps": simulated_execution
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作流模拟失败: {str(e)}")
