"""
采购申请管理服务（简化版）
"""
from typing import Tuple, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from datetime import datetime

from models.bangong_guanli import CaigouShenqing
from schemas.bangong_guanli.caigou_schemas import (
    CaigouShenqingCreate,
    CaigouShenqingUpdate,
    CaigouShenqingResponse,
    CaigouShenqingListParams
)

class CaigouService:
    """采购申请管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_shenqing_bianhao(self) -> str:
        """生成申请编号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(func.count(CaigouShenqing.id)).filter(
            CaigouShenqing.shenqing_bianhao.like(f"CG{today}%"),
            CaigouShenqing.is_deleted == "N"
        ).scalar()
        return f"CG{today}{str(count + 1).zfill(4)}"
    
    def create_caigou_shenqing(
        self, 
        shenqing_data: CaigouShenqingCreate, 
        shenqing_ren_id: str
    ) -> CaigouShenqingResponse:
        """创建采购申请"""
        shenqing_bianhao = self._generate_shenqing_bianhao()
        
        caigou_shenqing = CaigouShenqing(
            shenqing_bianhao=shenqing_bianhao,
            shenqing_ren_id=shenqing_ren_id,
            **shenqing_data.model_dump(),
            created_by=shenqing_ren_id
        )
        
        self.db.add(caigou_shenqing)
        self.db.commit()
        self.db.refresh(caigou_shenqing)
        
        return CaigouShenqingResponse.model_validate(caigou_shenqing)
    
    def get_caigou_shenqing_list(
        self, 
        params: CaigouShenqingListParams
    ) -> Tuple[List[CaigouShenqingResponse], int]:
        """获取采购申请列表"""
        query = self.db.query(CaigouShenqing).filter(
            CaigouShenqing.is_deleted == "N"
        )
        
        if params.shenhe_zhuangtai:
            query = query.filter(CaigouShenqing.shenhe_zhuangtai == params.shenhe_zhuangtai)
        
        total = query.count()
        query = query.order_by(desc(CaigouShenqing.created_at))
        query = query.offset((params.page - 1) * params.size).limit(params.size)
        
        shenqing_list = query.all()
        result = [CaigouShenqingResponse.model_validate(s) for s in shenqing_list]
        
        return result, total
    
    def get_caigou_shenqing_by_id(self, shenqing_id: str) -> CaigouShenqingResponse:
        """根据ID获取采购申请详情"""
        shenqing = self.db.query(CaigouShenqing).filter(
            CaigouShenqing.id == shenqing_id,
            CaigouShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="采购申请不存在")
        
        return CaigouShenqingResponse.model_validate(shenqing)
    
    def update_caigou_shenqing(
        self, 
        shenqing_id: str, 
        update_data: CaigouShenqingUpdate,
        updated_by: str
    ) -> CaigouShenqingResponse:
        """更新采购申请"""
        shenqing = self.db.query(CaigouShenqing).filter(
            CaigouShenqing.id == shenqing_id,
            CaigouShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="采购申请不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(shenqing, key, value)
        
        shenqing.updated_by = updated_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(shenqing)
        
        return CaigouShenqingResponse.model_validate(shenqing)
    
    def delete_caigou_shenqing(self, shenqing_id: str, deleted_by: str) -> Dict[str, str]:
        """删除采购申请（软删除）"""
        shenqing = self.db.query(CaigouShenqing).filter(
            CaigouShenqing.id == shenqing_id,
            CaigouShenqing.is_deleted == "N"
        ).first()
        
        if not shenqing:
            raise HTTPException(status_code=404, detail="采购申请不存在")
        
        shenqing.is_deleted = "Y"
        shenqing.updated_by = deleted_by
        shenqing.updated_at = datetime.now()
        
        self.db.commit()
        
        return {"message": "删除成功"}
