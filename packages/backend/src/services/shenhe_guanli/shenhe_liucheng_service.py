"""
审核流程管理服务
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException

from models.shenhe_guanli import ShenheLiucheng, ShenheJilu, ShenheGuize
from schemas.shenhe_guanli import (
    ShenheLiuchengResponse,
    ShenheLiuchengListParams,
    ShenheActionRequest
)


class ShenheLiuchengService:
    """审核流程管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_shenhe_liucheng_list(self, params: ShenheLiuchengListParams) -> Dict[str, Any]:
        """获取审核流程列表"""
        query = self.db.query(ShenheLiucheng).filter(ShenheLiucheng.is_deleted == "N")
        
        # 搜索条件
        if params.search:
            search_filter = or_(
                ShenheLiucheng.liucheng_bianhao.contains(params.search),
                ShenheLiucheng.shenqing_yuanyin.contains(params.search)
            )
            query = query.filter(search_filter)
        
        # 筛选条件
        if params.shenhe_leixing:
            query = query.filter(ShenheLiucheng.shenhe_leixing == params.shenhe_leixing)
        
        if params.shenhe_zhuangtai:
            query = query.filter(ShenheLiucheng.shenhe_zhuangtai == params.shenhe_zhuangtai)
        
        if params.shenqing_ren_id:
            query = query.filter(ShenheLiucheng.shenqing_ren_id == params.shenqing_ren_id)
        
        # 排序
        if params.sort_by:
            sort_column = getattr(ShenheLiucheng, params.sort_by, None)
            if sort_column:
                if params.sort_order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        
        # 分页
        total = query.count()
        offset = (params.page - 1) * params.size
        items = query.offset(offset).limit(params.size).all()
        
        return {
            "items": [self._to_response(item) for item in items],
            "total": total,
            "page": params.page,
            "size": params.size,
            "pages": (total + params.size - 1) // params.size
        }
    
    def get_shenhe_liucheng_by_id(self, liucheng_id: str) -> ShenheLiuchengResponse:
        """根据ID获取审核流程详情"""
        liucheng = self.db.query(ShenheLiucheng).options(
            joinedload(ShenheLiucheng.shenhe_jilu_list),
            joinedload(ShenheLiucheng.chufa_guize)
        ).filter(
            ShenheLiucheng.id == liucheng_id,
            ShenheLiucheng.is_deleted == "N"
        ).first()
        
        if not liucheng:
            raise HTTPException(status_code=404, detail="审核流程不存在")
        
        return self._to_response(liucheng)
    
    def get_pending_audits_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户待审核的任务"""
        # 查询用户待处理的审核记录
        pending_records = self.db.query(ShenheJilu).join(
            ShenheLiucheng, ShenheJilu.liucheng_id == ShenheLiucheng.id
        ).filter(
            ShenheJilu.shenhe_ren_id == user_id,
            ShenheJilu.jilu_zhuangtai == "daichuli",
            ShenheJilu.is_deleted == "N",
            ShenheLiucheng.shenhe_zhuangtai == "shenhzhong",
            ShenheLiucheng.is_deleted == "N"
        ).all()
        
        result = []
        for record in pending_records:
            workflow = record.shenhe_liucheng
            
            # 获取关联的业务对象信息
            related_info = self._get_related_object_info(workflow.shenhe_leixing, workflow.guanlian_id)
            
            result.append({
                "workflow_id": workflow.id,
                "step_id": record.id,
                "workflow_number": workflow.liucheng_bianhao,
                "audit_type": workflow.shenhe_leixing,
                "related_id": workflow.guanlian_id,
                "related_info": related_info,
                "step_number": record.buzhou_bianhao,
                "step_name": record.buzhou_mingcheng,
                "expected_time": record.qiwang_chuli_shijian,
                "created_at": workflow.created_at,
                "applicant_reason": workflow.shenqing_yuanyin
            })
        
        return result
    
    def process_audit_action(self, workflow_id: str, step_id: str, action_data: ShenheActionRequest, auditor_id: str) -> bool:
        """处理审核操作"""
        from .shenhe_workflow_engine import ShenheWorkflowEngine
        
        engine = ShenheWorkflowEngine(self.db)
        action_dict = {
            "shenhe_jieguo": action_data.shenhe_jieguo,
            "shenhe_yijian": action_data.shenhe_yijian,
            "fujian_lujing": action_data.fujian_lujing,
            "fujian_miaoshu": action_data.fujian_miaoshu
        }
        
        return engine.process_audit_action(workflow_id, step_id, action_dict, auditor_id)
    
    def get_audit_history_by_related_id(self, audit_type: str, related_id: str) -> List[ShenheLiuchengResponse]:
        """根据关联ID获取审核历史"""
        workflows = self.db.query(ShenheLiucheng).options(
            joinedload(ShenheLiucheng.shenhe_jilu_list)
        ).filter(
            ShenheLiucheng.shenhe_leixing == audit_type,
            ShenheLiucheng.guanlian_id == related_id,
            ShenheLiucheng.is_deleted == "N"
        ).order_by(desc(ShenheLiucheng.created_at)).all()
        
        return [self._to_response(workflow) for workflow in workflows]
    
    def cancel_audit_workflow(self, workflow_id: str, user_id: str, reason: str) -> bool:
        """取消审核流程"""
        workflow = self.db.query(ShenheLiucheng).filter(
            ShenheLiucheng.id == workflow_id,
            ShenheLiucheng.is_deleted == "N"
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="审核流程不存在")
        
        # 检查权限（只有申请人可以取消）
        if workflow.shenqing_ren_id != user_id:
            raise HTTPException(status_code=403, detail="无权限取消此审核流程")
        
        # 检查状态（只有进行中的流程可以取消）
        if workflow.shenhe_zhuangtai != "shenhzhong":
            raise HTTPException(status_code=400, detail="只能取消进行中的审核流程")
        
        # 更新流程状态
        workflow.shenhe_zhuangtai = "chexiao"
        workflow.wancheng_shijian = datetime.now()
        workflow.beizhu = f"用户取消：{reason}"
        workflow.updated_at = datetime.now()
        
        # 更新所有待处理的审核记录
        pending_records = self.db.query(ShenheJilu).filter(
            ShenheJilu.liucheng_id == workflow_id,
            ShenheJilu.jilu_zhuangtai == "daichuli",
            ShenheJilu.is_deleted == "N"
        ).all()
        
        for record in pending_records:
            record.jilu_zhuangtai = "yitiaoguo"
            record.shenhe_yijian = "流程已取消"
            record.updated_at = datetime.now()
        
        self.db.commit()
        return True
    
    def _get_related_object_info(self, audit_type: str, related_id: str) -> Dict[str, Any]:
        """获取关联业务对象信息"""
        if audit_type == "hetong":
            from models.hetong_guanli import Hetong
            hetong = self.db.query(Hetong).filter(
                Hetong.id == related_id,
                Hetong.is_deleted == "N"
            ).first()
            
            if hetong:
                return {
                    "type": "合同",
                    "name": hetong.hetong_mingcheng,
                    "number": hetong.hetong_bianhao,
                    "status": hetong.hetong_zhuangtai
                }
        
        elif audit_type == "baojia":
            from models.xiansuo_guanli import XiansuoBaojia
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == related_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()
            
            if baojia:
                return {
                    "type": "报价",
                    "name": baojia.baojia_mingcheng,
                    "number": baojia.baojia_bianma,
                    "status": baojia.baojia_zhuangtai,
                    "amount": float(baojia.zongji_jine)
                }
        
        return {"type": "未知", "name": "未知对象"}
    
    def _to_response(self, liucheng: ShenheLiucheng) -> ShenheLiuchengResponse:
        """转换为响应模型"""
        return ShenheLiuchengResponse(
            id=liucheng.id,
            liucheng_bianhao=liucheng.liucheng_bianhao,
            shenhe_leixing=liucheng.shenhe_leixing,
            guanlian_id=liucheng.guanlian_id,
            shenhe_zhuangtai=liucheng.shenhe_zhuangtai,
            chufa_guize_id=liucheng.chufa_guize_id,
            dangqian_buzhou=liucheng.dangqian_buzhou,
            zonggong_buzhou=liucheng.zonggong_buzhou,
            shenqing_ren_id=liucheng.shenqing_ren_id,
            shenqing_yuanyin=liucheng.shenqing_yuanyin,
            shenqing_shijian=liucheng.shenqing_shijian,
            wancheng_shijian=liucheng.wancheng_shijian,
            beizhu=liucheng.beizhu,
            created_at=liucheng.created_at,
            updated_at=liucheng.updated_at,
            created_by=liucheng.created_by
        )
