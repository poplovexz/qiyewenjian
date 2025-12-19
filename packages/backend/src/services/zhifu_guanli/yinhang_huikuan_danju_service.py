"""
银行汇款单据服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from models.zhifu_guanli.yinhang_huikuan_danju import YinhangHuikuanDanju
from models.zhifu_guanli.hetong_zhifu import HetongZhifu
from models.hetong_guanli.hetong import Hetong
from schemas.zhifu_guanli.yinhang_huikuan_danju_schemas import (
    YinhangHuikuanDanjuCreate,
    YinhangHuikuanDanjuUpdate,
    YinhangHuikuanDanjuResponse
)
from core.exceptions import BusinessException, ResourceNotFoundException
import logging

logger = logging.getLogger(__name__)

class YinhangHuikuanDanjuService:
    """银行汇款单据服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_yinhang_huikuan_danju(
        self,
        danju_data: YinhangHuikuanDanjuCreate,
        current_user_id: str
    ) -> YinhangHuikuanDanjuResponse:
        """创建银行汇款单据"""
        try:
            # 创建汇款单据
            danju = YinhangHuikuanDanju(
                id=str(uuid.uuid4()),
                **danju_data.dict(),
                created_by=current_user_id,
                updated_by=current_user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(danju)
            self.db.commit()
            self.db.refresh(danju)

            return YinhangHuikuanDanjuResponse.from_orm(danju)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, BusinessException):
                raise e
            raise BusinessException(
                message=f"创建银行汇款单据失败: {str(e)}",
                error_code="CREATE_BANK_TRANSFER_FAILED"
            )

    def get_yinhang_huikuan_danju_by_id(self, danju_id: str) -> Optional[YinhangHuikuanDanjuResponse]:
        """根据ID获取银行汇款单据"""
        danju = self.db.query(YinhangHuikuanDanju).filter(
            and_(
                YinhangHuikuanDanju.id == danju_id,
                YinhangHuikuanDanju.is_deleted == 'N'
            )
        ).first()

        if not danju:
            return None

        return YinhangHuikuanDanjuResponse.from_orm(danju)

    def get_yinhang_huikuan_danju_by_hetong_id(self, hetong_id: str) -> List[YinhangHuikuanDanjuResponse]:
        """根据合同ID获取银行汇款单据列表"""
        danju_list = self.db.query(YinhangHuikuanDanju).filter(
            and_(
                YinhangHuikuanDanju.hetong_id == hetong_id,
                YinhangHuikuanDanju.is_deleted == 'N'
            )
        ).order_by(desc(YinhangHuikuanDanju.created_at)).all()

        return [YinhangHuikuanDanjuResponse.from_orm(danju) for danju in danju_list]

    def update_yinhang_huikuan_danju(
        self,
        danju_id: str,
        danju_data: YinhangHuikuanDanjuUpdate,
        current_user_id: str
    ) -> YinhangHuikuanDanjuResponse:
        """更新银行汇款单据"""
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            # 更新字段
            update_data = danju_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(danju, field, value)

            danju.updated_by = current_user_id
            danju.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(danju)

            return YinhangHuikuanDanjuResponse.from_orm(danju)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"更新银行汇款单据失败: {str(e)}",
                error_code="UPDATE_BANK_TRANSFER_FAILED"
            )

    def delete_yinhang_huikuan_danju(self, danju_id: str, current_user_id: str) -> bool:
        """删除银行汇款单据（软删除）"""
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            # 检查是否可以删除
            if danju.shenhe_zhuangtai == 'approved':
                raise BusinessException(
                    message="已审核通过的单据不能删除",
                    error_code="APPROVED_TRANSFER_CANNOT_DELETE"
                )

            danju.is_deleted = 'Y'
            danju.updated_by = current_user_id
            danju.updated_at = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"删除银行汇款单据失败: {str(e)}",
                error_code="DELETE_BANK_TRANSFER_FAILED"
            )

    def get_yinhang_huikuan_danju_list(
        self,
        page: int = 1,
        size: int = 20,
        hetong_id: Optional[str] = None,
        shenhe_zhuangtai: Optional[str] = None,
        huikuan_yinhang: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取银行汇款单据列表"""
        try:
            query = self.db.query(YinhangHuikuanDanju).filter(YinhangHuikuanDanju.is_deleted == 'N')

            # 添加筛选条件
            if hetong_id:
                query = query.filter(YinhangHuikuanDanju.hetong_id == hetong_id)
            
            if shenhe_zhuangtai:
                query = query.filter(YinhangHuikuanDanju.shenhe_zhuangtai == shenhe_zhuangtai)
            
            if huikuan_yinhang:
                query = query.filter(YinhangHuikuanDanju.huikuan_yinhang.like(f"%{huikuan_yinhang}%"))

            # 获取总数
            total = query.count()

            # 分页查询
            danju_list = query.order_by(desc(YinhangHuikuanDanju.created_at)).offset(
                (page - 1) * size
            ).limit(size).all()

            return {
                "total": total,
                "items": [YinhangHuikuanDanjuResponse.from_orm(item) for item in danju_list],
                "page": page,
                "size": size
            }

        except Exception as e:
            raise BusinessException(
                message=f"获取银行汇款单据列表失败: {str(e)}",
                error_code="GET_BANK_TRANSFER_LIST_FAILED"
            )

    def approve_yinhang_huikuan_danju(
        self,
        danju_id: str,
        shenhe_yijian: Optional[str] = None,
        current_user_id: str = None
    ) -> YinhangHuikuanDanjuResponse:
        """审核通过银行汇款单据"""
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            if danju.shenhe_zhuangtai != 'pending':
                raise BusinessException(
                    message="只能审核待审核状态的单据",
                    error_code="INVALID_AUDIT_STATUS"
                )

            danju.shenhe_zhuangtai = 'approved'
            danju.shenhe_shijian = datetime.utcnow()
            danju.shenhe_ren = current_user_id
            if shenhe_yijian:
                danju.shenhe_yijian = shenhe_yijian

            if current_user_id:
                danju.updated_by = current_user_id
            danju.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(danju)

            return YinhangHuikuanDanjuResponse.from_orm(danju)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"审核银行汇款单据失败: {str(e)}",
                error_code="APPROVE_BANK_TRANSFER_FAILED"
            )

    def reject_yinhang_huikuan_danju(
        self,
        danju_id: str,
        shenhe_yijian: str,
        current_user_id: str = None
    ) -> YinhangHuikuanDanjuResponse:
        """审核拒绝银行汇款单据"""
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            if danju.shenhe_zhuangtai != 'pending':
                raise BusinessException(
                    message="只能审核待审核状态的单据",
                    error_code="INVALID_AUDIT_STATUS"
                )

            danju.shenhe_zhuangtai = 'rejected'
            danju.shenhe_shijian = datetime.utcnow()
            danju.shenhe_ren = current_user_id
            danju.shenhe_yijian = shenhe_yijian

            if current_user_id:
                danju.updated_by = current_user_id
            danju.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(danju)

            return YinhangHuikuanDanjuResponse.from_orm(danju)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"拒绝银行汇款单据失败: {str(e)}",
                error_code="REJECT_BANK_TRANSFER_FAILED"
            )

    def upload_voucher(
        self,
        danju_id: str,
        voucher_url: str,
        uploader_id: str,
        beizhu: str = None,
        huikuan_ren: str = None,
        huikuan_yinhang: str = None,
        huikuan_zhanghu: str = None,
        huikuan_riqi: str = None
    ) -> Dict[str, Any]:
        """
        业务员上传汇款凭证并填写汇款信息

        Args:
            danju_id: 单据ID
            voucher_url: 凭证图片URL
            uploader_id: 上传人ID
            beizhu: 备注
            huikuan_ren: 汇款人姓名
            huikuan_yinhang: 汇款银行
            huikuan_zhanghu: 汇款账户
            huikuan_riqi: 汇款日期

        Returns:
            上传结果
        """
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            # 检查状态
            if danju.shenhe_zhuangtai != 'waiting_voucher':
                raise BusinessException(
                    message=f"当前状态不允许上传凭证，当前状态：{danju.shenhe_zhuangtai}",
                    error_code="INVALID_STATUS_FOR_UPLOAD"
                )

            # 更新单据信息
            danju.danju_lujing = voucher_url
            danju.shangchuan_ren_id = uploader_id
            danju.shangchuan_shijian = datetime.now()
            danju.shenhe_zhuangtai = 'pending_audit'  # 更新为待审核状态

            # 更新汇款信息（业务员根据凭证填写）
            if huikuan_ren:
                danju.huikuan_ren = huikuan_ren
            if huikuan_yinhang:
                danju.huikuan_yinhang = huikuan_yinhang
            if huikuan_zhanghu:
                danju.huikuan_zhanghu = huikuan_zhanghu
            if huikuan_riqi:
                # 将字符串转换为datetime对象
                try:
                    danju.huikuan_riqi = datetime.fromisoformat(huikuan_riqi.replace('Z', '+00:00'))
                except Exception as e:
                    logger.warning(f"汇款日期格式转换失败: {huikuan_riqi}, 错误: {e}")
                    # 如果转换失败，使用当前时间
                    danju.huikuan_riqi = datetime.now()

            if beizhu:
                danju.beizhu = beizhu
            danju.updated_by = uploader_id
            danju.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(danju)

            logger.info(f"业务员 {uploader_id} 上传汇款凭证并填写汇款信息成功，单据：{danju.danju_bianhao}")

            # 触发审核流程
            workflow_id = None
            try:
                from services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine

                workflow_engine = ShenheWorkflowEngine(self.db)
                workflow_id = workflow_engine.trigger_audit(
                    audit_type="yinhang_huikuan",  # 银行汇款审核类型
                    related_id=danju.id,  # 汇款单据ID
                    trigger_data={
                        "danju_bianhao": danju.danju_bianhao,
                        "huikuan_jine": float(danju.huikuan_jine),
                        "voucher_url": voucher_url,
                        "hetong_zhifu_id": danju.hetong_zhifu_id,
                        "huikuan_ren": huikuan_ren,
                        "huikuan_yinhang": huikuan_yinhang
                    },
                    applicant_id=uploader_id  # 上传人ID（业务员）
                )

                if workflow_id:
                    logger.info(f"成功触发审核流程，流程ID：{workflow_id}")
                else:
                    logger.warning(f"未找到匹配的审核规则，单据：{danju.danju_bianhao}")

            except Exception as e:
                logger.error(f"触发审核流程失败: {str(e)}")
                # 不影响主流程，继续返回成功

            return {
                "success": True,
                "message": "凭证上传成功，汇款信息已更新，已提交财务审核",
                "danju_id": danju.id,
                "danju_bianhao": danju.danju_bianhao,
                "workflow_id": workflow_id
            }

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"上传凭证失败: {str(e)}",
                error_code="UPLOAD_VOUCHER_FAILED"
            )

    def audit_voucher(
        self,
        danju_id: str,
        audit_result: str,
        audit_opinion: str,
        auditor_id: str,
        actual_amount: float = None,
        arrival_time: datetime = None
    ) -> Dict[str, Any]:
        """
        财务审核汇款凭证

        Args:
            danju_id: 单据ID
            audit_result: 审核结果（approved/rejected）
            audit_opinion: 审核意见
            auditor_id: 审核人ID
            actual_amount: 实际到账金额
            arrival_time: 到账时间

        Returns:
            审核结果
        """
        try:
            danju = self.db.query(YinhangHuikuanDanju).filter(
                and_(
                    YinhangHuikuanDanju.id == danju_id,
                    YinhangHuikuanDanju.is_deleted == 'N'
                )
            ).first()

            if not danju:
                raise ResourceNotFoundException(
                    message="银行汇款单据不存在",
                    error_code="BANK_TRANSFER_NOT_FOUND"
                )

            # 检查状态
            if danju.shenhe_zhuangtai != 'pending_audit':
                raise BusinessException(
                    message=f"当前状态不允许审核，当前状态：{danju.shenhe_zhuangtai}",
                    error_code="INVALID_STATUS_FOR_AUDIT"
                )

            # 更新审核信息
            danju.shenhe_ren_id = auditor_id
            danju.shenhe_shijian = datetime.now()
            danju.shenhe_yijian = audit_opinion
            danju.updated_by = auditor_id
            danju.updated_at = datetime.now()

            if audit_result == 'approved':
                danju.shenhe_zhuangtai = 'approved'

                # 更新合同支付状态
                hetong_zhifu = self.db.query(HetongZhifu).filter(
                    HetongZhifu.id == danju.hetong_zhifu_id,
                    HetongZhifu.is_deleted == 'N'
                ).first()

                if hetong_zhifu:
                    hetong_zhifu.zhifu_zhuangtai = 'paid'
                    hetong_zhifu.zhifu_shijian = arrival_time or datetime.now()
                    hetong_zhifu.updated_by = auditor_id
                    hetong_zhifu.updated_at = datetime.now()

                    # 更新合同状态
                    hetong = self.db.query(Hetong).filter(
                        Hetong.id == hetong_zhifu.hetong_id,
                        Hetong.is_deleted == 'N'
                    ).first()

                    if hetong:
                        hetong.payment_status = 'paid'
                        hetong.paid_at = arrival_time or datetime.now()
                        hetong.updated_by = auditor_id
                        hetong.updated_at = datetime.now()

                        logger.info(f"合同 {hetong.hetong_bianhao} 支付状态已更新为已支付")

                        # ✅ 自动更新线索状态为"已成交"
                        if hetong.xiansuo_id:
                            try:
                                from models.xiansuo_guanli.xiansuo import Xiansuo
                                from models.xiansuo_guanli.xiansuo_laiyuan import XiansuoLaiyuan

                                xiansuo = self.db.query(Xiansuo).filter(
                                    Xiansuo.id == hetong.xiansuo_id,
                                    Xiansuo.is_deleted == 'N'
                                ).first()

                                if xiansuo and xiansuo.xiansuo_zhuangtai != 'won':
                                    old_status = xiansuo.xiansuo_zhuangtai
                                    xiansuo.xiansuo_zhuangtai = 'won'  # 已成交
                                    xiansuo.shi_zhuanhua = 'Y'  # 标记为已转化
                                    xiansuo.zhuanhua_shijian = datetime.now()
                                    xiansuo.zhuanhua_jine = actual_amount or danju.huikuan_jine
                                    xiansuo.updated_by = auditor_id
                                    xiansuo.updated_at = datetime.now()

                                    # 更新来源的转化统计（如果还未更新）
                                    if old_status != 'won':
                                        laiyuan = self.db.query(XiansuoLaiyuan).filter(
                                            XiansuoLaiyuan.id == xiansuo.laiyuan_id
                                        ).first()

                                        if laiyuan:
                                            laiyuan.zhuanhua_shuliang = (laiyuan.zhuanhua_shuliang or 0) + 1
                                            if laiyuan.xiansuo_shuliang > 0:
                                                laiyuan.zhuanhua_lv = (laiyuan.zhuanhua_shuliang / laiyuan.xiansuo_shuliang) * 100

                                    logger.info(f"线索状态自动更新：{old_status} → won（银行汇款审核通过触发）")
                            except Exception as e:
                                logger.error(f"自动更新线索状态失败: {str(e)}")
                                # 不影响主流程

                logger.info(f"财务审核通过，单据：{danju.danju_bianhao}")
                message = "审核通过，合同支付状态已更新"
            else:
                danju.shenhe_zhuangtai = 'rejected'
                logger.info(f"财务审核拒绝，单据：{danju.danju_bianhao}")
                message = "审核已拒绝"

            self.db.commit()
            self.db.refresh(danju)

            # TODO: 发送通知

            return {
                "success": True,
                "message": message,
                "audit_result": audit_result,
                "danju_id": danju.id
            }

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"审核失败: {str(e)}",
                error_code="AUDIT_VOUCHER_FAILED"
            )
