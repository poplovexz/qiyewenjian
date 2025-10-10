"""
产品步骤管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from models.chanpin_guanli import ChanpinXiangmu, ChanpinBuzou
from schemas.chanpin_guanli import (
    ChanpinBuzouCreate,
    ChanpinBuzouUpdate,
    ChanpinBuzouResponse,
    ChanpinBuzouBatchCreate,
    ChanpinBuzouBatchUpdate
)


class ChanpinBuzouService:
    """产品步骤管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        
        # 软删除
        buzou.is_deleted = "Y"
        buzou.updated_by = deleted_by
        
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
        
        return result_list
