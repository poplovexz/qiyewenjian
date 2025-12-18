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
from models.zhifu_guanli import ZhifuTongzhi
from models.yonghu_guanli import Yonghu


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

        # 发送通知给第一个审核人
        self._send_audit_notification(workflow_id, applicant_id)

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

            # 发送拒绝通知给申请人
            self._send_rejection_notification(workflow_id, auditor_id, action_data.get("shenhe_yijian"))

            return True

        elif action_data.get("shenhe_jieguo") == "tongguo":
            # 通过，检查是否还有下一步
            if workflow.dangqian_buzhou >= workflow.zonggong_buzhou:
                # 所有步骤完成
                workflow.shenhe_zhuangtai = "tongguo"
                workflow.wancheng_shijian = datetime.now()
                workflow.updated_at = datetime.now()
                self.db.commit()

                # 发送审核通过通知给申请人
                self._send_approval_notification(workflow_id, auditor_id)

                return True
            else:
                # 进入下一步
                workflow.dangqian_buzhou += 1
                workflow.updated_at = datetime.now()
                self.db.commit()

                # 发送通知给下一个审核人
                self._send_next_step_notification(workflow_id, auditor_id)

                return False

        self.db.commit()
        return False
    
    def _find_matching_rule(self, audit_type: str, trigger_data: Dict[str, Any]) -> Optional[ShenheGuize]:
        """查找匹配的审核规则"""
        # 审核类型可以直接使用，也可以通过映射转换
        # 支持两种格式：
        # 1. 直接传入规则类型，如 "hetong_jine_xiuzheng"
        # 2. 传入简化类型，如 "hetong"，会映射到 "hetong_jine_xiuzheng"
        # 3. 工作流模板类型，如 "yinhang_huikuan"，通过 chufa_tiaojian 中的 audit_type 匹配
        rule_type_map = {
            "hetong": "hetong_jine_xiuzheng",
            "baojia": "baojia_shenhe"
        }

        # 如果 audit_type 在映射表中，使用映射值；否则直接使用 audit_type
        rule_type = rule_type_map.get(audit_type, audit_type)
        if not rule_type:
            return None

        # 先查询传统规则类型（按 guize_leixing 匹配）
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == rule_type,
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()

        # 检查每个规则的触发条件
        for rule in rules:
            if self._check_trigger_condition(rule, trigger_data):
                return rule

        # 如果没有找到传统规则，查询工作流模板类型（按 audit_type 匹配）
        workflow_templates = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == "workflow_template",
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()

        for template in workflow_templates:
            try:
                condition = json.loads(template.chufa_tiaojian) if isinstance(template.chufa_tiaojian, str) else template.chufa_tiaojian
                # 检查 audit_type 是否匹配
                if condition.get("audit_type") == audit_type:
                    return template
            except Exception:
                continue

        return None
    
    @staticmethod
    def _check_trigger_condition(rule: ShenheGuize, trigger_data: Dict[str, Any]) -> bool:
        """检查触发条件是否满足"""
        try:
            condition = json.loads(rule.chufa_tiaojian) if isinstance(rule.chufa_tiaojian, str) else rule.chufa_tiaojian

            # 工作流模板类型：无需检查触发条件，直接返回 True
            if rule.guize_leixing == "workflow_template":
                return True

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

        # 构建申请原因（兼容多种字段名）
        reason = trigger_data.get("change_reason") or trigger_data.get("reason") or ""

        # 如果没有原因，根据审核类型生成默认原因
        if not reason:
            if audit_type == "hetong_jine_xiuzheng":
                original_amount = trigger_data.get("original_amount", 0)
                new_amount = trigger_data.get("new_amount", 0)
                diff = new_amount - original_amount
                if diff > 0:
                    reason = f"合同金额上调 {abs(diff):.2f} 元"
                elif diff < 0:
                    reason = f"合同金额下调 {abs(diff):.2f} 元"
                else:
                    reason = "合同金额修正"
            elif audit_type == "yinhang_huikuan":
                danju_bianhao = trigger_data.get("danju_bianhao", "")
                huikuan_jine = trigger_data.get("huikuan_jine", 0)
                reason = f"银行汇款凭证审核 - 单据号：{danju_bianhao}，金额：{huikuan_jine:.2f} 元"

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
            shenqing_yuanyin=reason,
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

        # 🔧 修复：如果流程配置中有 workflow_id，则从工作流模板中加载步骤配置
        if "workflow_id" in flow_config and not flow_config.get("steps"):
            workflow_template_id = flow_config.get("workflow_id")
            if workflow_template_id:
                # 查询工作流模板
                workflow_template = self.db.query(ShenheGuize).filter(
                    ShenheGuize.id == workflow_template_id,
                    ShenheGuize.guize_leixing == "workflow_template",
                    ShenheGuize.is_deleted == "N"
                ).first()

                if workflow_template:
                    # 从模板中加载步骤配置
                    template_config = json.loads(workflow_template.shenhe_liucheng_peizhi) if isinstance(workflow_template.shenhe_liucheng_peizhi, str) else workflow_template.shenhe_liucheng_peizhi
                    flow_config = template_config

        steps = flow_config.get("steps", [])
        
        for step_config in steps:
            # 检查步骤条件
            if not self._check_step_condition(step_config, trigger_data):
                continue

            # 查找审核人
            # 优先使用 approver_user_id，如果没有则根据 approver_role 查找
            auditor_id = step_config.get("approver_user_id")
            if not auditor_id:
                # 兼容旧数据：根据角色查找用户
                auditor_id = self._find_auditor_by_role(step_config.get("approver_role") or step_config.get("role"))

            if not auditor_id:
                continue
            
            # 兼容两种字段名：step/step_order, name/step_name
            step_order = step_config.get("step_order") or step_config.get("step")
            step_name = step_config.get("step_name") or step_config.get("name")

            step = ShenheJilu(
                id=str(uuid.uuid4()),
                liucheng_id=workflow_id,
                buzhou_bianhao=step_order,
                buzhou_mingcheng=step_name,
                shenhe_ren_id=auditor_id,
                jilu_zhuangtai="daichuli" if step_order == 1 else "daichuli",
                qiwang_chuli_shijian=datetime.now() + timedelta(days=3),  # 默认3天处理期限
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )
            
            self.db.add(step)
        
        self.db.commit()
    
    @staticmethod
    def _check_step_condition(step_config: Dict[str, Any], trigger_data: Dict[str, Any]) -> bool:
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
        if not role:
            return None

        try:
            from models.yonghu_guanli.jiaose import Jiaose
            from models.yonghu_guanli.yonghu_jiaose import YonghuJiaose

            # 查找角色
            jiaose = self.db.query(Jiaose).filter(
                Jiaose.jiaose_bianma == role,
                Jiaose.is_deleted == "N"
            ).first()

            if not jiaose:
                return None

            # 查找拥有该角色的第一个启用用户
            yonghu_jiaose = self.db.query(YonghuJiaose).join(
                Yonghu, YonghuJiaose.yonghu_id == Yonghu.id
            ).filter(
                YonghuJiaose.jiaose_id == jiaose.id,
                Yonghu.zhuangtai == "active",
                Yonghu.is_deleted == "N",
                YonghuJiaose.is_deleted == "N"
            ).first()

            if yonghu_jiaose:
                return yonghu_jiaose.yonghu_id

            return None

        except Exception as e:
            print(f"查找审核人失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _send_audit_notification(self, workflow_id: str, applicant_id: str):
        """发送审核通知给第一个审核人"""
        try:
            # 获取审核流程
            workflow = self.db.query(ShenheLiucheng).filter(
                ShenheLiucheng.id == workflow_id,
                ShenheLiucheng.is_deleted == "N"
            ).first()

            if not workflow:
                return

            # 获取第一个审核步骤
            first_step = self.db.query(ShenheJilu).filter(
                ShenheJilu.liucheng_id == workflow_id,
                ShenheJilu.buzhou_bianhao == 1,
                ShenheJilu.is_deleted == "N"
            ).first()

            if not first_step or not first_step.shenhe_ren_id:
                return

            # 获取申请人信息
            applicant = self.db.query(Yonghu).filter(
                Yonghu.id == applicant_id,
                Yonghu.is_deleted == "N"
            ).first()

            applicant_name = applicant.xingming if applicant else "未知用户"

            # 构建通知内容
            audit_type_map = {
                "hetong": "合同审核",
                "hetong_jine_xiuzheng": "合同金额修正审核",
                "baojia": "报价审核",
                "yinhang_huikuan": "银行汇款审核"
            }

            audit_type_name = audit_type_map.get(workflow.shenhe_leixing, workflow.shenhe_leixing)

            tongzhi_biaoti = f"【待审核】{audit_type_name} - {workflow.liucheng_bianhao}"
            tongzhi_neirong = f"""
您有一个新的审核任务需要处理：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请人：{applicant_name}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
申请原因：{workflow.shenqing_yuanyin or '无'}

请及时登录系统进行审核。
            """.strip()

            # 创建通知
            notification = ZhifuTongzhi(
                jieshou_ren_id=first_step.shenhe_ren_id,
                tongzhi_leixing="audit_pending",
                tongzhi_biaoti=tongzhi_biaoti,
                tongzhi_neirong=tongzhi_neirong,
                youxian_ji="high",
                fasong_shijian=datetime.now(),
                tongzhi_zhuangtai="unread",
                lianjie_url="/audit/tasks",  # 跳转到审核任务列表
                kuozhan_shuju=json.dumps({
                    "workflow_id": workflow_id,
                    "audit_type": workflow.shenhe_leixing,
                    "step_id": first_step.id,
                    "step_number": first_step.buzhou_bianhao
                }),
                created_by="system"
            )

            self.db.add(notification)
            self.db.commit()

        except Exception as e:
            print(f"发送审核通知失败: {e}")
            import traceback
            traceback.print_exc()

    def _send_next_step_notification(self, workflow_id: str, previous_auditor_id: str):
        """发送通知给下一个审核人"""
        try:
            # 获取审核流程
            workflow = self.db.query(ShenheLiucheng).filter(
                ShenheLiucheng.id == workflow_id,
                ShenheLiucheng.is_deleted == "N"
            ).first()

            if not workflow:
                return

            # 获取下一个审核步骤
            next_step = self.db.query(ShenheJilu).filter(
                ShenheJilu.liucheng_id == workflow_id,
                ShenheJilu.buzhou_bianhao == workflow.dangqian_buzhou,
                ShenheJilu.is_deleted == "N"
            ).first()

            if not next_step or not next_step.shenhe_ren_id:
                return

            # 获取上一个审核人信息
            previous_auditor = self.db.query(Yonghu).filter(
                Yonghu.id == previous_auditor_id,
                Yonghu.is_deleted == "N"
            ).first()

            previous_auditor_name = previous_auditor.xingming if previous_auditor else "未知用户"

            # 构建通知内容
            audit_type_map = {
                "hetong": "合同审核",
                "hetong_jine_xiuzheng": "合同金额修正审核",
                "baojia": "报价审核",
                "yinhang_huikuan": "银行汇款审核"
            }

            audit_type_name = audit_type_map.get(workflow.shenhe_leixing, workflow.shenhe_leixing)

            tongzhi_biaoti = f"【待审核】{audit_type_name} - {workflow.liucheng_bianhao}"
            tongzhi_neirong = f"""
您有一个新的审核任务需要处理：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
当前步骤：第 {workflow.dangqian_buzhou} 步（共 {workflow.zonggong_buzhou} 步）
上一审核人：{previous_auditor_name}（已通过）

请及时登录系统进行审核。
            """.strip()

            # 创建通知
            notification = ZhifuTongzhi(
                jieshou_ren_id=next_step.shenhe_ren_id,
                tongzhi_leixing="audit_pending",
                tongzhi_biaoti=tongzhi_biaoti,
                tongzhi_neirong=tongzhi_neirong,
                youxian_ji="high",
                fasong_shijian=datetime.now(),
                tongzhi_zhuangtai="unread",
                lianjie_url="/audit/tasks",  # 跳转到审核任务列表
                kuozhan_shuju=json.dumps({
                    "workflow_id": workflow_id,
                    "audit_type": workflow.shenhe_leixing,
                    "step_id": next_step.id,
                    "step_number": next_step.buzhou_bianhao
                }),
                created_by="system"
            )

            self.db.add(notification)
            self.db.commit()

        except Exception as e:
            print(f"发送下一步审核通知失败: {e}")
            import traceback
            traceback.print_exc()

    def _send_approval_notification(self, workflow_id: str, final_auditor_id: str):
        """发送审核通过通知给申请人"""
        try:
            # 获取审核流程
            workflow = self.db.query(ShenheLiucheng).filter(
                ShenheLiucheng.id == workflow_id,
                ShenheLiucheng.is_deleted == "N"
            ).first()

            if not workflow or not workflow.shenqing_ren_id:
                return

            # 获取最终审核人信息
            final_auditor = self.db.query(Yonghu).filter(
                Yonghu.id == final_auditor_id,
                Yonghu.is_deleted == "N"
            ).first()

            final_auditor_name = final_auditor.xingming if final_auditor else "未知用户"

            # 构建通知内容
            audit_type_map = {
                "hetong": "合同审核",
                "hetong_jine_xiuzheng": "合同金额修正审核",
                "baojia": "报价审核",
                "yinhang_huikuan": "银行汇款审核"
            }

            audit_type_name = audit_type_map.get(workflow.shenhe_leixing, workflow.shenhe_leixing)

            tongzhi_biaoti = f"【审核通过】{audit_type_name} - {workflow.liucheng_bianhao}"
            tongzhi_neirong = f"""
您的审核申请已通过：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
完成时间：{workflow.wancheng_shijian.strftime('%Y-%m-%d %H:%M:%S') if workflow.wancheng_shijian else '刚刚'}
最终审核人：{final_auditor_name}

您的申请已全部审核通过，可以继续后续操作。
            """.strip()

            # 创建通知
            notification = ZhifuTongzhi(
                jieshou_ren_id=workflow.shenqing_ren_id,
                tongzhi_leixing="audit_approved",
                tongzhi_biaoti=tongzhi_biaoti,
                tongzhi_neirong=tongzhi_neirong,
                youxian_ji="normal",
                fasong_shijian=datetime.now(),
                tongzhi_zhuangtai="unread",
                lianjie_url="/audit/tasks",  # 跳转到审核任务列表
                kuozhan_shuju=json.dumps({
                    "workflow_id": workflow_id,
                    "audit_type": workflow.shenhe_leixing,
                    "result": "approved"
                }),
                created_by="system"
            )

            self.db.add(notification)
            self.db.commit()

        except Exception as e:
            print(f"发送审核通过通知失败: {e}")
            import traceback
            traceback.print_exc()

    def _send_rejection_notification(self, workflow_id: str, auditor_id: str, rejection_reason: str = None):
        """发送审核拒绝通知给申请人"""
        try:
            # 获取审核流程
            workflow = self.db.query(ShenheLiucheng).filter(
                ShenheLiucheng.id == workflow_id,
                ShenheLiucheng.is_deleted == "N"
            ).first()

            if not workflow or not workflow.shenqing_ren_id:
                return

            # 获取审核人信息
            auditor = self.db.query(Yonghu).filter(
                Yonghu.id == auditor_id,
                Yonghu.is_deleted == "N"
            ).first()

            auditor_name = auditor.xingming if auditor else "未知用户"

            # 构建通知内容
            audit_type_map = {
                "hetong": "合同审核",
                "hetong_jine_xiuzheng": "合同金额修正审核",
                "baojia": "报价审核",
                "yinhang_huikuan": "银行汇款审核"
            }

            audit_type_name = audit_type_map.get(workflow.shenhe_leixing, workflow.shenhe_leixing)

            tongzhi_biaoti = f"【审核拒绝】{audit_type_name} - {workflow.liucheng_bianhao}"
            tongzhi_neirong = f"""
您的审核申请已被拒绝：

审核类型：{audit_type_name}
流程编号：{workflow.liucheng_bianhao}
申请时间：{workflow.shenqing_shijian.strftime('%Y-%m-%d %H:%M:%S')}
拒绝时间：{workflow.wancheng_shijian.strftime('%Y-%m-%d %H:%M:%S') if workflow.wancheng_shijian else '刚刚'}
审核人：{auditor_name}
拒绝原因：{rejection_reason or '无'}

如有疑问，请联系审核人了解详情。
            """.strip()

            # 创建通知
            notification = ZhifuTongzhi(
                jieshou_ren_id=workflow.shenqing_ren_id,
                tongzhi_leixing="audit_rejected",
                tongzhi_biaoti=tongzhi_biaoti,
                tongzhi_neirong=tongzhi_neirong,
                youxian_ji="high",
                fasong_shijian=datetime.now(),
                tongzhi_zhuangtai="unread",
                lianjie_url="/audit/tasks",  # 跳转到审核任务列表
                kuozhan_shuju=json.dumps({
                    "workflow_id": workflow_id,
                    "audit_type": workflow.shenhe_leixing,
                    "result": "rejected",
                    "rejection_reason": rejection_reason
                }),
                created_by="system"
            )

            self.db.add(notification)
            self.db.commit()

        except Exception as e:
            print(f"发送审核拒绝通知失败: {e}")
            import traceback
            traceback.print_exc()
