"""
合同支付服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from models.zhifu_guanli.hetong_zhifu import HetongZhifu
from schemas.zhifu_guanli.hetong_zhifu_schemas import (
    HetongZhifuCreate,
    HetongZhifuUpdate,
    HetongZhifuResponse
)
from core.exceptions import BusinessException, ResourceNotFoundException


class HetongZhifuService:
    """合同支付服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_hetong_zhifu(
        self,
        hetong_zhifu_data: HetongZhifuCreate,
        current_user_id: str
    ) -> HetongZhifuResponse:
        """创建合同支付记录"""
        try:
            # 检查合同是否已有支付记录
            existing = self.db.query(HetongZhifu).filter(
                and_(
                    HetongZhifu.hetong_id == hetong_zhifu_data.hetong_id,
                    HetongZhifu.is_deleted == 'N'
                )
            ).first()
            
            if existing:
                raise BusinessException(
                    message="该合同已存在支付记录",
                    error_code="PAYMENT_EXISTS"
                )

            # 创建支付记录
            hetong_zhifu = HetongZhifu(
                id=str(uuid.uuid4()),
                **hetong_zhifu_data.dict(),
                created_by=current_user_id,
                updated_by=current_user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(hetong_zhifu)
            self.db.commit()
            self.db.refresh(hetong_zhifu)

            return HetongZhifuResponse.from_orm(hetong_zhifu)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, BusinessException):
                raise e
            raise BusinessException(
                message=f"创建合同支付记录失败: {str(e)}",
                error_code="CREATE_PAYMENT_FAILED"
            )

    def get_hetong_zhifu_by_id(self, hetong_zhifu_id: str) -> Optional[HetongZhifuResponse]:
        """根据ID获取合同支付记录"""
        hetong_zhifu = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.id == hetong_zhifu_id,
                HetongZhifu.is_deleted == 'N'
            )
        ).first()

        if not hetong_zhifu:
            return None

        return HetongZhifuResponse.from_orm(hetong_zhifu)

    def get_hetong_zhifu_by_hetong_id(self, hetong_id: str) -> Optional[HetongZhifuResponse]:
        """根据合同ID获取支付记录"""
        hetong_zhifu = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.hetong_id == hetong_id,
                HetongZhifu.is_deleted == 'N'
            )
        ).first()

        if not hetong_zhifu:
            return None

        return HetongZhifuResponse.from_orm(hetong_zhifu)

    def update_hetong_zhifu(
        self,
        hetong_zhifu_id: str,
        hetong_zhifu_data: HetongZhifuUpdate,
        current_user_id: str
    ) -> HetongZhifuResponse:
        """更新合同支付记录"""
        try:
            hetong_zhifu = self.db.query(HetongZhifu).filter(
                and_(
                    HetongZhifu.id == hetong_zhifu_id,
                    HetongZhifu.is_deleted == 'N'
                )
            ).first()

            if not hetong_zhifu:
                raise ResourceNotFoundException(
                    message="合同支付记录不存在",
                    error_code="PAYMENT_NOT_FOUND"
                )

            # 更新字段
            update_data = hetong_zhifu_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(hetong_zhifu, field, value)

            hetong_zhifu.updated_by = current_user_id
            hetong_zhifu.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(hetong_zhifu)

            return HetongZhifuResponse.from_orm(hetong_zhifu)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"更新合同支付记录失败: {str(e)}",
                error_code="UPDATE_PAYMENT_FAILED"
            )

    def delete_hetong_zhifu(self, hetong_zhifu_id: str, current_user_id: str) -> bool:
        """删除合同支付记录（软删除）"""
        try:
            hetong_zhifu = self.db.query(HetongZhifu).filter(
                and_(
                    HetongZhifu.id == hetong_zhifu_id,
                    HetongZhifu.is_deleted == 'N'
                )
            ).first()

            if not hetong_zhifu:
                raise ResourceNotFoundException(
                    message="合同支付记录不存在",
                    error_code="PAYMENT_NOT_FOUND"
                )

            # 检查是否可以删除
            if hetong_zhifu.zhifu_zhuangtai == 'paid':
                raise BusinessException(
                    message="已支付的记录不能删除",
                    error_code="PAID_PAYMENT_CANNOT_DELETE"
                )

            hetong_zhifu.is_deleted = 'Y'
            hetong_zhifu.updated_by = current_user_id
            hetong_zhifu.updated_at = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"删除合同支付记录失败: {str(e)}",
                error_code="DELETE_PAYMENT_FAILED"
            )

    def get_hetong_zhifu_list(
        self,
        page: int = 1,
        size: int = 20,
        hetong_id: Optional[str] = None,
        zhifu_zhuangtai: Optional[str] = None,
        zhifu_fangshi: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取合同支付记录列表"""
        try:
            query = self.db.query(HetongZhifu).filter(HetongZhifu.is_deleted == 'N')

            # 添加筛选条件
            if hetong_id:
                query = query.filter(HetongZhifu.hetong_id == hetong_id)
            
            if zhifu_zhuangtai:
                query = query.filter(HetongZhifu.zhifu_zhuangtai == zhifu_zhuangtai)
            
            if zhifu_fangshi:
                query = query.filter(HetongZhifu.zhifu_fangshi == zhifu_fangshi)

            # 获取总数
            total = query.count()

            # 分页查询
            hetong_zhifu_list = query.order_by(desc(HetongZhifu.created_at)).offset(
                (page - 1) * size
            ).limit(size).all()

            return {
                "total": total,
                "items": [HetongZhifuResponse.from_orm(item) for item in hetong_zhifu_list],
                "page": page,
                "size": size
            }

        except Exception as e:
            raise BusinessException(
                message=f"获取合同支付记录列表失败: {str(e)}",
                error_code="GET_PAYMENT_LIST_FAILED"
            )

    def update_payment_status(
        self,
        hetong_zhifu_id: str,
        zhifu_zhuangtai: str,
        zhifu_liushui_hao: Optional[str] = None,
        current_user_id: str = None
    ) -> HetongZhifuResponse:
        """更新支付状态"""
        try:
            hetong_zhifu = self.db.query(HetongZhifu).filter(
                and_(
                    HetongZhifu.id == hetong_zhifu_id,
                    HetongZhifu.is_deleted == 'N'
                )
            ).first()

            if not hetong_zhifu:
                raise ResourceNotFoundException(
                    message="合同支付记录不存在",
                    error_code="PAYMENT_NOT_FOUND"
                )

            hetong_zhifu.zhifu_zhuangtai = zhifu_zhuangtai
            if zhifu_liushui_hao:
                hetong_zhifu.zhifu_liushui_hao = zhifu_liushui_hao
            
            if zhifu_zhuangtai == 'paid':
                hetong_zhifu.zhifu_shijian = datetime.utcnow()

            if current_user_id:
                hetong_zhifu.updated_by = current_user_id
            hetong_zhifu.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(hetong_zhifu)

            return HetongZhifuResponse.from_orm(hetong_zhifu)

        except Exception as e:
            self.db.rollback()
            if isinstance(e, (BusinessException, ResourceNotFoundException)):
                raise e
            raise BusinessException(
                message=f"更新支付状态失败: {str(e)}",
                error_code="UPDATE_PAYMENT_STATUS_FAILED"
            )
