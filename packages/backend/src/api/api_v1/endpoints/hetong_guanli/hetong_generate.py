"""
合同生成API端点
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.security.jwt_handler import get_current_user
from models.yonghu_guanli import Yonghu
from services.hetong_guanli.hetong_generate_service import HetongGenerateService
from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine

router = APIRouter()


class ContractGenerateRequest(BaseModel):
    """合同生成请求模型"""
    baojia_id: str = Field(..., description="报价ID")
    contract_types: List[str] = Field(..., description="合同类型列表")
    daili_jizhang_config: Dict[str, Any] = Field(None, description="代理记账合同配置")
    zengzhi_fuwu_config: Dict[str, Any] = Field(None, description="增值服务合同配置")


class ContractTypeConfig(BaseModel):
    """合同类型配置"""
    price: float = Field(..., description="合同价格")
    count: int = Field(1, description="合同数量")
    party_id: Optional[str] = Field(None, description="乙方主体ID")
    price_change_reason: Optional[str] = Field(None, description="价格调整原因")


class ContractPreviewRequest(BaseModel):
    """合同预览请求模型"""
    hetong_moban_id: str = Field(..., description="合同模板ID")
    kehu_id: str = Field(..., description="客户ID")
    bianliang_zhis: Dict[str, Any] = Field(..., description="模板变量值")


@router.post("/generate", summary="生成合同")
async def generate_contracts(
    request: ContractGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    基于报价生成合同
    
    支持生成多种类型的合同：
    - 代理记账合同
    - 增值服务合同
    
    如果价格调整超过阈值，会自动触发审核流程
    """
    try:
        service = HetongGenerateService(db)
        workflow_engine = ShenheWorkflowEngine(db)
        
        # 验证报价存在且已接受
        quote = service.validate_quote(request.baojia_id)
        
        generated_contracts = []
        audit_workflows = []
        
        # 生成代理记账合同
        if "daili_jizhang" in request.contract_types and request.daili_jizhang_config:
            config = ContractTypeConfig(**request.daili_jizhang_config)
            
            # 检查是否需要审核
            price_diff = abs(config.price - float(quote.zongji_jine))
            if price_diff > 0:
                # 触发审核流程
                audit_data = {
                    "original_amount": float(quote.zongji_jine),
                    "new_amount": config.price,
                    "price_difference": price_diff,
                    "change_reason": config.price_change_reason,
                    "contract_type": "daili_jizhang"
                }
                
                workflow_id = workflow_engine.trigger_audit(
                    audit_type="hetong_jine_xiuzheng",
                    related_id=request.baojia_id,
                    trigger_data=audit_data,
                    applicant_id=current_user.id
                )
                
                if workflow_id:
                    audit_workflows.append({
                        "workflow_id": workflow_id,
                        "contract_type": "daili_jizhang",
                        "reason": "价格调整需要审核"
                    })
                else:
                    # 直接生成合同
                    for i in range(config.count):
                        contract_data = {
                            "kehu_id": quote.xiansuo.kehu_id,
                            "baojia_id": request.baojia_id,
                            "hetong_moban_id": service.get_template_by_type("daili_jizhang"),
                            "yifang_zhuti_id": config.party_id,
                            "hetong_mingcheng": f"{quote.xiansuo.gongsi_mingcheng}代理记账服务合同{f'({i+1})' if i > 0 else ''}",
                            "hetong_jine": config.price,
                            "hetong_leixing": "daili_jizhang",
                            "price_change_reason": config.price_change_reason
                        }
                        
                        contract = service.create_contract(contract_data, current_user.id)
                        generated_contracts.append(contract)
        
        # 生成增值服务合同
        if "zengzhi_fuwu" in request.contract_types and request.zengzhi_fuwu_config:
            config = ContractTypeConfig(**request.zengzhi_fuwu_config)
            
            # 检查是否需要审核
            price_diff = abs(config.price - float(quote.zongji_jine))
            if price_diff > 0:
                # 触发审核流程
                audit_data = {
                    "original_amount": float(quote.zongji_jine),
                    "new_amount": config.price,
                    "price_difference": price_diff,
                    "change_reason": config.price_change_reason,
                    "contract_type": "zengzhi_fuwu"
                }
                
                workflow_id = workflow_engine.trigger_audit(
                    audit_type="hetong_jine_xiuzheng",
                    related_id=request.baojia_id,
                    trigger_data=audit_data,
                    applicant_id=current_user.id
                )
                
                if workflow_id:
                    audit_workflows.append({
                        "workflow_id": workflow_id,
                        "contract_type": "zengzhi_fuwu",
                        "reason": "价格调整需要审核"
                    })
                else:
                    # 直接生成合同
                    for i in range(config.count):
                        contract_data = {
                            "kehu_id": quote.xiansuo.kehu_id,
                            "baojia_id": request.baojia_id,
                            "hetong_moban_id": service.get_template_by_type("zengzhi_fuwu"),
                            "yifang_zhuti_id": config.party_id,
                            "hetong_mingcheng": f"{quote.xiansuo.gongsi_mingcheng}增值服务合同{f'({i+1})' if i > 0 else ''}",
                            "hetong_jine": config.price,
                            "hetong_leixing": "zengzhi_fuwu",
                            "price_change_reason": config.price_change_reason
                        }
                        
                        contract = service.create_contract(contract_data, current_user.id)
                        generated_contracts.append(contract)
        
        return {
            "success": True,
            "message": f"成功生成 {len(generated_contracts)} 份合同" + 
                      (f"，{len(audit_workflows)} 份合同需要审核" if audit_workflows else ""),
            "data": {
                "generated_contracts": generated_contracts,
                "audit_workflows": audit_workflows
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成合同失败: {str(e)}")


@router.post("/preview", summary="预览合同")
async def preview_contract(
    request: ContractPreviewRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    预览合同内容

    根据模板和变量值生成合同预览内容
    """
    try:
        import traceback
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"预览合同请求: template_id={request.hetong_moban_id}, customer_id={request.kehu_id}")
        logger.info(f"变量值: {request.bianliang_zhis}")

        service = HetongGenerateService(db)
        content = service.preview_contract(
            template_id=request.hetong_moban_id,
            customer_id=request.kehu_id,
            variables=request.bianliang_zhis
        )

        return {
            "success": True,
            "data": {
                "content": content
            }
        }

    except HTTPException as he:
        # 重新抛出HTTP异常
        raise he
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"预览合同失败: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"预览合同失败: {str(e)}")


@router.get("/check-by-quote/{baojia_id}", summary="检查报价是否已生成合同")
async def check_contract_by_quote(
    baojia_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    检查指定报价是否已经生成过合同
    """
    try:
        service = HetongGenerateService(db)
        contracts = service.get_contracts_by_quote(baojia_id)
        
        return {
            "success": True,
            "data": {
                "has_contracts": len(contracts) > 0,
                "contracts": contracts
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查合同状态失败: {str(e)}")


@router.get("/templates", summary="获取合同模板列表")
async def get_contract_templates(
    contract_type: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取可用的合同模板列表
    """
    try:
        service = HetongGenerateService(db)
        templates = service.get_available_templates(contract_type)
        
        return {
            "success": True,
            "data": templates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.get("/audit-rules", summary="获取合同审核规则")
async def get_audit_rules(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取合同生成相关的审核规则配置
    """
    try:
        workflow_engine = ShenheWorkflowEngine(db)
        rules = workflow_engine.get_rules_by_type("hetong_jine_xiuzheng")
        
        return {
            "success": True,
            "data": rules
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核规则失败: {str(e)}")
