"""
支付订单审核集成服务
将支付订单系统与审核流程对接
"""
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from models.zhifu_guanli import ZhifuDingdan, ZhifuLiushui
from models.shenhe_guanli import ShenheJilu, ShenheGuize
from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine
from services.shenhe_guanli.approval_matrix_service import ApprovalMatrixService


class PaymentAuditService:
    """支付订单审核集成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_engine = ShenheWorkflowEngine(db)
        self.approval_matrix = ApprovalMatrixService(db)
    
    def trigger_payment_audit(self, payment_order_id: str, trigger_user_id: str) -> Dict[str, Any]:
        """
        触发支付订单审核
        
        Args:
            payment_order_id: 支付订单ID
            trigger_user_id: 触发用户ID
            
        Returns:
            审核记录信息
        """
        # 获取支付订单
        payment_order = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == payment_order_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not payment_order:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 检查是否已有审核记录
        existing_audit = self.db.query(ShenheJilu).filter(
            ShenheJilu.yewu_id == payment_order_id,
            ShenheJilu.yewu_leixing == "payment_order",
            ShenheJilu.shenhe_zhuangtai.in_(["pending", "in_progress"])
        ).first()
        
        if existing_audit:
            raise HTTPException(status_code=400, detail="该支付订单已在审核中")
        
        # 根据金额和支付类型匹配审核规则
        applicable_rules = self._find_applicable_rules(payment_order)
        
        if not applicable_rules:
            # 如果没有匹配的规则，直接通过
            return self._auto_approve_payment(payment_order, trigger_user_id)
        
        # 选择最高优先级的规则
        selected_rule = min(applicable_rules, key=lambda r: r.paixu)
        
        # 创建审核记录
        audit_record = self._create_audit_record(payment_order, selected_rule, trigger_user_id)
        
        # 启动审核工作流
        workflow_result = self.workflow_engine.start_workflow(
            rule_id=selected_rule.id,
            business_id=payment_order_id,
            business_type="payment_order",
            applicant_id=trigger_user_id,
            business_data={
                "payment_amount": float(payment_order.dingdan_jine),
                "payment_type": payment_order.zhifu_leixing,
                "contract_id": payment_order.hetong_id,
                "customer_id": payment_order.kehu_id,
                "order_name": payment_order.dingdan_mingcheng
            }
        )
        
        return {
            "audit_record_id": audit_record.id,
            "rule_id": selected_rule.id,
            "rule_name": selected_rule.guize_mingcheng,
            "workflow_id": workflow_result.get("workflow_id"),
            "current_step": workflow_result.get("current_step"),
            "next_approver": workflow_result.get("next_approver"),
            "estimated_completion": workflow_result.get("estimated_completion")
        }
    
    def approve_payment(self, audit_record_id: str, approver_id: str, 
                       approval_comment: str = None, approval_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        审批支付订单
        
        Args:
            audit_record_id: 审核记录ID
            approver_id: 审批人ID
            approval_comment: 审批意见
            approval_data: 审批数据
            
        Returns:
            审批结果
        """
        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == audit_record_id
        ).first()
        
        if not audit_record:
            raise HTTPException(status_code=404, detail="审核记录不存在")
        
        # 验证审批权限
        if audit_record.dangqian_shenpi_ren != approver_id:
            raise HTTPException(status_code=403, detail="您不是当前审批人")
        
        # 获取支付订单
        payment_order = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == audit_record.yewu_id
        ).first()
        
        if not payment_order:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 执行审批
        approval_result = self.workflow_engine.approve_step(
            audit_record_id=audit_record_id,
            approver_id=approver_id,
            decision="approve",
            comment=approval_comment,
            approval_data=approval_data
        )
        
        # 如果审核完成且通过，更新支付订单状态
        if approval_result.get("workflow_status") == "completed" and approval_result.get("final_decision") == "approved":
            self._complete_payment_approval(payment_order, approver_id)
        
        return approval_result
    
    def reject_payment(self, audit_record_id: str, approver_id: str, 
                      rejection_reason: str) -> Dict[str, Any]:
        """
        拒绝支付订单
        
        Args:
            audit_record_id: 审核记录ID
            approver_id: 审批人ID
            rejection_reason: 拒绝原因
            
        Returns:
            拒绝结果
        """
        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == audit_record_id
        ).first()
        
        if not audit_record:
            raise HTTPException(status_code=404, detail="审核记录不存在")
        
        # 验证审批权限
        if audit_record.dangqian_shenpi_ren != approver_id:
            raise HTTPException(status_code=403, detail="您不是当前审批人")
        
        # 获取支付订单
        payment_order = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == audit_record.yewu_id
        ).first()
        
        if not payment_order:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 执行拒绝
        rejection_result = self.workflow_engine.approve_step(
            audit_record_id=audit_record_id,
            approver_id=approver_id,
            decision="reject",
            comment=rejection_reason
        )
        
        # 更新支付订单状态为审核拒绝
        payment_order.zhifu_zhuangtai = "audit_rejected"
        payment_order.updated_at = datetime.now()
        payment_order.updated_by = approver_id
        self.db.commit()
        
        return rejection_result
    
    def get_payment_audit_status(self, payment_order_id: str) -> Dict[str, Any]:
        """
        获取支付订单审核状态
        
        Args:
            payment_order_id: 支付订单ID
            
        Returns:
            审核状态信息
        """
        # 获取支付订单
        payment_order = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == payment_order_id
        ).first()
        
        if not payment_order:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.yewu_id == payment_order_id,
            ShenheJilu.yewu_leixing == "payment_order"
        ).order_by(ShenheJilu.created_at.desc()).first()
        
        if not audit_record:
            return {
                "payment_order_id": payment_order_id,
                "audit_status": "not_required",
                "payment_status": payment_order.zhifu_zhuangtai,
                "message": "该支付订单无需审核"
            }
        
        # 获取审核步骤详情
        workflow_status = self.workflow_engine.get_workflow_status(audit_record.id)
        
        return {
            "payment_order_id": payment_order_id,
            "audit_record_id": audit_record.id,
            "audit_status": audit_record.shenhe_zhuangtai,
            "payment_status": payment_order.zhifu_zhuangtai,
            "current_approver": audit_record.dangqian_shenpi_ren,
            "workflow_status": workflow_status,
            "created_at": audit_record.created_at,
            "updated_at": audit_record.updated_at
        }
    
    def _find_applicable_rules(self, payment_order: ZhifuDingdan) -> List[ShenheGuize]:
        """查找适用的审核规则"""
        # 查询支付审核相关的规则
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == "zhifu_shenhe",
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()
        
        applicable_rules = []
        
        for rule in rules:
            if self._check_rule_conditions(rule, payment_order):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    @staticmethod
    def _check_rule_conditions(rule: ShenheGuize, payment_order: ZhifuDingdan) -> bool:
        """检查规则条件是否满足"""
        try:
            conditions = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian
            
            if not conditions:
                return False
            
            # 检查金额条件
            if "amount_threshold" in conditions:
                threshold = conditions["amount_threshold"].get("value", 0)
                operator = conditions["amount_threshold"].get("operator", ">=")
                amount = float(payment_order.dingdan_jine)
                
                if operator == ">=" and amount >= threshold:
                    return True
                elif operator == ">" and amount > threshold:
                    return True
                elif operator == "<=" and amount <= threshold:
                    return True
                elif operator == "<" and amount < threshold:
                    return True
            
            # 检查支付类型条件
            if "payment_types" in conditions:
                allowed_types = conditions["payment_types"]
                if payment_order.zhifu_leixing in allowed_types:
                    return True
            
            return False
        except Exception:
            return False
    
    def _create_audit_record(self, payment_order: ZhifuDingdan, rule: ShenheGuize, applicant_id: str) -> ShenheJilu:
        """创建审核记录"""
        audit_record = ShenheJilu(
            yewu_id=payment_order.id,
            yewu_leixing="payment_order",
            shenqing_ren=applicant_id,
            shenhe_guize_id=rule.id,
            shenhe_zhuangtai="pending",
            shenqing_shijian=datetime.now(),
            yewu_shuju=json.dumps({
                "payment_amount": float(payment_order.dingdan_jine),
                "payment_type": payment_order.zhifu_leixing,
                "contract_id": payment_order.hetong_id,
                "customer_id": payment_order.kehu_id,
                "order_name": payment_order.dingdan_mingcheng
            }),
            created_by=applicant_id
        )
        
        self.db.add(audit_record)
        self.db.commit()
        self.db.refresh(audit_record)
        
        return audit_record
    
    def _auto_approve_payment(self, payment_order: ZhifuDingdan, user_id: str) -> Dict[str, Any]:
        """自动通过支付订单"""
        payment_order.zhifu_zhuangtai = "approved"
        payment_order.updated_at = datetime.now()
        payment_order.updated_by = user_id
        self.db.commit()
        
        return {
            "payment_order_id": payment_order.id,
            "status": "auto_approved",
            "message": "支付订单已自动通过审核"
        }
    
    def _complete_payment_approval(self, payment_order: ZhifuDingdan, approver_id: str):
        """完成支付审批"""
        payment_order.zhifu_zhuangtai = "approved"
        payment_order.updated_at = datetime.now()
        payment_order.updated_by = approver_id
        self.db.commit()

    # 支付流水审核相关方法
    def trigger_flow_audit(self, flow_id: str, trigger_user_id: str) -> Dict[str, Any]:
        """
        触发支付流水审核

        Args:
            flow_id: 支付流水ID
            trigger_user_id: 触发用户ID

        Returns:
            审核记录信息
        """
        # 获取支付流水
        payment_flow = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == flow_id,
            ZhifuLiushui.is_deleted == "N"
        ).first()

        if not payment_flow:
            raise HTTPException(status_code=404, detail="支付流水不存在")

        # 检查是否已有审核记录
        existing_audit = self.db.query(ShenheJilu).filter(
            ShenheJilu.yewu_id == flow_id,
            ShenheJilu.yewu_leixing == "payment_flow",
            ShenheJilu.shenhe_zhuangtai.in_(["pending", "in_progress"])
        ).first()

        if existing_audit:
            raise HTTPException(status_code=400, detail="该支付流水已在审核中")

        # 根据金额和流水类型匹配审核规则
        applicable_rules = self._find_applicable_flow_rules(payment_flow)

        if not applicable_rules:
            # 如果没有匹配的规则，直接通过
            return self._auto_approve_flow(payment_flow, trigger_user_id)

        # 选择最高优先级的规则
        selected_rule = min(applicable_rules, key=lambda r: r.paixu)

        # 创建审核记录
        audit_record = self._create_flow_audit_record(payment_flow, selected_rule, trigger_user_id)

        # 启动审核工作流
        workflow_result = self.workflow_engine.start_workflow(
            rule_id=selected_rule.id,
            business_id=flow_id,
            business_type="payment_flow",
            applicant_id=trigger_user_id,
            business_data={
                "transaction_amount": float(payment_flow.jiaoyijine),
                "flow_type": payment_flow.liushui_leixing,
                "payment_method": payment_flow.zhifu_fangshi,
                "customer_id": payment_flow.kehu_id,
                "order_id": payment_flow.zhifu_dingdan_id
            }
        )

        return {
            "audit_record_id": audit_record.id,
            "rule_id": selected_rule.id,
            "rule_name": selected_rule.guize_mingcheng,
            "workflow_id": workflow_result.get("workflow_id"),
            "current_step": workflow_result.get("current_step"),
            "next_approver": workflow_result.get("next_approver"),
            "estimated_completion": workflow_result.get("estimated_completion")
        }

    def approve_flow(self, audit_record_id: str, approver_id: str,
                    approval_comment: str = None, approval_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        审批支付流水

        Args:
            audit_record_id: 审核记录ID
            approver_id: 审批人ID
            approval_comment: 审批意见
            approval_data: 审批数据

        Returns:
            审批结果
        """
        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == audit_record_id
        ).first()

        if not audit_record:
            raise HTTPException(status_code=404, detail="审核记录不存在")

        # 验证审批权限
        if audit_record.dangqian_shenpi_ren != approver_id:
            raise HTTPException(status_code=403, detail="您不是当前审批人")

        # 获取支付流水
        payment_flow = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == audit_record.yewu_id
        ).first()

        if not payment_flow:
            raise HTTPException(status_code=404, detail="支付流水不存在")

        # 执行审批
        approval_result = self.workflow_engine.approve_step(
            audit_record_id=audit_record_id,
            approver_id=approver_id,
            decision="approve",
            comment=approval_comment,
            approval_data=approval_data
        )

        # 如果审核完成且通过，更新支付流水状态
        if approval_result.get("workflow_status") == "completed" and approval_result.get("final_decision") == "approved":
            self._complete_flow_approval(payment_flow, approver_id)

        return approval_result

    def reject_flow(self, audit_record_id: str, approver_id: str,
                   rejection_reason: str) -> Dict[str, Any]:
        """
        拒绝支付流水

        Args:
            audit_record_id: 审核记录ID
            approver_id: 审批人ID
            rejection_reason: 拒绝原因

        Returns:
            拒绝结果
        """
        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == audit_record_id
        ).first()

        if not audit_record:
            raise HTTPException(status_code=404, detail="审核记录不存在")

        # 验证审批权限
        if audit_record.dangqian_shenpi_ren != approver_id:
            raise HTTPException(status_code=403, detail="您不是当前审批人")

        # 获取支付流水
        payment_flow = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == audit_record.yewu_id
        ).first()

        if not payment_flow:
            raise HTTPException(status_code=404, detail="支付流水不存在")

        # 执行拒绝
        rejection_result = self.workflow_engine.approve_step(
            audit_record_id=audit_record_id,
            approver_id=approver_id,
            decision="reject",
            comment=rejection_reason
        )

        # 更新支付流水状态为审核拒绝
        payment_flow.liushui_zhuangtai = "audit_rejected"
        payment_flow.updated_at = datetime.now()
        payment_flow.updated_by = approver_id
        self.db.commit()

        return rejection_result

    def get_flow_audit_status(self, flow_id: str) -> Dict[str, Any]:
        """
        获取支付流水审核状态

        Args:
            flow_id: 支付流水ID

        Returns:
            审核状态信息
        """
        # 获取支付流水
        payment_flow = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == flow_id
        ).first()

        if not payment_flow:
            raise HTTPException(status_code=404, detail="支付流水不存在")

        # 获取审核记录
        audit_record = self.db.query(ShenheJilu).filter(
            ShenheJilu.yewu_id == flow_id,
            ShenheJilu.yewu_leixing == "payment_flow"
        ).order_by(ShenheJilu.created_at.desc()).first()

        if not audit_record:
            return {
                "flow_id": flow_id,
                "audit_status": "not_required",
                "flow_status": payment_flow.liushui_zhuangtai,
                "message": "该支付流水无需审核"
            }

        # 获取审核步骤详情
        workflow_status = self.workflow_engine.get_workflow_status(audit_record.id)

        return {
            "flow_id": flow_id,
            "audit_record_id": audit_record.id,
            "audit_status": audit_record.shenhe_zhuangtai,
            "flow_status": payment_flow.liushui_zhuangtai,
            "current_approver": audit_record.dangqian_shenpi_ren,
            "workflow_status": workflow_status,
            "created_at": audit_record.created_at,
            "updated_at": audit_record.updated_at
        }

    def _find_applicable_flow_rules(self, payment_flow: ZhifuLiushui) -> List[ShenheGuize]:
        """查找适用的支付流水审核规则"""
        # 查询支付流水审核相关的规则
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == "liushui_shenhe",
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()

        applicable_rules = []

        for rule in rules:
            if self._check_flow_rule_conditions(rule, payment_flow):
                applicable_rules.append(rule)

        return applicable_rules

    @staticmethod
    def _check_flow_rule_conditions(rule: ShenheGuize, payment_flow: ZhifuLiushui) -> bool:
        """检查支付流水规则条件是否满足"""
        try:
            conditions = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian

            if not conditions:
                return False

            # 检查金额条件
            if "amount_threshold" in conditions:
                threshold = conditions["amount_threshold"].get("value", 0)
                operator = conditions["amount_threshold"].get("operator", ">=")
                amount = float(payment_flow.jiaoyijine)

                if operator == ">=" and amount >= threshold:
                    return True
                elif operator == ">" and amount > threshold:
                    return True
                elif operator == "<=" and amount <= threshold:
                    return True
                elif operator == "<" and amount < threshold:
                    return True

            # 检查流水类型条件
            if "flow_types" in conditions:
                allowed_types = conditions["flow_types"]
                if payment_flow.liushui_leixing in allowed_types:
                    return True

            # 检查支付方式条件
            if "payment_methods" in conditions:
                allowed_methods = conditions["payment_methods"]
                if payment_flow.zhifu_fangshi in allowed_methods:
                    return True

            return False
        except Exception:
            return False

    def _create_flow_audit_record(self, payment_flow: ZhifuLiushui, rule: ShenheGuize, applicant_id: str) -> ShenheJilu:
        """创建支付流水审核记录"""
        audit_record = ShenheJilu(
            yewu_id=payment_flow.id,
            yewu_leixing="payment_flow",
            shenqing_ren=applicant_id,
            shenhe_guize_id=rule.id,
            shenhe_zhuangtai="pending",
            shenqing_shijian=datetime.now(),
            yewu_shuju=json.dumps({
                "transaction_amount": float(payment_flow.jiaoyijine),
                "flow_type": payment_flow.liushui_leixing,
                "payment_method": payment_flow.zhifu_fangshi,
                "customer_id": payment_flow.kehu_id,
                "order_id": payment_flow.zhifu_dingdan_id,
                "flow_number": payment_flow.liushui_bianhao
            }),
            created_by=applicant_id
        )

        self.db.add(audit_record)
        self.db.commit()
        self.db.refresh(audit_record)

        return audit_record

    def _auto_approve_flow(self, payment_flow: ZhifuLiushui, user_id: str) -> Dict[str, Any]:
        """自动通过支付流水"""
        payment_flow.liushui_zhuangtai = "approved"
        payment_flow.updated_at = datetime.now()
        payment_flow.updated_by = user_id
        self.db.commit()

        return {
            "flow_id": payment_flow.id,
            "status": "auto_approved",
            "message": "支付流水已自动通过审核"
        }

    def _complete_flow_approval(self, payment_flow: ZhifuLiushui, approver_id: str):
        """完成支付流水审批"""
        payment_flow.liushui_zhuangtai = "approved"
        payment_flow.caiwu_queren_ren = approver_id
        payment_flow.caiwu_queren_shijian = datetime.now()
        payment_flow.updated_at = datetime.now()
        payment_flow.updated_by = approver_id
        self.db.commit()
