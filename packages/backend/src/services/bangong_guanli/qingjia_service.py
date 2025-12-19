"""
请假申请管理服务
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from fastapi import HTTPException
from datetime import datetime
import json

from models.bangong_guanli import QingjiaShenqing
from models.yonghu_guanli import Yonghu
from models.zhifu_guanli import ZhifuTongzhi
from schemas.bangong_guanli.qingjia_schemas import (
    QingjiaShenqingCreate,
    QingjiaShenqingUpdate,
    QingjiaShenqingResponse,
    QingjiaShenqingListParams
)
from services.shenhe_guanli import ShenheWorkflowEngine

class QingjiaService:
    """请假申请管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_shenqing_bianhao(self) -> str:
        """生成申请编号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(func.count(QingjiaShenqing.id)).filter(
            QingjiaShenqing.shenqing_bianhao.like(f"QJ{today}%"),
            QingjiaShenqing.is_deleted == "N"
        ).scalar()
        return f"QJ{today}{str(count + 1).zfill(4)}"
    
    def create_qingjia_shenqing(
        self, 
        shenqing_data: QingjiaShenqingCreate, 
        shenqing_ren_id: str
    ) -> QingjiaShenqingResponse:
        """创建请假申请"""
        shenqing_ren = self.db.query(Yonghu).filter(
            Yonghu.id == shenqing_ren_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not shenqing_ren:
            raise HTTPException(status_code=404, detail="申请人不存在")
        
        shenqing_bianhao = self._generate_shenqing_bianhao()
        
        qingjia_shenqing = QingjiaShenqing(
            shenqing_bianhao=shenqing_bianhao,
            shenqing_ren_id=shenqing_ren_id,
            **shenqing_data.model_dump(),
            created_by=shenqing_ren_id
        )
        
        self.db.add(qingjia_shenqing)
        self.db.commit()
        self.db.refresh(qingjia_shenqing)
        
        response_data = QingjiaShenqingResponse.model_validate(qingjia_shenqing)
        response_data.shenqing_ren_xingming = shenqing_ren.xingming
        
        return response_data
    
    def get_qingjia_shenqing_list(
        self, 
        params: QingjiaShenqingListParams
    ) -> Tuple[List[QingjiaShenqingResponse], int]:
        """获取请假申请列表"""
        query = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.is_deleted == "N"
        )
        
        if params.shenqing_ren_id:
            query = query.filter(QingjiaShenqing.shenqing_ren_id == params.shenqing_ren_id)
        
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    QingjiaShenqing.shenqing_bianhao.like(search_pattern),
                    QingjiaShenqing.qingjia_yuanyin.like(search_pattern)
                )
            )
        
        if params.shenhe_zhuangtai:
            query = query.filter(QingjiaShenqing.shenhe_zhuangtai == params.shenhe_zhuangtai)
        
        if params.qingjia_leixing:
            query = query.filter(QingjiaShenqing.qingjia_leixing == params.qingjia_leixing)
        
        total = query.count()
        query = query.order_by(desc(QingjiaShenqing.created_at))
        query = query.offset((params.page - 1) * params.size).limit(params.size)
        
        shenqing_list = query.all()
        
        shenqing_ren_ids = [s.shenqing_ren_id for s in shenqing_list]
        shenqing_ren_map = {}
        if shenqing_ren_ids:
            shenqing_ren_list = self.db.query(Yonghu).filter(
                Yonghu.id.in_(shenqing_ren_ids)
            ).all()
            shenqing_ren_map = {u.id: u.xingming for u in shenqing_ren_list}
        
        result = []
        for shenqing in shenqing_list:
            response_data = QingjiaShenqingResponse.model_validate(shenqing)
            response_data.shenqing_ren_xingming = shenqing_ren_map.get(shenqing.shenqing_ren_id)
            result.append(response_data)
        
        return result, total
    
    def get_qingjia_shenqing_by_id(self, shenqing_id: str) -> QingjiaShenqingResponse:
        """根据ID获取请假申请详情"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")
        
        shenqing_ren = self.db.query(Yonghu).filter(
            Yonghu.id == shenqing.shenqing_ren_id
        ).first()
        
        response_data = QingjiaShenqingResponse.model_validate(shenqing)
        if shenqing_ren:
            response_data.shenqing_ren_xingming = shenqing_ren.xingming
        
        return response_data
    
    def update_qingjia_shenqing(
        self, 
        shenqing_id: str, 
        update_data: QingjiaShenqingUpdate,
        updated_by: str
    ) -> QingjiaShenqingResponse:
        """更新请假申请"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")
        
        if shenqing.shenhe_zhuangtai not in ["daishehe"]:
            raise HTTPException(status_code=400, detail="只有待审核状态的申请才能修改")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(shenqing, key, value)
        
        shenqing.updated_by = updated_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(shenqing)
        
        return self.get_qingjia_shenqing_by_id(shenqing_id)
    
    def delete_qingjia_shenqing(self, shenqing_id: str, deleted_by: str) -> Dict[str, str]:
        """删除请假申请（软删除）"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")
        
        if shenqing.shenhe_zhuangtai not in ["daishehe"]:
            raise HTTPException(status_code=400, detail="只有待审核状态的申请才能删除")
        
        shenqing.is_deleted = "Y"
        shenqing.updated_by = deleted_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()

        return {"message": "删除成功"}

    def submit_for_approval(self, shenqing_id: str, submitted_by: str) -> Dict[str, str]:
        """提交审批"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")

        if shenqing.shenhe_zhuangtai != "daishehe":
            raise HTTPException(status_code=400, detail="该申请已提交审批")

        # 调用审批流程引擎
        workflow_engine = ShenheWorkflowEngine(self.db)

        trigger_data = {
            "qingjia_tianshu": shenqing.qingjia_tianshu,
            "qingjia_leixing": shenqing.qingjia_leixing,
            "shenqing_bianhao": shenqing.shenqing_bianhao
        }

        workflow_id = workflow_engine.trigger_audit(
            audit_type="qingjia",
            related_id=shenqing_id,
            trigger_data=trigger_data,
            applicant_id=submitted_by
        )

        if workflow_id:
            shenqing.shenhe_zhuangtai = "shenhezhong"
            shenqing.shenhe_liucheng_id = workflow_id
            shenqing.updated_by = submitted_by
            shenqing.updated_at = datetime.now()

            self.db.commit()

            self._send_submit_notification(shenqing, submitted_by)

            return {"message": "提交审批成功", "workflow_id": workflow_id}
        else:
            shenqing.shenhe_zhuangtai = "tongguo"
            shenqing.updated_by = submitted_by
            shenqing.updated_at = datetime.now()

            self.db.commit()

            return {"message": "无需审批，已自动通过"}

    def approve_application(self, shenqing_id: str, approver_id: str, shenhe_yijian: str = None) -> Dict[str, str]:
        """审批通过"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")

        if not shenqing.shenhe_liucheng_id:
            raise HTTPException(status_code=400, detail="该申请没有审批流程")

        workflow_engine = ShenheWorkflowEngine(self.db)

        action_data = {
            "shenhe_jieguo": "tongguo",
            "shenhe_yijian": shenhe_yijian or "同意"
        }

        is_completed = workflow_engine.process_audit_action(
            workflow_id=shenqing.shenhe_liucheng_id,
            auditor_id=approver_id,
            action_data=action_data
        )

        if is_completed:
            shenqing.shenhe_zhuangtai = "tongguo"
            shenqing.updated_by = approver_id
            shenqing.updated_at = datetime.now()

            self.db.commit()

            self._send_approval_notification(shenqing, approver_id, "tongguo")

            return {"message": "审批通过，流程已完成"}
        else:
            return {"message": "审批通过，进入下一审批步骤"}

    def reject_application(self, shenqing_id: str, approver_id: str, shenhe_yijian: str) -> Dict[str, str]:
        """审批拒绝"""
        shenqing = self.db.query(QingjiaShenqing).filter(
            QingjiaShenqing.id == shenqing_id,
            QingjiaShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="请假申请不存在")

        if not shenqing.shenhe_liucheng_id:
            raise HTTPException(status_code=400, detail="该申请没有审批流程")

        workflow_engine = ShenheWorkflowEngine(self.db)

        action_data = {
            "shenhe_jieguo": "jujue",
            "shenhe_yijian": shenhe_yijian
        }

        workflow_engine.process_audit_action(
            workflow_id=shenqing.shenhe_liucheng_id,
            auditor_id=approver_id,
            action_data=action_data
        )

        shenqing.shenhe_zhuangtai = "jujue"
        shenqing.updated_by = approver_id
        shenqing.updated_at = datetime.now()

        self.db.commit()

        self._send_approval_notification(shenqing, approver_id, "jujue")

        return {"message": "审批已拒绝"}

    def _send_submit_notification(self, shenqing: QingjiaShenqing, submitted_by: str):
        """发送提交通知"""
        try:
            notification = ZhifuTongzhi(
                jieshou_ren_id=submitted_by,
                tongzhi_leixing="qingjia_submit",
                tongzhi_biaoti="请假申请已提交",
                tongzhi_neirong=f"您的请假申请【{shenqing.shenqing_bianhao}】已提交审批，请等待审批结果。",
                tongzhi_zhuangtai="unread",
                youxian_ji="normal",
                fasong_shijian=datetime.now(),
                lianjie_url=f"/office/leave/detail/{shenqing.id}",
                kuozhan_shuju=json.dumps({"shenqing_id": shenqing.id, "shenqing_bianhao": shenqing.shenqing_bianhao}),
                created_by=submitted_by
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:

    def _send_approval_notification(self, shenqing: QingjiaShenqing, approver_id: str, result: str):
        """发送审批结果通知"""
        try:
            result_text = "已通过" if result == "tongguo" else "已拒绝"
            notification = ZhifuTongzhi(
                jieshou_ren_id=shenqing.shenqing_ren_id,
                tongzhi_leixing=f"qingjia_{result}",
                tongzhi_biaoti=f"请假申请{result_text}",
                tongzhi_neirong=f"您的请假申请【{shenqing.shenqing_bianhao}】{result_text}。",
                tongzhi_zhuangtai="unread",
                youxian_ji="high",
                fasong_shijian=datetime.now(),
                lianjie_url=f"/office/leave/detail/{shenqing.id}",
                kuozhan_shuju=json.dumps({"shenqing_id": shenqing.id, "shenqing_bianhao": shenqing.shenqing_bianhao}),
                created_by=approver_id
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
