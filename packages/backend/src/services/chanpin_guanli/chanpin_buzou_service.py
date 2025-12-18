"""
产品步骤管理服务
"""
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from models.chanpin_guanli import ChanpinXiangmu, ChanpinBuzou
from schemas.chanpin_guanli import (
    ChanpinBuzouCreate,
    ChanpinBuzouUpdate,
    ChanpinBuzouResponse
)


class ChanpinBuzouService:
    """产品步骤管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    def _convert_to_days(self, time: Decimal, unit: str) -> float:
        """将时间转换为天数

        Args:
            time: 时间值
            unit: 时间单位 (tian/xiaoshi/fenzhong)

        Returns:
            转换后的天数
        """
        unit_map = {
            'tian': 1.0,           # 天 -> 天
            'xiaoshi': 1.0/8.0,    # 小时 -> 天（按8小时工作日）
            'fenzhong': 1.0/480.0  # 分钟 -> 天（480分钟 = 8小时 = 1天）
        }
        return float(time) * unit_map.get(unit, 1.0)

    def _update_xiangmu_banshi_tianshu(self, xiangmu_id: str) -> None:
        """计算并更新产品项目的办事天数

        根据该产品所有步骤的预估时长，计算总办事天数并更新到产品项目表

        Args:
            xiangmu_id: 产品项目ID
        """
        # 获取该产品的所有步骤
        buzou_list = self.db.query(ChanpinBuzou).filter(
            and_(
                ChanpinBuzou.xiangmu_id == xiangmu_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).all()

        # 计算总天数
        total_days = 0.0
        for buzou in buzou_list:
            days = self._convert_to_days(buzou.yugu_shichang, buzou.shichang_danwei)
            total_days += days

        # 向上取整
        import math
        total_days_int = math.ceil(total_days)

        # 更新产品项目的办事天数
        xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if xiangmu:
            xiangmu.banshi_tianshu = total_days_int
            # 注意：不需要调用 commit()，因为调用方会统一提交

    async def create_buzou(
        self,
        buzou_data: ChanpinBuzouCreate,
        created_by: str
    ) -> ChanpinBuzouResponse:
        """创建产品步骤"""
        # 检查项目是否存在
        xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.id == buzou_data.xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所属项目不存在"
            )

        # 创建步骤
        buzou = ChanpinBuzou(
            **buzou_data.model_dump(),
            created_by=created_by
        )

        self.db.add(buzou)

        # 更新产品项目的办事天数
        self._update_xiangmu_banshi_tianshu(buzou_data.xiangmu_id)

        self.db.commit()
        self.db.refresh(buzou)

        return ChanpinBuzouResponse.model_validate(buzou)
    
    async def get_buzou_list(self, xiangmu_id: str) -> List[ChanpinBuzouResponse]:
        """获取产品步骤列表"""
        buzou_list = self.db.query(ChanpinBuzou).filter(
            and_(
                ChanpinBuzou.xiangmu_id == xiangmu_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).order_by(
            ChanpinBuzou.paixu.asc(),
            ChanpinBuzou.created_at.asc()
        ).all()
        
        return [ChanpinBuzouResponse.model_validate(buzou) for buzou in buzou_list]
    
    async def get_buzou_by_id(self, buzou_id: str) -> Optional[ChanpinBuzouResponse]:
        """根据ID获取产品步骤"""
        buzou = self.db.query(ChanpinBuzou).filter(
            and_(
                ChanpinBuzou.id == buzou_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).first()
        
        if not buzou:
            return None
        
        return ChanpinBuzouResponse.model_validate(buzou)
    
    async def update_buzou(
        self,
        buzou_id: str,
        buzou_data: ChanpinBuzouUpdate,
        updated_by: str
    ) -> ChanpinBuzouResponse:
        """更新产品步骤"""
        buzou = self.db.query(ChanpinBuzou).filter(
            and_(
                ChanpinBuzou.id == buzou_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).first()

        if not buzou:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品步骤不存在"
            )

        # 记录原来的项目ID
        old_xiangmu_id = buzou.xiangmu_id

        # 检查项目是否存在（如果要更新项目）
        if buzou_data.xiangmu_id and buzou_data.xiangmu_id != buzou.xiangmu_id:
            xiangmu = self.db.query(ChanpinXiangmu).filter(
                and_(
                    ChanpinXiangmu.id == buzou_data.xiangmu_id,
                    ChanpinXiangmu.is_deleted == "N"
                )
            ).first()

            if not xiangmu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="所属项目不存在"
                )

        # 更新字段
        update_data = buzou_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(buzou, field, value)

        buzou.updated_by = updated_by

        # 更新产品项目的办事天数
        # 如果项目ID发生变化，需要更新新旧两个项目的办事天数
        if buzou_data.xiangmu_id and buzou_data.xiangmu_id != old_xiangmu_id:
            self._update_xiangmu_banshi_tianshu(old_xiangmu_id)
            self._update_xiangmu_banshi_tianshu(buzou.xiangmu_id)
        else:
            # 否则只更新当前项目的办事天数
            self._update_xiangmu_banshi_tianshu(buzou.xiangmu_id)

        self.db.commit()
        self.db.refresh(buzou)

        return ChanpinBuzouResponse.model_validate(buzou)
    
    async def delete_buzou(self, buzou_id: str, deleted_by: str) -> bool:
        """删除产品步骤"""
        buzou = self.db.query(ChanpinBuzou).filter(
            and_(
                ChanpinBuzou.id == buzou_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).first()

        if not buzou:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品步骤不存在"
            )

        # 记录项目ID，用于更新办事天数
        xiangmu_id = buzou.xiangmu_id

        # 软删除
        buzou.is_deleted = "Y"
        buzou.updated_by = deleted_by

        # 更新产品项目的办事天数
        self._update_xiangmu_banshi_tianshu(xiangmu_id)

        self.db.commit()

        return True
    
    async def batch_update_buzou(
        self,
        xiangmu_id: str,
        buzou_list: List[dict],
        updated_by: str
    ) -> List[ChanpinBuzouResponse]:
        """批量更新产品步骤"""
        # 检查项目是否存在
        xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所属项目不存在"
            )

        result_list = []

        for buzou_data in buzou_list:
            if 'id' in buzou_data and buzou_data['id']:
                # 更新现有步骤
                buzou_id = buzou_data.pop('id')
                update_data = ChanpinBuzouUpdate(**buzou_data)
                buzou = await self.update_buzou(buzou_id, update_data, updated_by)
                result_list.append(buzou)
            else:
                # 创建新步骤
                buzou_data['xiangmu_id'] = xiangmu_id
                create_data = ChanpinBuzouCreate(**buzou_data)
                buzou = await self.create_buzou(create_data, updated_by)
                result_list.append(buzou)

        # 注意：create_buzou 和 update_buzou 已经会更新办事天数
        # 这里不需要再次调用 _update_xiangmu_banshi_tianshu

        return result_list
