"""
审核工作流模板服务
用于管理工作流模板配置
"""
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from fastapi import HTTPException

from models.shenhe_guanli import ShenheGuize
from schemas.shenhe_guanli.audit_workflow_schemas import (
    AuditWorkflowCreate,
    AuditWorkflowUpdate,
    AuditWorkflowResponse,
    AuditWorkflowListParams
)


class AuditWorkflowService:
    """审核工作流模板服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_workflow_template(self, workflow_data: AuditWorkflowCreate, created_by: str) -> AuditWorkflowResponse:
        """创建工作流模板"""
        # 检查工作流名称是否重复
        existing_workflow = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_mingcheng == f"工作流模板-{workflow_data.workflow_name}",
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if existing_workflow:
            raise HTTPException(status_code=400, detail="工作流名称已存在")
        
        # 将工作流步骤转换为审核流程配置格式
        steps_config = {
            "steps": [
                {
                    "step": step.step_order,
                    "name": step.step_name,
                    "approver_user_id": getattr(step, 'approver_user_id', None),  # 新增：用户ID
                    "approver_role": getattr(step, 'approver_role', None),  # 保留：角色（兼容）
                    "description": step.description,
                    "expected_time": step.expected_time,
                    "is_required": step.is_required
                }
                for step in workflow_data.steps
            ]
        }
        
        # 创建触发条件配置
        trigger_config = {
            "type": "workflow_template",
            "audit_type": workflow_data.audit_type
        }
        
        # 使用ShenheGuize表存储工作流模板
        workflow_template = ShenheGuize(
            id=str(uuid.uuid4()),
            guize_mingcheng=f"工作流模板-{workflow_data.workflow_name}",
            guize_leixing="workflow_template",
            chufa_tiaojian=json.dumps(trigger_config, ensure_ascii=False),
            shenhe_liucheng_peizhi=json.dumps(steps_config, ensure_ascii=False),
            shi_qiyong="Y" if workflow_data.status == "active" else "N",
            paixu=0,
            guize_miaoshu=workflow_data.description,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        self.db.add(workflow_template)
        self.db.commit()
        self.db.refresh(workflow_template)
        
        return self._to_workflow_response(workflow_template, workflow_data.workflow_name)
    
    def get_workflow_list(self, params: AuditWorkflowListParams) -> Dict[str, Any]:
        """获取工作流模板列表"""
        query = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == "workflow_template",
            ShenheGuize.is_deleted == "N"
        )
        
        # 搜索条件
        if params.search:
            search_filter = or_(
                ShenheGuize.guize_mingcheng.contains(params.search),
                ShenheGuize.guize_miaoshu.contains(params.search)
            )
            query = query.filter(search_filter)
        
        # 状态筛选
        if params.status:
            status_value = "Y" if params.status == "active" else "N"
            query = query.filter(ShenheGuize.shi_qiyong == status_value)
        
        # 审核类型筛选
        if params.audit_type:
            query = query.filter(ShenheGuize.chufa_tiaojian.contains(f'"audit_type": "{params.audit_type}"'))
        
        # 排序
        query = query.order_by(desc(ShenheGuize.created_at))
        
        # 分页
        total = query.count()
        offset = (params.page - 1) * params.size
        items = query.offset(offset).limit(params.size).all()
        
        return {
            "items": [self._to_workflow_response(item) for item in items],
            "total": total,
            "page": params.page,
            "size": params.size,
            "pages": (total + params.size - 1) // params.size
        }
    
    def get_workflow_by_id(self, workflow_id: str) -> AuditWorkflowResponse:
        """根据ID获取工作流模板"""
        workflow = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == workflow_id,
            ShenheGuize.guize_leixing == "workflow_template",
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流模板不存在")
        
        return self._to_workflow_response(workflow)
    
    def update_workflow_template(self, workflow_id: str, workflow_data: AuditWorkflowUpdate, updated_by: str) -> AuditWorkflowResponse:
        """更新工作流模板"""
        workflow = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == workflow_id,
            ShenheGuize.guize_leixing == "workflow_template",
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流模板不存在")
        
        # 更新字段
        if workflow_data.workflow_name:
            workflow.guize_mingcheng = f"工作流模板-{workflow_data.workflow_name}"
        
        if workflow_data.description is not None:
            workflow.guize_miaoshu = workflow_data.description
        
        if workflow_data.status:
            workflow.shi_qiyong = "Y" if workflow_data.status == "active" else "N"
        
        if workflow_data.steps:
            steps_config = {
                "steps": [
                    {
                        "step": step.step_order,
                        "name": step.step_name,
                        "approver_user_id": getattr(step, 'approver_user_id', None),  # 新增：用户ID
                        "approver_role": getattr(step, 'approver_role', None),  # 保留：角色（兼容）
                        "description": step.description,
                        "expected_time": step.expected_time,
                        "is_required": step.is_required
                    }
                    for step in workflow_data.steps
                ]
            }
            workflow.shenhe_liucheng_peizhi = json.dumps(steps_config, ensure_ascii=False)
        
        if workflow_data.audit_type:
            trigger_config = json.loads(workflow.chufa_tiaojian)
            trigger_config["audit_type"] = workflow_data.audit_type
            workflow.chufa_tiaojian = json.dumps(trigger_config, ensure_ascii=False)
        
        workflow.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return self._to_workflow_response(workflow, workflow_data.workflow_name)
    
    def delete_workflow_template(self, workflow_id: str) -> bool:
        """删除工作流模板"""
        workflow = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == workflow_id,
            ShenheGuize.guize_leixing == "workflow_template",
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流模板不存在")
        
        workflow.is_deleted = "Y"
        workflow.updated_at = datetime.now()
        
        self.db.commit()
        return True
    
    @staticmethod
    def _to_workflow_response(workflow: ShenheGuize, workflow_name: str = None) -> AuditWorkflowResponse:
        """转换为工作流响应模型"""
        # 解析流程配置
        try:
            steps_config = json.loads(workflow.shenhe_liucheng_peizhi) if isinstance(workflow.shenhe_liucheng_peizhi, str) else workflow.shenhe_liucheng_peizhi
            steps = steps_config.get("steps", [])
        except (json.JSONDecodeError, TypeError, AttributeError):
            steps = []

        # 解析触发条件获取审核类型
        try:
            trigger_config = json.loads(workflow.chufa_tiaojian) if isinstance(workflow.chufa_tiaojian, str) else workflow.chufa_tiaojian
            audit_type = trigger_config.get("audit_type", "")
        except (json.JSONDecodeError, TypeError, AttributeError):
            audit_type = ""

        # 提取工作流名称
        if not workflow_name:
            workflow_name = workflow.guize_mingcheng.replace("工作流模板-", "") if workflow.guize_mingcheng.startswith("工作流模板-") else workflow.guize_mingcheng

        return AuditWorkflowResponse(
            id=workflow.id,
            workflow_name=workflow_name,
            audit_type=audit_type,
            description=workflow.guize_miaoshu,
            status="active" if workflow.shi_qiyong == "Y" else "inactive",
            steps=steps,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
