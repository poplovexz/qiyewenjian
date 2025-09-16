"""
服务记录管理服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from src.models.kehu_guanli import FuwuJilu, Kehu
from src.schemas.kehu_guanli.fuwu_jilu_schemas import (
    FuwuJiluCreate,
    FuwuJiluUpdate,
    FuwuJiluResponse,
    FuwuJiluListResponse
)


class FuwuJiluService:
    """服务记录管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fuwu_jilu(self, fuwu_jilu_data: FuwuJiluCreate, created_by: str) -> FuwuJiluResponse:
        """创建服务记录"""
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == fuwu_jilu_data.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 创建服务记录
        fuwu_jilu = FuwuJilu(
            **fuwu_jilu_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(fuwu_jilu)
        self.db.commit()
        self.db.refresh(fuwu_jilu)
        
        return FuwuJiluResponse.model_validate(fuwu_jilu)
    
    def get_fuwu_jilu_by_id(self, fuwu_jilu_id: str) -> Optional[FuwuJiluResponse]:
        """根据ID获取服务记录"""
        fuwu_jilu = self.db.query(FuwuJilu).filter(
            FuwuJilu.id == fuwu_jilu_id,
            FuwuJilu.is_deleted == "N"
        ).first()
        
        if not fuwu_jilu:
            return None
        
        return FuwuJiluResponse.model_validate(fuwu_jilu)
    
    def get_fuwu_jilu_list(
        self,
        page: int = 1,
        size: int = 100,
        kehu_id: Optional[str] = None,
        goutong_fangshi: Optional[str] = None,
        wenti_leixing: Optional[str] = None,
        chuli_zhuangtai: Optional[str] = None,
        search: Optional[str] = None
    ) -> FuwuJiluListResponse:
        """获取服务记录列表"""
        query = self.db.query(FuwuJilu).filter(FuwuJilu.is_deleted == "N")
        
        # 客户筛选
        if kehu_id:
            query = query.filter(FuwuJilu.kehu_id == kehu_id)
        
        # 沟通方式筛选
        if goutong_fangshi:
            query = query.filter(FuwuJilu.goutong_fangshi == goutong_fangshi)
        
        # 问题类型筛选
        if wenti_leixing:
            query = query.filter(FuwuJilu.wenti_leixing == wenti_leixing)
        
        # 处理状态筛选
        if chuli_zhuangtai:
            query = query.filter(FuwuJilu.chuli_zhuangtai == chuli_zhuangtai)
        
        # 搜索条件
        if search:
            search_filter = or_(
                FuwuJilu.goutong_neirong.contains(search),
                FuwuJilu.wenti_miaoshu.contains(search),
                FuwuJilu.chuli_jieguo.contains(search)
            )
            query = query.filter(search_filter)
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * size
        fuwu_jilu_list = query.order_by(FuwuJilu.created_at.desc()).offset(offset).limit(size).all()
        
        return FuwuJiluListResponse(
            total=total,
            items=[FuwuJiluResponse.model_validate(fuwu_jilu) for fuwu_jilu in fuwu_jilu_list],
            page=page,
            size=size
        )
    
    def update_fuwu_jilu(self, fuwu_jilu_id: str, fuwu_jilu_data: FuwuJiluUpdate, updated_by: str) -> FuwuJiluResponse:
        """更新服务记录"""
        fuwu_jilu = self.db.query(FuwuJilu).filter(
            FuwuJilu.id == fuwu_jilu_id,
            FuwuJilu.is_deleted == "N"
        ).first()
        
        if not fuwu_jilu:
            raise HTTPException(status_code=404, detail="服务记录不存在")
        
        # 更新字段
        update_data = fuwu_jilu_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fuwu_jilu, field, value)
        
        fuwu_jilu.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(fuwu_jilu)
        
        return FuwuJiluResponse.model_validate(fuwu_jilu)
    
    def delete_fuwu_jilu(self, fuwu_jilu_id: str, deleted_by: str) -> bool:
        """删除服务记录（软删除）"""
        fuwu_jilu = self.db.query(FuwuJilu).filter(
            FuwuJilu.id == fuwu_jilu_id,
            FuwuJilu.is_deleted == "N"
        ).first()
        
        if not fuwu_jilu:
            raise HTTPException(status_code=404, detail="服务记录不存在")
        
        # 软删除
        fuwu_jilu.is_deleted = "Y"
        fuwu_jilu.updated_by = deleted_by
        
        self.db.commit()
        
        return True
    
    def get_kehu_fuwu_jilu_list(self, kehu_id: str, page: int = 1, size: int = 50) -> FuwuJiluListResponse:
        """获取指定客户的服务记录列表"""
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        return self.get_fuwu_jilu_list(
            page=page,
            size=size,
            kehu_id=kehu_id
        )
    
    def update_chuli_zhuangtai(self, fuwu_jilu_id: str, new_status: str, chuli_jieguo: Optional[str], updated_by: str) -> FuwuJiluResponse:
        """更新处理状态"""
        fuwu_jilu = self.db.query(FuwuJilu).filter(
            FuwuJilu.id == fuwu_jilu_id,
            FuwuJilu.is_deleted == "N"
        ).first()
        
        if not fuwu_jilu:
            raise HTTPException(status_code=404, detail="服务记录不存在")
        
        # 验证状态值
        allowed_statuses = ["pending", "processing", "completed", "cancelled"]
        if new_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"无效的处理状态: {new_status}")
        
        fuwu_jilu.chuli_zhuangtai = new_status
        if chuli_jieguo:
            fuwu_jilu.chuli_jieguo = chuli_jieguo
        fuwu_jilu.chuli_ren_id = updated_by
        fuwu_jilu.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(fuwu_jilu)
        
        return FuwuJiluResponse.model_validate(fuwu_jilu)
