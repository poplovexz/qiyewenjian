"""
规则测试服务
用于测试审核规则的触发条件和流程逻辑
"""
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.shenhe_guanli import ShenheGuize
from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine


class RuleTestService:
    """规则测试服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def test_rule_trigger(self, rule_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试规则触发条件
        
        Args:
            rule_id: 规则ID
            test_data: 测试数据
            
        Returns:
            测试结果
        """
        # 获取规则
        rule = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == rule_id,
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 解析触发条件
        try:
            trigger_conditions = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian
        except:
            trigger_conditions = {}
        
        # 执行规则测试
        test_result = self._evaluate_trigger_conditions(trigger_conditions, test_data)
        
        # 如果触发，模拟流程创建
        workflow_preview = None
        if test_result["triggered"]:
            workflow_preview = self._generate_workflow_preview(rule, test_data)
        
        return {
            "rule_id": rule_id,
            "rule_name": rule.guize_mingcheng,
            "test_data": test_data,
            "triggered": test_result["triggered"],
            "trigger_reason": test_result["reason"],
            "conditions_met": test_result["conditions_met"],
            "workflow_preview": workflow_preview,
            "test_timestamp": "2024-01-15T12:00:00"
        }
    
    def test_multiple_rules(self, rule_type: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试多个规则
        
        Args:
            rule_type: 规则类型
            test_data: 测试数据
            
        Returns:
            测试结果
        """
        # 获取指定类型的所有启用规则
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == rule_type,
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()
        
        test_results = []
        triggered_rules = []
        
        for rule in rules:
            try:
                result = self.test_rule_trigger(rule.id, test_data)
                test_results.append(result)
                
                if result["triggered"]:
                    triggered_rules.append({
                        "rule_id": rule.id,
                        "rule_name": rule.guize_mingcheng,
                        "priority": rule.paixu
                    })
            except Exception as e:
                test_results.append({
                    "rule_id": rule.id,
                    "rule_name": rule.guize_mingcheng,
                    "error": str(e),
                    "triggered": False
                })
        
        return {
            "rule_type": rule_type,
            "test_data": test_data,
            "total_rules": len(rules),
            "triggered_count": len(triggered_rules),
            "triggered_rules": triggered_rules,
            "detailed_results": test_results
        }
    
    def _evaluate_trigger_conditions(self, conditions: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估触发条件"""
        if not conditions:
            return {
                "triggered": False,
                "reason": "无触发条件配置",
                "conditions_met": []
            }
        
        conditions_met = []
        triggered = False
        reason = ""
        
        # 处理不同类型的条件
        condition_type = conditions.get("type", "")
        
        if condition_type == "amount_threshold":
            # 金额阈值条件
            threshold = conditions.get("threshold", 0)
            amount = test_data.get("amount", 0)
            operator = conditions.get("operator", ">=")
            
            if operator == ">=" and amount >= threshold:
                triggered = True
                reason = f"金额 {amount} 大于等于阈值 {threshold}"
            elif operator == ">" and amount > threshold:
                triggered = True
                reason = f"金额 {amount} 大于阈值 {threshold}"
            elif operator == "<=" and amount <= threshold:
                triggered = True
                reason = f"金额 {amount} 小于等于阈值 {threshold}"
            elif operator == "<" and amount < threshold:
                triggered = True
                reason = f"金额 {amount} 小于阈值 {threshold}"
            else:
                reason = f"金额 {amount} 不满足条件 {operator} {threshold}"
            
            conditions_met.append({
                "type": "amount_threshold",
                "expected": f"{operator} {threshold}",
                "actual": amount,
                "met": triggered
            })
        
        elif condition_type == "percentage_change":
            # 百分比变更条件
            threshold = conditions.get("threshold", 0)
            original_amount = test_data.get("original_amount", 0)
            new_amount = test_data.get("new_amount", 0)
            
            if original_amount > 0:
                change_percentage = abs((new_amount - original_amount) / original_amount) * 100
                if change_percentage >= threshold:
                    triggered = True
                    reason = f"变更百分比 {change_percentage:.2f}% 大于等于阈值 {threshold}%"
                else:
                    reason = f"变更百分比 {change_percentage:.2f}% 小于阈值 {threshold}%"
                
                conditions_met.append({
                    "type": "percentage_change",
                    "expected": f">= {threshold}%",
                    "actual": f"{change_percentage:.2f}%",
                    "met": triggered
                })
            else:
                reason = "原始金额为0，无法计算变更百分比"
        
        elif condition_type == "quote_approval":
            # 报价审核条件
            thresholds = conditions.get("thresholds", [])
            amount = test_data.get("amount", 0)
            
            for threshold_config in thresholds:
                threshold_amount = threshold_config.get("amount", 0)
                if amount >= threshold_amount:
                    triggered = True
                    reason = f"报价金额 {amount} 触发 {threshold_config.get('approver_level', '')} 审核"
                    conditions_met.append({
                        "type": "quote_approval",
                        "level": threshold_config.get("approver_level", ""),
                        "threshold": threshold_amount,
                        "met": True
                    })
        
        return {
            "triggered": triggered,
            "reason": reason,
            "conditions_met": conditions_met
        }
    
    def _generate_workflow_preview(self, rule: ShenheGuize, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成工作流预览"""
        try:
            workflow_config = json.loads(rule.shenhe_liucheng_peizhi) if isinstance(rule.shenhe_liucheng_peizhi, str) else rule.shenhe_liucheng_peizhi
            steps = workflow_config.get("steps", [])
            
            preview_steps = []
            for step in steps:
                # 检查步骤条件
                step_condition = step.get("condition", "")
                step_applicable = True
                
                if step_condition:
                    # 简单的条件检查
                    amount = test_data.get("amount", 0)
                    if "amount >=" in step_condition:
                        threshold = int(step_condition.split(">=")[1].strip())
                        step_applicable = amount >= threshold
                    elif "amount <" in step_condition:
                        threshold = int(step_condition.split("<")[1].strip())
                        step_applicable = amount < threshold
                
                if step_applicable:
                    preview_steps.append({
                        "step": step.get("step", 0),
                        "name": step.get("name", ""),
                        "role": step.get("role", ""),
                        "applicable": True,
                        "estimated_time": "24小时"
                    })
                else:
                    preview_steps.append({
                        "step": step.get("step", 0),
                        "name": step.get("name", ""),
                        "role": step.get("role", ""),
                        "applicable": False,
                        "skip_reason": "不满足条件"
                    })
            
            return {
                "total_steps": len(preview_steps),
                "applicable_steps": len([s for s in preview_steps if s.get("applicable", True)]),
                "estimated_duration": f"{len([s for s in preview_steps if s.get('applicable', True)]) * 24}小时",
                "steps": preview_steps
            }
        except Exception as e:
            return {
                "error": f"生成工作流预览失败: {str(e)}",
                "steps": []
            }
    
    def get_test_templates(self) -> List[Dict[str, Any]]:
        """获取测试模板"""
        return [
            {
                "name": "合同金额修改测试",
                "type": "hetong_jine_xiuzheng",
                "template": {
                    "contract_id": "CONTRACT-001",
                    "original_amount": 100000,
                    "new_amount": 120000,
                    "amount": 120000,
                    "change_reason": "客户需求变更",
                    "applicant": "张三"
                }
            },
            {
                "name": "报价审核测试",
                "type": "baojia_shenhe",
                "template": {
                    "quote_id": "QUOTE-001",
                    "amount": 50000,
                    "customer": "ABC公司",
                    "discount_rate": 0.1,
                    "sales_person": "李四"
                }
            },
            {
                "name": "大额支付审核测试",
                "type": "zhifu_shenhe",
                "template": {
                    "payment_id": "PAY-001",
                    "amount": 200000,
                    "payment_type": "bank_transfer",
                    "recipient": "供应商A",
                    "purpose": "采购付款"
                }
            }
        ]
