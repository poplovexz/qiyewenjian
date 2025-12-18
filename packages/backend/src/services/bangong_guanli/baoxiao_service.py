"""
报销申请管理服务
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from fastapi import HTTPException
from datetime import datetime
import json

from models.bangong_guanli import BaoxiaoShenqing
from models.yonghu_guanli import Yonghu
from models.zhifu_guanli import ZhifuTongzhi, ZhifuLiushui
from schemas.bangong_guanli.baoxiao_schemas import (
    BaoxiaoShenqingCreate,
    BaoxiaoShenqingUpdate,
    BaoxiaoShenqingResponse,
    BaoxiaoShenqingListParams
)
from schemas.zhifu_guanli.zhifu_liushui_schemas import ZhifuLiushuiCreate
from services.shenhe_guanli import ShenheWorkflowEngine
from services.zhifu_guanli.zhifu_liushui_service import ZhifuLiushuiService
from decimal import Decimal


class BaoxiaoService:
    """报销申请管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_shenqing_bianhao(self) -> str:
        """生成申请编号"""
        today = datetime.now().strftime("%Y%m%d")
        # 查询今天已有的申请数量
        count = self.db.query(func.count(BaoxiaoShenqing.id)).filter(
            BaoxiaoShenqing.shenqing_bianhao.like(f"BX{today}%"),
            BaoxiaoShenqing.is_deleted == "N"
        ).scalar()
        
        # 生成编号：BX + 日期 + 4位序号
        return f"BX{today}{str(count + 1).zfill(4)}"
    
    def create_baoxiao_shenqing(
        self, 
        shenqing_data: BaoxiaoShenqingCreate, 
        shenqing_ren_id: str
    ) -> BaoxiaoShenqingResponse:
        """创建报销申请"""
        # 验证申请人是否存在
        shenqing_ren = self.db.query(Yonghu).filter(
            Yonghu.id == shenqing_ren_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not shenqing_ren:
            raise HTTPException(status_code=404, detail="申请人不存在")
        
        # 生成申请编号
        shenqing_bianhao = self._generate_shenqing_bianhao()
        
        # 创建报销申请
        baoxiao_shenqing = BaoxiaoShenqing(
            shenqing_bianhao=shenqing_bianhao,
            shenqing_ren_id=shenqing_ren_id,
            **shenqing_data.model_dump(),
            created_by=shenqing_ren_id
        )
        
        self.db.add(baoxiao_shenqing)
        self.db.commit()
        self.db.refresh(baoxiao_shenqing)
        
        # 构造响应数据
        response_data = BaoxiaoShenqingResponse.model_validate(baoxiao_shenqing)
        response_data.shenqing_ren_xingming = shenqing_ren.xingming
        
        return response_data
    
    def get_baoxiao_shenqing_list(
        self, 
        params: BaoxiaoShenqingListParams,
        current_user_id: Optional[str] = None
    ) -> Tuple[List[BaoxiaoShenqingResponse], int]:
        """获取报销申请列表"""
        query = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.is_deleted == "N"
        )
        
        # 如果指定了申请人，只查询该申请人的记录
        if params.shenqing_ren_id:
            query = query.filter(BaoxiaoShenqing.shenqing_ren_id == params.shenqing_ren_id)
        
        # 搜索条件
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    BaoxiaoShenqing.shenqing_bianhao.like(search_pattern),
                    BaoxiaoShenqing.baoxiao_yuanyin.like(search_pattern)
                )
            )
        
        # 筛选条件
        if params.shenhe_zhuangtai:
            query = query.filter(BaoxiaoShenqing.shenhe_zhuangtai == params.shenhe_zhuangtai)
        
        if params.baoxiao_leixing:
            query = query.filter(BaoxiaoShenqing.baoxiao_leixing == params.baoxiao_leixing)
        
        if params.kaishi_shijian:
            query = query.filter(BaoxiaoShenqing.baoxiao_shijian >= params.kaishi_shijian)
        
        if params.jieshu_shijian:
            query = query.filter(BaoxiaoShenqing.baoxiao_shijian <= params.jieshu_shijian)
        
        # 总数
        total = query.count()
        
        # 排序和分页
        query = query.order_by(desc(BaoxiaoShenqing.created_at))
        query = query.offset((params.page - 1) * params.size).limit(params.size)
        
        # 执行查询
        shenqing_list = query.all()
        
        # 获取申请人信息
        shenqing_ren_ids = [s.shenqing_ren_id for s in shenqing_list]
        shenqing_ren_map = {}
        if shenqing_ren_ids:
            shenqing_ren_list = self.db.query(Yonghu).filter(
                Yonghu.id.in_(shenqing_ren_ids)
            ).all()
            shenqing_ren_map = {u.id: u.xingming for u in shenqing_ren_list}
        
        # 构造响应数据
        result = []
        for shenqing in shenqing_list:
            response_data = BaoxiaoShenqingResponse.model_validate(shenqing)
            response_data.shenqing_ren_xingming = shenqing_ren_map.get(shenqing.shenqing_ren_id)
            result.append(response_data)
        
        return result, total
    
    def get_baoxiao_shenqing_by_id(self, shenqing_id: str) -> BaoxiaoShenqingResponse:
        """根据ID获取报销申请详情"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")
        
        # 获取申请人信息
        shenqing_ren = self.db.query(Yonghu).filter(
            Yonghu.id == shenqing.shenqing_ren_id
        ).first()
        
        response_data = BaoxiaoShenqingResponse.model_validate(shenqing)
        if shenqing_ren:
            response_data.shenqing_ren_xingming = shenqing_ren.xingming
        
        return response_data
    
    def update_baoxiao_shenqing(
        self, 
        shenqing_id: str, 
        update_data: BaoxiaoShenqingUpdate,
        updated_by: str
    ) -> BaoxiaoShenqingResponse:
        """更新报销申请"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")
        
        # 只有待审核状态才能修改
        if shenqing.shenhe_zhuangtai not in ["daishehe"]:
            raise HTTPException(status_code=400, detail="只有待审核状态的申请才能修改")
        
        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(shenqing, key, value)
        
        shenqing.updated_by = updated_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(shenqing)
        
        return self.get_baoxiao_shenqing_by_id(shenqing_id)
    
    def delete_baoxiao_shenqing(self, shenqing_id: str, deleted_by: str) -> Dict[str, str]:
        """删除报销申请（软删除）"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")
        
        # 只有待审核状态才能删除
        if shenqing.shenhe_zhuangtai not in ["daishehe"]:
            raise HTTPException(status_code=400, detail="只有待审核状态的申请才能删除")
        
        shenqing.is_deleted = "Y"
        shenqing.updated_by = deleted_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        
        return {"message": "删除成功"}
    
    def submit_for_approval(self, shenqing_id: str, submitted_by: str) -> Dict[str, str]:
        """提交审批"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")

        # 只有待审核状态才能提交
        if shenqing.shenhe_zhuangtai != "daishehe":
            raise HTTPException(status_code=400, detail="该申请已提交审批")

        # 调用审批流程引擎创建审批流程
        workflow_engine = ShenheWorkflowEngine(self.db)

        # 准备触发数据
        trigger_data = {
            "baoxiao_jine": float(shenqing.baoxiao_jine),
            "baoxiao_leixing": shenqing.baoxiao_leixing,
            "shenqing_bianhao": shenqing.shenqing_bianhao
        }

        # 触发审批流程
        workflow_id = workflow_engine.trigger_audit(
            audit_type="baoxiao",  # 报销审批类型
            related_id=shenqing_id,
            trigger_data=trigger_data,
            applicant_id=submitted_by
        )

        if workflow_id:
            # 更新申请状态和审批流程ID
            shenqing.shenhe_zhuangtai = "shenhezhong"
            shenqing.shenhe_liucheng_id = workflow_id
            shenqing.updated_by = submitted_by
            shenqing.updated_at = datetime.now()

            self.db.commit()

            # 发送通知给申请人
            self._send_submit_notification(shenqing, submitted_by)

            return {"message": "提交审批成功", "workflow_id": workflow_id}
        else:
            # 如果没有匹配的审批规则，直接通过
            shenqing.shenhe_zhuangtai = "tongguo"
            shenqing.updated_by = submitted_by
            shenqing.updated_at = datetime.now()

            self.db.commit()

            # 创建支付流水记录（报销支出）
            try:
                self._create_expense_liushui(shenqing, submitted_by)
            except Exception as e:
                # 流水创建失败不影响审批流程
                print(f"创建报销支出流水失败: {e}")
                import traceback
                traceback.print_exc()

            return {"message": "无需审批，已自动通过"}

    def approve_application(self, shenqing_id: str, approver_id: str, shenhe_yijian: str = None) -> Dict[str, str]:
        """审批通过"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")

        if not shenqing.shenhe_liucheng_id:
            raise HTTPException(status_code=400, detail="该申请没有审批流程")

        # 调用审批流程引擎处理审批
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
            # 审批流程完成，更新申请状态
            shenqing.shenhe_zhuangtai = "tongguo"
            shenqing.updated_by = approver_id
            shenqing.updated_at = datetime.now()

            self.db.commit()

            # 创建支付流水记录（报销支出）
            try:
                self._create_expense_liushui(shenqing, approver_id)
            except Exception as e:
                # 流水创建失败不影响审批流程
                print(f"创建报销支出流水失败: {e}")
                import traceback
                traceback.print_exc()

            # 发送通知给申请人
            self._send_approval_notification(shenqing, approver_id, "tongguo")

            return {"message": "审批通过，流程已完成"}
        else:
            return {"message": "审批通过，进入下一审批步骤"}

    def reject_application(self, shenqing_id: str, approver_id: str, shenhe_yijian: str) -> Dict[str, str]:
        """审批拒绝"""
        shenqing = self.db.query(BaoxiaoShenqing).filter(
            BaoxiaoShenqing.id == shenqing_id,
            BaoxiaoShenqing.is_deleted == "N"
        ).first()

        if not shenqing:
            raise HTTPException(status_code=404, detail="报销申请不存在")

        if not shenqing.shenhe_liucheng_id:
            raise HTTPException(status_code=400, detail="该申请没有审批流程")

        # 调用审批流程引擎处理审批
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

        # 更新申请状态
        shenqing.shenhe_zhuangtai = "jujue"
        shenqing.updated_by = approver_id
        shenqing.updated_at = datetime.now()

        self.db.commit()

        # 发送通知给申请人
        self._send_approval_notification(shenqing, approver_id, "jujue")

        return {"message": "审批已拒绝"}

    def _send_submit_notification(self, shenqing: BaoxiaoShenqing, submitted_by: str):
        """发送提交通知"""
        try:
            notification = ZhifuTongzhi(
                jieshou_ren_id=submitted_by,
                tongzhi_leixing="baoxiao_submit",
                tongzhi_biaoti="报销申请已提交",
                tongzhi_neirong=f"您的报销申请【{shenqing.shenqing_bianhao}】已提交审批，请等待审批结果。",
                tongzhi_zhuangtai="unread",
                youxian_ji="normal",
                fasong_shijian=datetime.now(),
                lianjie_url=f"/office/reimbursement/detail/{shenqing.id}",
                kuozhan_shuju=json.dumps({"shenqing_id": shenqing.id, "shenqing_bianhao": shenqing.shenqing_bianhao}),
                created_by=submitted_by
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            # 通知发送失败不影响主流程
            print(f"发送通知失败: {e}")

    def _send_approval_notification(self, shenqing: BaoxiaoShenqing, approver_id: str, result: str):
        """发送审批结果通知"""
        try:
            result_text = "已通过" if result == "tongguo" else "已拒绝"
            notification = ZhifuTongzhi(
                jieshou_ren_id=shenqing.shenqing_ren_id,
                tongzhi_leixing=f"baoxiao_{result}",
                tongzhi_biaoti=f"报销申请{result_text}",
                tongzhi_neirong=f"您的报销申请【{shenqing.shenqing_bianhao}】{result_text}。",
                tongzhi_zhuangtai="unread",
                youxian_ji="high",
                fasong_shijian=datetime.now(),
                lianjie_url=f"/office/reimbursement/detail/{shenqing.id}",
                kuozhan_shuju=json.dumps({"shenqing_id": shenqing.id, "shenqing_bianhao": shenqing.shenqing_bianhao}),
                created_by=approver_id
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            # 通知发送失败不影响主流程
            print(f"发送通知失败: {e}")

    def _create_expense_liushui(self, shenqing: BaoxiaoShenqing, approver_id: str):
        """创建报销支出流水记录"""
        # 检查是否已经创建过流水记录
        existing_liushui = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.baoxiao_shenqing_id == shenqing.id,
            ZhifuLiushui.is_deleted == "N"
        ).first()

        if existing_liushui:
            print(f"报销申请 {shenqing.shenqing_bianhao} 已有流水记录，跳过创建")
            return

        # 创建支付流水服务
        liushui_service = ZhifuLiushuiService(self.db)

        # 构建流水数据
        liushui_data = ZhifuLiushuiCreate(
            zhifu_dingdan_id=None,
            kehu_id=None,
            baoxiao_shenqing_id=shenqing.id,
            guanlian_leixing="baoxiao_shenqing",
            liushui_leixing="expense",
            jiaoyijine=shenqing.baoxiao_jine,
            shouxufei=Decimal('0.00'),
            shiji_shouru=-shenqing.baoxiao_jine,  # 支出为负数
            zhifu_fangshi="baoxiao",
            zhifu_zhanghu=shenqing.shenqing_ren.xingming if shenqing.shenqing_ren else "",
            jiaoyishijian=datetime.now(),
            daozhangjian=None,
            liushui_zhuangtai="success",
            duizhang_zhuangtai="pending",
            beizhu=f"报销申请：{shenqing.baoxiao_yuanyin}"
        )

        # 创建流水记录
        liushui_service.create_zhifu_liushui(liushui_data, "system")
        print(f"为报销申请 {shenqing.shenqing_bianhao} 创建支出流水记录成功")

