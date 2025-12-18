"""
合同服务层
"""
import re
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException

from models.hetong_guanli import Hetong, HetongMoban, HetongJineBiangeng
from models.xiansuo_guanli import XiansuoBaojia
from models.kehu_guanli import Kehu
from models.fuwu_guanli import FuwuGongdan
from schemas.hetong_guanli import (
    HetongCreate,
    HetongUpdate,
    HetongResponse,
    HetongListResponse,
    HetongPreviewRequest,
    HetongPreviewResponse,
    HetongSignRequest
)
from core.events import event_bus


class HetongService:
    """合同服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_hetong(self, hetong_data: HetongCreate, created_by: str) -> HetongResponse:
        """创建合同"""
        # 验证合同编号唯一性
        existing_hetong = self.db.query(Hetong).filter(
            Hetong.hetong_bianhao == hetong_data.hetong_bianhao,
            Hetong.is_deleted == "N"
        ).first()
        
        if existing_hetong:
            raise HTTPException(status_code=400, detail="合同编号已存在")
        
        # 验证客户存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == hetong_data.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 验证合同模板存在
        moban = self.db.query(HetongMoban).filter(
            HetongMoban.id == hetong_data.hetong_moban_id,
            HetongMoban.is_deleted == "N"
        ).first()
        if not moban:
            raise HTTPException(status_code=404, detail="合同模板不存在")
        
        # 如果有报价ID，验证报价存在且已确认
        if hetong_data.baojia_id:
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == hetong_data.baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()
            if not baojia:
                raise HTTPException(status_code=404, detail="报价不存在")
            if baojia.baojia_zhuangtai != "accepted":
                raise HTTPException(status_code=400, detail="只能基于已确认的报价创建合同")
        
        # 创建合同
        hetong = Hetong(
            **hetong_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(hetong)
        self.db.commit()
        self.db.refresh(hetong)
        
        # 发布合同创建事件
        event_bus.publish("hetong_created", {
            "hetong_id": hetong.id,
            "hetong_bianhao": hetong.hetong_bianhao,
            "kehu_id": hetong.kehu_id,
            "baojia_id": hetong.baojia_id,
            "created_by": created_by
        })
        
        return HetongResponse.model_validate(hetong)
    
    def create_hetong_from_baojia(self, baojia_id: str, created_by: str) -> HetongResponse:
        """基于报价自动生成合同"""
        # 获取报价信息
        baojia = self.db.query(XiansuoBaojia).filter(
            XiansuoBaojia.id == baojia_id,
            XiansuoBaojia.is_deleted == "N"
        ).first()
        
        if not baojia:
            raise HTTPException(status_code=404, detail="报价不存在")
        
        if baojia.baojia_zhuangtai != "accepted":
            raise HTTPException(status_code=400, detail="只能基于已确认的报价生成合同")
        
        # 检查是否已经生成过合同
        existing_hetong = self.db.query(Hetong).filter(
            Hetong.baojia_id == baojia_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if existing_hetong:
            raise HTTPException(status_code=400, detail="该报价已经生成过合同")
        
        # 获取线索信息
        xiansuo = baojia.xiansuo
        if not xiansuo:
            raise HTTPException(status_code=404, detail="报价关联的线索不存在")
        
        # 获取客户信息
        kehu = self.db.query(Kehu).filter(
            Kehu.id == xiansuo.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 获取默认的代理记账合同模板
        moban = self.db.query(HetongMoban).filter(
            HetongMoban.hetong_leixing == "daili_jizhang",
            HetongMoban.shi_dangqian_banben == "Y",
            HetongMoban.moban_zhuangtai == "active",
            HetongMoban.is_deleted == "N"
        ).first()
        
        if not moban:
            raise HTTPException(status_code=404, detail="未找到可用的代理记账合同模板")
        
        # 生成合同编号
        hetong_bianhao = self._generate_hetong_bianhao()
        
        # 生成合同名称
        hetong_mingcheng = f"{kehu.gongsi_mingcheng}代理记账服务合同"
        
        # 基于模板和报价数据生成合同内容
        hetong_neirong = self._generate_hetong_content_from_baojia(moban, baojia, kehu)
        
        # 设置合同到期日期（默认1年）
        daoqi_riqi = datetime.now() + timedelta(days=365)
        
        # 创建合同数据
        hetong_data = HetongCreate(
            kehu_id=kehu.id,
            hetong_moban_id=moban.id,
            baojia_id=baojia_id,
            hetong_bianhao=hetong_bianhao,
            hetong_mingcheng=hetong_mingcheng,
            hetong_neirong=hetong_neirong,
            hetong_zhuangtai="draft",
            daoqi_riqi=daoqi_riqi,
            hetong_laiyuan="auto_from_quote",
            zidong_shengcheng="Y"
        )

        # 创建合同
        hetong_response = self.create_hetong(hetong_data, created_by)

        # 设置支付金额（从报价中获取）
        hetong = self.db.query(Hetong).filter(Hetong.id == hetong_response.id).first()
        if hetong and baojia.baojia_jine:
            hetong.payment_amount = str(baojia.baojia_jine)
            hetong.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(hetong)
            hetong_response = HetongResponse.model_validate(hetong)

        return hetong_response
    
    @staticmethod
    def _generate_hetong_bianhao() -> str:
        """生成合同编号"""
        from datetime import datetime
        import random
        import string
        
        now = datetime.now()
        # 使用年月日时分秒
        timestamp = now.strftime('%Y%m%d%H%M%S')
        # 添加3位随机字符
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return f"HT{timestamp}{random_suffix}"
    
    @staticmethod
    def _generate_hetong_content_from_baojia(moban: HetongMoban, baojia: XiansuoBaojia, kehu: Kehu) -> str:
        """基于模板和报价生成合同内容"""
        content = moban.moban_neirong
        
        # 准备变量值
        bianliang_zhis = {
            "客户名称": kehu.gongsi_mingcheng,
            "客户联系人": kehu.faren_xingming or "",
            "客户电话": kehu.lianxi_dianhua or "",
            "客户地址": kehu.lianxi_dizhi or "",
            "报价编码": baojia.baojia_bianma,
            "报价总金额": str(baojia.zongji_jine),
            "服务期限": "一年",
            "签约日期": datetime.now().strftime('%Y年%m月%d日')
        }
        
        # 添加报价项目信息
        if baojia.xiangmu_list:
            xiangmu_list = []
            for xiangmu in baojia.xiangmu_list:
                xiangmu_list.append(f"{xiangmu.xiangmu_mingcheng}：{xiangmu.danjia}元")
            bianliang_zhis["服务项目"] = "；".join(xiangmu_list)
        else:
            bianliang_zhis["服务项目"] = "代理记账服务"
        
        # 替换模板中的变量
        def replace_variable(match):
            var_name = match.group(1).strip()
            return str(bianliang_zhis.get(var_name, f"{{{{ {var_name} }}}}"))
        
        # 使用正则表达式替换变量
        content = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_variable, content)
        
        return content

    def get_hetong_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        hetong_zhuangtai: Optional[str] = None,
        kehu_id: Optional[str] = None,
        hetong_laiyuan: Optional[str] = None
    ) -> HetongListResponse:
        """获取合同列表"""
        query = self.db.query(Hetong).filter(Hetong.is_deleted == "N")

        # 预加载关联对象以避免N+1查询问题
        query = query.options(
            joinedload(Hetong.kehu),
            joinedload(Hetong.hetong_moban)
        )

        # 搜索条件
        if search:
            search_filter = or_(
                Hetong.hetong_bianhao.contains(search),
                Hetong.hetong_mingcheng.contains(search)
            )
            query = query.filter(search_filter)

        # 筛选条件
        if hetong_zhuangtai:
            query = query.filter(Hetong.hetong_zhuangtai == hetong_zhuangtai)

        if kehu_id:
            query = query.filter(Hetong.kehu_id == kehu_id)

        if hetong_laiyuan:
            query = query.filter(Hetong.hetong_laiyuan == hetong_laiyuan)

        # 排序
        query = query.order_by(Hetong.created_at.desc())

        # 分页
        total = query.count()
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()

        # 批量查询工单状态
        hetong_ids = [item.id for item in items]
        gongdan_hetong_ids = set()
        if hetong_ids:
            gongdan_query = self.db.query(FuwuGongdan.hetong_id).filter(
                FuwuGongdan.hetong_id.in_(hetong_ids),
                FuwuGongdan.is_deleted == "N"
            ).distinct()
            gongdan_hetong_ids = {row[0] for row in gongdan_query.all()}

        # 转换为响应模型并设置has_service_order
        response_items = []
        for item in items:
            response_item = HetongResponse.model_validate(item)
            response_item.has_service_order = item.id in gongdan_hetong_ids
            response_items.append(response_item)

        return HetongListResponse(
            total=total,
            items=response_items,
            page=page,
            size=size
        )

    def get_hetong_by_id(self, hetong_id: str) -> HetongResponse:
        """根据ID获取合同"""
        hetong = self.db.query(Hetong).options(
            joinedload(Hetong.kehu),
            joinedload(Hetong.hetong_moban)
        ).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        return HetongResponse.model_validate(hetong)

    def update_hetong(self, hetong_id: str, hetong_data: HetongUpdate) -> HetongResponse:
        """更新合同"""
        hetong = self.db.query(Hetong).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        # 验证合同编号唯一性（如果要更新编号）
        if hetong_data.hetong_bianhao and hetong_data.hetong_bianhao != hetong.hetong_bianhao:
            existing_hetong = self.db.query(Hetong).filter(
                Hetong.hetong_bianhao == hetong_data.hetong_bianhao,
                Hetong.id != hetong_id,
                Hetong.is_deleted == "N"
            ).first()

            if existing_hetong:
                raise HTTPException(status_code=400, detail="合同编号已存在")

        # 检查是否有金额变更
        original_amount = None
        new_amount = None

        # 从报价获取原始金额
        if hetong.baojia_id:
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == hetong.baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()
            if baojia:
                original_amount = float(baojia.zongji_jine)

        # 检查是否有金额字段更新（这里需要根据实际的金额字段名调整）
        amount_changed = False
        if hasattr(hetong_data, 'hetong_jine') and hetong_data.hetong_jine is not None:
            new_amount = float(hetong_data.hetong_jine)
            if original_amount and new_amount != original_amount:
                amount_changed = True

        # 更新字段
        update_data = hetong_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hetong, field, value)

        hetong.updated_at = datetime.now()

        # 如果金额发生变更，触发审核流程
        if amount_changed and original_amount and new_amount:
            workflow_id = self._trigger_amount_change_audit(
                hetong_id=hetong.id,
                original_amount=original_amount,
                new_amount=new_amount,
                change_reason=getattr(hetong_data, 'change_reason', '合同金额调整'),
                applicant_id=getattr(hetong_data, 'updated_by', 'system')
            )

            if workflow_id:
                # 如果触发了审核，将合同状态设为待审核
                hetong.hetong_zhuangtai = "pending"

        self.db.commit()
        self.db.refresh(hetong)

        return HetongResponse.model_validate(hetong)

    def delete_hetong(self, hetong_id: str) -> bool:
        """删除合同（软删除）"""
        hetong = self.db.query(Hetong).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        # 检查合同状态，已签署的合同不能删除
        if hetong.hetong_zhuangtai == "signed":
            raise HTTPException(status_code=400, detail="已签署的合同不能删除")

        # 检查合同状态，已作废的合同不能删除
        if hetong.hetong_zhuangtai == "voided":
            raise HTTPException(status_code=400, detail="已作废的合同不能删除，只能保留用于历史记录")

        hetong.is_deleted = "Y"
        hetong.updated_at = datetime.now()
        self.db.commit()

        return True

    def void_hetong(self, hetong_id: str, void_reason: str, voided_by: str) -> HetongResponse:
        """作废合同"""
        from sqlalchemy.orm import joinedload

        hetong = self.db.query(Hetong).options(
            joinedload(Hetong.kehu),
            joinedload(Hetong.hetong_moban)
        ).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        # 检查合同状态，已作废的合同不能再次作废
        if hetong.hetong_zhuangtai == "voided":
            raise HTTPException(status_code=400, detail="合同已经是作废状态")

        # 更新合同状态为作废
        hetong.hetong_zhuangtai = "voided"
        # 将作废信息记录在签名备注中
        void_info = f"作废原因: {void_reason}\n作废时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n作废人: {voided_by}"
        if hetong.qianming_beizhu:
            hetong.qianming_beizhu = f"{void_info}\n\n{hetong.qianming_beizhu}"
        else:
            hetong.qianming_beizhu = void_info
        hetong.updated_at = datetime.now()
        hetong.updated_by = voided_by

        self.db.commit()
        self.db.refresh(hetong)

        return HetongResponse.model_validate(hetong)

    def preview_hetong(self, preview_request: HetongPreviewRequest) -> HetongPreviewResponse:
        """预览合同内容"""
        # 获取合同模板
        moban = self.db.query(HetongMoban).filter(
            HetongMoban.id == preview_request.hetong_moban_id,
            HetongMoban.is_deleted == "N"
        ).first()

        if not moban:
            raise HTTPException(status_code=404, detail="合同模板不存在")

        content = moban.moban_neirong
        bianliang_zhis = preview_request.bianliang_zhis or {}

        # 如果提供了报价ID，自动填充报价相关变量
        if preview_request.baojia_id:
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == preview_request.baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()

            if baojia and baojia.xiansuo:
                kehu = self.db.query(Kehu).filter(
                    Kehu.id == baojia.xiansuo.kehu_id,
                    Kehu.is_deleted == "N"
                ).first()

                if kehu:
                    # 自动填充客户和报价信息
                    auto_vars = {
                        "客户名称": kehu.kehu_mingcheng,
                        "客户联系人": kehu.lianxi_ren or "",
                        "客户电话": kehu.lianxi_dianhua or "",
                        "客户地址": kehu.kehu_dizhi or "",
                        "报价编码": baojia.baojia_bianma,
                        "报价总金额": str(baojia.zongjine),
                        "签约日期": datetime.now().strftime('%Y年%m月%d日')
                    }

                    # 合并变量（用户提供的变量优先）
                    bianliang_zhis = {**auto_vars, **bianliang_zhis}

        # 提取模板中的所有变量
        bianliang_list = list(set(re.findall(r'\{\{\s*([^}]+)\s*\}\}', content)))

        # 替换变量
        def replace_variable(match):
            var_name = match.group(1).strip()
            return str(bianliang_zhis.get(var_name, f"{{{{ {var_name} }}}}"))

        content = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_variable, content)

        return HetongPreviewResponse(
            hetong_neirong=content,
            bianliang_list=bianliang_list
        )

    def sign_hetong(self, hetong_id: str, sign_request: HetongSignRequest, signer_id: str, signer_ip: str) -> HetongResponse:
        """签署合同"""
        hetong = self.db.query(Hetong).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        # 检查合同状态
        if hetong.hetong_zhuangtai not in ["draft", "approved"]:
            raise HTTPException(status_code=400, detail="只有草稿或已审批的合同才能签署")

        # 更新签署信息
        now = datetime.now()
        hetong.hetong_zhuangtai = "signed"
        hetong.qianshu_riqi = now
        hetong.qianming_ren_id = signer_id
        hetong.qianming_shijian = now
        hetong.qianming_ip = signer_ip
        hetong.qianming_beizhu = sign_request.qianming_beizhu
        hetong.shengxiao_riqi = now  # 签署后立即生效
        hetong.updated_at = now

        self.db.commit()
        self.db.refresh(hetong)

        # 发布合同签署事件
        event_bus.publish("hetong_signed", {
            "hetong_id": hetong.id,
            "hetong_bianhao": hetong.hetong_bianhao,
            "kehu_id": hetong.kehu_id,
            "signer_id": signer_id,
            "signed_at": now.isoformat()
        })

        return HetongResponse.model_validate(hetong)

    def get_hetong_by_baojia_id(self, baojia_id: str) -> Optional[HetongResponse]:
        """根据报价ID获取合同"""
        hetong = self.db.query(Hetong).filter(
            Hetong.baojia_id == baojia_id,
            Hetong.is_deleted == "N"
        ).first()

        if hetong:
            return HetongResponse.model_validate(hetong)
        return None

    def _trigger_amount_change_audit(self, hetong_id: str, original_amount: float,
                                   new_amount: float, change_reason: str, applicant_id: str) -> str:
        """触发合同金额变更审核"""
        try:
            from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine

            # 创建金额变更记录
            change_record = HetongJineBiangeng(
                id=str(uuid.uuid4()),
                hetong_id=hetong_id,
                yuanshi_jine=original_amount,
                xiuzheng_jine=new_amount,
                biangeng_jine=new_amount - original_amount,
                biangeng_bili=((new_amount - original_amount) / original_amount) * 100 if original_amount > 0 else 0,
                biangeng_yuanyin=change_reason,
                biangeng_ren_id=applicant_id,
                biangeng_shijian=datetime.now(),
                biangeng_zhuangtai="daishehe",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_deleted="N"
            )

            self.db.add(change_record)
            self.db.flush()  # 获取ID但不提交

            # 触发审核工作流
            engine = ShenheWorkflowEngine(self.db)
            trigger_data = {
                "original_amount": original_amount,
                "new_amount": new_amount,
                "change_percentage": abs(((original_amount - new_amount) / original_amount) * 100) if original_amount > 0 else 0,
                "reason": change_reason
            }

            workflow_id = engine.trigger_audit(
                audit_type="hetong",
                related_id=hetong_id,
                trigger_data=trigger_data,
                applicant_id=applicant_id
            )

            if workflow_id:
                # 关联审核流程ID
                change_record.shenhe_liucheng_id = workflow_id
                self.db.commit()
                return workflow_id
            else:
                # 如果不需要审核，直接通过
                change_record.biangeng_zhuangtai = "tongguo"
                self.db.commit()
                return None

        except Exception as e:
            self.db.rollback()
            # 记录错误但不阻止合同更新
            print(f"触发审核失败: {e}")
            return None

    def create_hetong_from_quote_direct(self, baojia_id: str, created_by: str,
                                      custom_amount: float = None, change_reason: str = None) -> HetongResponse:
        """直接从报价生成合同（支持金额修改）"""
        # 先调用原有的生成方法
        hetong_response = self.create_hetong_from_baojia(baojia_id, created_by)

        # 如果指定了自定义金额且与原金额不同，触发审核
        if custom_amount is not None:
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()

            if baojia and float(baojia.zongji_jine) != custom_amount:
                # 更新合同金额并触发审核
                hetong = self.db.query(Hetong).filter(
                    Hetong.id == hetong_response.id,
                    Hetong.is_deleted == "N"
                ).first()

                if hetong:
                    original_amount = float(baojia.zongji_jine)

                    # 这里需要根据实际的合同金额字段名调整
                    # setattr(hetong, 'hetong_jine', custom_amount)

                    workflow_id = self._trigger_amount_change_audit(
                        hetong_id=hetong.id,
                        original_amount=original_amount,
                        new_amount=custom_amount,
                        change_reason=change_reason or "合同生成时金额调整",
                        applicant_id=created_by
                    )

                    if workflow_id:
                        hetong.hetong_zhuangtai = "pending"
                        self.db.commit()
                        self.db.refresh(hetong)
                        return HetongResponse.model_validate(hetong)

        return hetong_response
