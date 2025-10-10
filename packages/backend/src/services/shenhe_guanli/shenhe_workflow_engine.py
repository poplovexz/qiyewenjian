"""
审核工作流引擎
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.shenhe_guanli import ShenheGuize, ShenheLiucheng, ShenheJilu
from models.hetong_guanli import Hetong, HetongJineBiangeng
from models.xiansuo_guanli import XiansuoBaojia


class ShenheWorkflowEngine:
    """审核工作流引擎"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def trigger_audit(self, audit_type: str, related_id: str, trigger_data: Dict[str, Any], applicant_id: str) -> Optional[str]:
        """
        触发审核流程
        
        Args:
            audit_type: 审核类型 (hetong, baojia)
            related_id: 关联ID (合同ID或报价ID)
            trigger_data: 触发数据 (包含金额、变更信息等)
            applicant_id: 申请人ID
            
        Returns:
            审核流程ID，如果不需要审核则返回None
        """
        # 查找匹配的审核规则
        matching_rule = self._find_matching_rule(audit_type, trigger_data)
        if not matching_rule:
            return None
        
        # 创建审核流程
        workflow_id = self._create_audit_workflow(
            audit_type=audit_type,
            related_id=related_id,
            rule=matching_rule,
            trigger_data=trigger_data,
            applicant_id=applicant_id
        )
        
        # 创建审核步骤
        self._create_audit_steps(workflow_id, matching_rule, trigger_data)
        
        return workflow_id
    
    def process_audit_action(self, workflow_id: str, step_id: str, action_data: Dict[str, Any], auditor_id: str) -> bool:
        """
        处理审核操作
        
        Args:
            workflow_id: 审核流程ID
            step_id: 审核步骤ID
            action_data: 审核操作数据
            auditor_id: 审核人ID
            
        Returns:
            是否完成整个审核流程
        """
        # 获取审核流程
        workflow = self.db.query(ShenheLiucheng).filter(
            ShenheLiucheng.id == workflow_id,
            ShenheLiucheng.is_deleted == "N"
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="审核流程不存在")
        
        # 获取当前审核步骤
        current_step = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == step_id,
            ShenheJilu.liucheng_id == workflow_id,
            ShenheJilu.is_deleted == "N"
        ).first()
        
        if not current_step:
            raise HTTPException(status_code=404, detail="审核步骤不存在")
        
        # 验证审核人权限
        if current_step.shenhe_ren_id != auditor_id:
            raise HTTPException(status_code=403, detail="无权限进行此审核")
        
        # 更新审核记录
        current_step.shenhe_jieguo = action_data.get("shenhe_jieguo")
        current_step.shenhe_yijian = action_data.get("shenhe_yijian")
        current_step.shenhe_shijian = datetime.now()
        current_step.fujian_lujing = action_data.get("fujian_lujing")
        current_step.fujian_miaoshu = action_data.get("fujian_miaoshu")
        current_step.jilu_zhuangtai = "yichuli"
        current_step.updated_at = datetime.now()
        
        # 根据审核结果决定下一步
        if action_data.get("shenhe_jieguo") == "jujue":
            # 拒绝，结束流程
            workflow.shenhe_zhuangtai = "jujue"
            workflow.wancheng_shijian = datetime.now()
            workflow.updated_at = datetime.now()
            self.db.commit()
            return True
        
        elif action_data.get("shenhe_jieguo") == "tongguo":
            # 通过，检查是否还有下一步
            if workflow.dangqian_buzhou >= workflow.zonggong_buzhou:
                # 所有步骤完成
                workflow.shenhe_zhuangtai = "tongguo"
                workflow.wancheng_shijian = datetime.now()
                workflow.updated_at = datetime.now()
                self.db.commit()
                return True
            else:
                # 进入下一步
                workflow.dangqian_buzhou += 1
                workflow.updated_at = datetime.now()
                self.db.commit()
                return False
        
        self.db.commit()
        return False
    
    def _find_matching_rule(self, audit_type: str, trigger_data: Dict[str, Any]) -> Optional[ShenheGuize]:
        """查找匹配的审核规则"""
        # 根据审核类型查找规则
        rule_type_map = {
            "hetong": "hetong_jine_xiuzheng",
            "baojia": "baojia_shenhe"
        }
        
        rule_type = rule_type_map.get(audit_type)
        if not rule_type:
            return None
        
        # 查询启用的规则，按优先级排序
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == rule_type,
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()
        
        # 检查每个规则的触发条件
        for rule in rules:
            if self._check_trigger_condition(rule, trigger_data):
                return rule
        
        return None
    
    def _check_trigger_condition(self, rule: ShenheGuize, trigger_data: Dict[str, Any]) -> bool:
        """检查触发条件是否满足"""
        try:
            condition = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian
            
            if rule.guize_leixing == "hetong_jine_xiuzheng":
                # 合同金额修正规则
                original_amount = trigger_data.get("original_amount", 0)
                new_amount = trigger_data.get("new_amount", 0)
                
                if original_amount <= 0:
                    return False
                
                decrease_percentage = ((original_amount - new_amount) / original_amount) * 100
                
                # 检查是否满足阈值条件
                thresholds = condition.get("thresholds", [])
                for threshold in thresholds:
                    if decrease_percentage >= threshold.get("percentage", 0):
                        return True
            
            elif rule.guize_leixing == "baojia_shenhe":
                # 报价审核规则
                amount = trigger_data.get("amount", 0)
                
                thresholds = condition.get("thresholds", [])
                for threshold in thresholds:
                    if amount >= threshold.get("amount", 0):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _create_audit_workflow(self, audit_type: str, related_id: str, rule: ShenheGuize, 
                             trigger_data: Dict[str, Any], applicant_id: str) -> str:
        """创建审核流程"""
        workflow_id = str(uuid.uuid4())
        workflow_number = f"SH{datetime.now().strftime('%Y%m%d%H%M%S')}{workflow_id[:6]}"
        
        # 计算总步骤数
        flow_config = json.loads(rule.shenhe_liucheng_peizhi) if isinstance(rule.shenhe_liucheng_peizhi, str) else rule.shenhe_liucheng_peizhi
        total_steps = len(flow_config.get("steps", []))
        
        workflow = ShenheLiucheng(
            id=workflow_id,
            liucheng_bianhao=workflow_number,
            shenhe_leixing=audit_type,
            guanlian_id=related_id,
            shenhe_zhuangtai="shenhzhong",
            chufa_guize_id=rule.id,
            dangqian_buzhou=1,
            zonggong_buzhou=total_steps,
            shenqing_ren_id=applicant_id,
            shenqing_yuanyin=trigger_data.get("reason", ""),
            shenqing_shijian=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        self.db.add(workflow)
        self.db.commit()
        
        return workflow_id
    
    def _create_audit_steps(self, workflow_id: str, rule: ShenheGuize, trigger_data: Dict[str, Any]):
        """创建审核步骤"""
        flow_config = json.loads(rule.shenhe_liucheng_peizhi) if isinstance(rule.shenhe_liucheng_peizhi, str) else rule.shenhe_liucheng_peizhi
        steps = flow_config.get("steps", [])
        
        for step_config in steps:
            # 检查步骤条件
            if not self._check_step_condition(step_config, trigger_data):
                continue
            
            # 查找审核人 (这里简化处理，实际应该根据角色查找具体用户)
            auditor_id = self._find_auditor_by_role(step_config.get("role"))
            if not auditor_id:
                continue
            
            step = ShenheJilu(
                id=str(uuid.uuid4()),
                liucheng_id=workflow_id,
                buzhou_bianhao=step_config.get("step"),
                buzhou_mingcheng=step_config.get("name"),
                shenhe_ren_id=auditor_id,
                jilu_zhuangtai="daichuli" if step_config.get("step") == 1 else "daichuli",
                qiwang_chuli_shijian=datetime.now() + timedelta(days=3),  # 默认3天处理期限
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )
            
            self.db.add(step)
        
        self.db.commit()
    
    def _check_step_condition(self, step_config: Dict[str, Any], trigger_data: Dict[str, Any]) -> bool:
        """检查步骤条件"""
        condition = step_config.get("condition")
        if not condition:
            return True
        
        # 简化的条件检查逻辑
        if "percentage" in condition:
            original_amount = trigger_data.get("original_amount", 0)
            new_amount = trigger_data.get("new_amount", 0)
            if original_amount > 0:
                decrease_percentage = ((original_amount - new_amount) / original_amount) * 100
                required_percentage = float(condition.split(">=")[1].strip())
                return decrease_percentage >= required_percentage
        
        if "amount" in condition:
            amount = trigger_data.get("amount", 0)
            required_amount = float(condition.split(">=")[1].strip())
            return amount >= required_amount
        
        return True
    
    def _find_auditor_by_role(self, role: str) -> Optional[str]:
        """根据角色查找审核人"""
        # 这里应该实现根据角色查找用户的逻辑
        # 简化处理，返回固定的用户ID
        role_user_map = {
            "supervisor": "supervisor_user_id",
            "manager": "manager_user_id", 
            "director": "director_user_id"
        }
        return role_user_map.get(role)
