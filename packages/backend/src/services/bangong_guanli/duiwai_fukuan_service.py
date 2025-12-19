"""
对外付款申请管理服务（简化版）
"""
from typing import Tuple, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from datetime import datetime

from models.bangong_guanli import DuiwaiFukuanShenqing
from schemas.bangong_guanli.duiwai_fukuan_schemas import (
    DuiwaiFukuanShenqingCreate,
    DuiwaiFukuanShenqingUpdate,
    DuiwaiFukuanShenqingResponse,
    DuiwaiFukuanShenqingListParams
)

class DuiwaiFukuanService:
    """对外付款申请管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_shenqing_bianhao(self) -> str:
        """生成申请编号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(func.count(DuiwaiFukuanShenqing.id)).filter(
            DuiwaiFukuanShenqing.shenqing_bianhao.like(f"FK{today}%"),
            DuiwaiFukuanShenqing.is_deleted == "N"
        ).scalar()
        return f"FK{today}{str(count + 1).zfill(4)}"
    
    def create_duiwai_fukuan_shenqing(
        self, 
        shenqing_data: DuiwaiFukuanShenqingCreate, 
        shenqing_ren_id: str
    ) -> DuiwaiFukuanShenqingResponse:
        """创建对外付款申请"""
        shenqing_bianhao = self._generate_shenqing_bianhao()
        
        fukuan_shenqing = DuiwaiFukuanShenqing(
            shenqing_bianhao=shenqing_bianhao,
            shenqing_ren_id=shenqing_ren_id,
            **shenqing_data.model_dump(),
            created_by=shenqing_ren_id
        )
        
        self.db.add(fukuan_shenqing)
        self.db.commit()
        self.db.refresh(fukuan_shenqing)
        
        return DuiwaiFukuanShenqingResponse.model_validate(fukuan_shenqing)
    
    def get_duiwai_fukuan_shenqing_list(
        self, 
        params: DuiwaiFukuanShenqingListParams
    ) -> Tuple[List[DuiwaiFukuanShenqingResponse], int]:
        """获取对外付款申请列表"""
        query = self.db.query(DuiwaiFukuanShenqing).filter(
            DuiwaiFukuanShenqing.is_deleted == "N"
        )
        
        if params.shenhe_zhuangtai:
            query = query.filter(DuiwaiFukuanShenqing.shenhe_zhuangtai == params.shenhe_zhuangtai)
        
        total = query.count()
        query = query.order_by(desc(DuiwaiFukuanShenqing.created_at))
        query = query.offset((params.page - 1) * params.size).limit(params.size)
        
        shenqing_list = query.all()
        result = [DuiwaiFukuanShenqingResponse.model_validate(s) for s in shenqing_list]
        
        return result, total
    
    def get_duiwai_fukuan_shenqing_by_id(self, shenqing_id: str) -> DuiwaiFukuanShenqingResponse:
        """根据ID获取对外付款申请详情"""
        shenqing = self.db.query(DuiwaiFukuanShenqing).filter(
            DuiwaiFukuanShenqing.id == shenqing_id,
            DuiwaiFukuanShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="对外付款申请不存在")
        
        return DuiwaiFukuanShenqingResponse.model_validate(shenqing)
    
    def update_duiwai_fukuan_shenqing(
        self, 
        shenqing_id: str, 
        update_data: DuiwaiFukuanShenqingUpdate,
        updated_by: str
    ) -> DuiwaiFukuanShenqingResponse:
        """更新对外付款申请"""
        shenqing = self.db.query(DuiwaiFukuanShenqing).filter(
            DuiwaiFukuanShenqing.id == shenqing_id,
            DuiwaiFukuanShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="对外付款申请不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(shenqing, key, value)
        
        shenqing.updated_by = updated_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(shenqing)
        
        return DuiwaiFukuanShenqingResponse.model_validate(shenqing)
    
    def delete_duiwai_fukuan_shenqing(self, shenqing_id: str, deleted_by: str) -> Dict[str, str]:
        """删除对外付款申请（软删除）"""
        shenqing = self.db.query(DuiwaiFukuanShenqing).filter(
            DuiwaiFukuanShenqing.id == shenqing_id,
            DuiwaiFukuanShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="对外付款申请不存在")
        
        shenqing.is_deleted = "Y"
        shenqing.updated_by = deleted_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        
        return {"message": "删除成功"}
