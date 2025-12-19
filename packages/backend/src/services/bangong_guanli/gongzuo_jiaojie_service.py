"""
工作交接单管理服务（简化版）
"""
from typing import Tuple, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from datetime import datetime

from models.bangong_guanli import GongzuoJiaojie
from schemas.bangong_guanli.gongzuo_jiaojie_schemas import (
    GongzuoJiaojieCreate,
    GongzuoJiaojieUpdate,
    GongzuoJiaojieResponse,
    GongzuoJiaojieListParams
)

class GongzuoJiaojieService:
    """工作交接单管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_jiaojie_bianhao(self) -> str:
        """生成交接编号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(func.count(GongzuoJiaojie.id)).filter(
            GongzuoJiaojie.jiaojie_bianhao.like(f"JJ{today}%"),
            GongzuoJiaojie.is_deleted == "N"
        ).scalar()
        return f"JJ{today}{str(count + 1).zfill(4)}"
    
    def create_gongzuo_jiaojie(
        self, 
        jiaojie_data: GongzuoJiaojieCreate, 
        jiaojie_ren_id: str
    ) -> GongzuoJiaojieResponse:
        """创建工作交接单"""
        jiaojie_bianhao = self._generate_jiaojie_bianhao()
        
        gongzuo_jiaojie = GongzuoJiaojie(
            jiaojie_bianhao=jiaojie_bianhao,
            jiaojie_ren_id=jiaojie_ren_id,
            **jiaojie_data.model_dump(),
            created_by=jiaojie_ren_id
        )
        
        self.db.add(gongzuo_jiaojie)
        self.db.commit()
        self.db.refresh(gongzuo_jiaojie)
        
        return GongzuoJiaojieResponse.model_validate(gongzuo_jiaojie)
    
    def get_gongzuo_jiaojie_list(
        self, 
        params: GongzuoJiaojieListParams
    ) -> Tuple[List[GongzuoJiaojieResponse], int]:
        """获取工作交接单列表"""
        query = self.db.query(GongzuoJiaojie).filter(
            GongzuoJiaojie.is_deleted == "N"
        )
        
        if params.jiaojie_zhuangtai:
            query = query.filter(GongzuoJiaojie.jiaojie_zhuangtai == params.jiaojie_zhuangtai)
        
        total = query.count()
        query = query.order_by(desc(GongzuoJiaojie.created_at))
        query = query.offset((params.page - 1) * params.size).limit(params.size)
        
        jiaojie_list = query.all()
        result = [GongzuoJiaojieResponse.model_validate(j) for j in jiaojie_list]
        
        return result, total
    
    def get_gongzuo_jiaojie_by_id(self, jiaojie_id: str) -> GongzuoJiaojieResponse:
        """根据ID获取工作交接单详情"""
        jiaojie = self.db.query(GongzuoJiaojie).filter(
            GongzuoJiaojie.id == jiaojie_id,
            GongzuoJiaojie.is_deleted == "N"
        ).first()
        
        if not jiaojie:
            raise HTTPException(status_code=404, detail="工作交接单不存在")
        
        return GongzuoJiaojieResponse.model_validate(jiaojie)
    
    def update_gongzuo_jiaojie(
        self, 
        jiaojie_id: str, 
        update_data: GongzuoJiaojieUpdate,
        updated_by: str
    ) -> GongzuoJiaojieResponse:
        """更新工作交接单"""
        jiaojie = self.db.query(GongzuoJiaojie).filter(
            GongzuoJiaojie.id == jiaojie_id,
            GongzuoJiaojie.is_deleted == "N"
        ).first()
        
        if not jiaojie:
            raise HTTPException(status_code=404, detail="工作交接单不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(jiaojie, key, value)
        
        jiaojie.updated_by = updated_by
        jiaojie.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(jiaojie)
        
        return GongzuoJiaojieResponse.model_validate(jiaojie)
    
    def delete_gongzuo_jiaojie(self, jiaojie_id: str, deleted_by: str) -> Dict[str, str]:
        """删除工作交接单（软删除）"""
        jiaojie = self.db.query(GongzuoJiaojie).filter(
            GongzuoJiaojie.id == jiaojie_id,
            GongzuoJiaojie.is_deleted == "N"
        ).first()
        
        if not jiaojie:
            raise HTTPException(status_code=404, detail="工作交接单不存在")
        
        jiaojie.is_deleted = "Y"
        jiaojie.updated_by = deleted_by
        jiaojie.updated_at = datetime.now()
        
        self.db.commit()
        
        return {"message": "删除成功"}
