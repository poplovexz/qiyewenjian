"""
银行汇款单据服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.models.zhifu_guanli.yinhang_huikuan_danju import YinhangHuikuanDanju
from src.schemas.zhifu_guanli.yinhang_huikuan_danju_schemas import (
    YinhangHuikuanDanjuCreate,
    YinhangHuikuanDanjuUpdate,
    YinhangHuikuanDanjuResponse
)
from src.core.exceptions import BusinessException, ResourceNotFoundException


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
