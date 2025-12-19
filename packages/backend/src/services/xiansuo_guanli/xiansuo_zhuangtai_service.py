"""
线索状态管理服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from models.xiansuo_guanli import XiansuoZhuangtai
from schemas.xiansuo_guanli import (
    XiansuoZhuangtaiCreate,
    XiansuoZhuangtaiUpdate,
    XiansuoZhuangtaiResponse,
    XiansuoZhuangtaiListResponse
)

class XiansuoZhuangtaiService:
    """线索状态管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_zhuangtai(self, zhuangtai_data: XiansuoZhuangtaiCreate, created_by: str) -> XiansuoZhuangtaiResponse:
        """创建线索状态"""
        # 验证状态编码唯一性
        existing_zhuangtai = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.zhuangtai_bianma == zhuangtai_data.zhuangtai_bianma,
            XiansuoZhuangtai.is_deleted == "N"
        ).first()
        
        if existing_zhuangtai:
            raise HTTPException(status_code=400, detail="状态编码已存在")
        
        # 创建线索状态
        zhuangtai = XiansuoZhuangtai(
            **zhuangtai_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(zhuangtai)
        self.db.commit()
        self.db.refresh(zhuangtai)
        
        return XiansuoZhuangtaiResponse.model_validate(zhuangtai)
    
    def get_zhuangtai_by_id(self, zhuangtai_id: str) -> Optional[XiansuoZhuangtaiResponse]:
        """根据ID获取线索状态"""
        zhuangtai = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.id == zhuangtai_id,
            XiansuoZhuangtai.is_deleted == "N"
        ).first()
        
        if not zhuangtai:
            return None
        
        return XiansuoZhuangtaiResponse.model_validate(zhuangtai)
    
    def get_zhuangtai_by_code(self, zhuangtai_bianma: str) -> Optional[XiansuoZhuangtaiResponse]:
        """根据编码获取线索状态"""
        zhuangtai = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.zhuangtai_bianma == zhuangtai_bianma,
            XiansuoZhuangtai.is_deleted == "N"
        ).first()
        
        if not zhuangtai:
            return None
        
        return XiansuoZhuangtaiResponse.model_validate(zhuangtai)
    
    def get_zhuangtai_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        zhuangtai_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> XiansuoZhuangtaiListResponse:
        """获取线索状态列表"""
        query = self.db.query(XiansuoZhuangtai).filter(XiansuoZhuangtai.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                XiansuoZhuangtai.zhuangtai_mingcheng.contains(search),
                XiansuoZhuangtai.zhuangtai_bianma.contains(search),
                XiansuoZhuangtai.miaoshu.contains(search)
            )
            query = query.filter(search_filter)
        
        # 类型筛选
        if zhuangtai_leixing:
            query = query.filter(XiansuoZhuangtai.zhuangtai_leixing == zhuangtai_leixing)
        
        # 状态筛选
        if zhuangtai:
            query = query.filter(XiansuoZhuangtai.zhuangtai == zhuangtai)
        
        # 排序
        query = query.order_by(XiansuoZhuangtai.paixu.asc(), XiansuoZhuangtai.created_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = (page - 1) * size
        zhuangtai_list = query.offset(skip).limit(size).all()
        
        return XiansuoZhuangtaiListResponse(
            items=[XiansuoZhuangtaiResponse.model_validate(zhuangtai) for zhuangtai in zhuangtai_list],
            total=total,
            page=page,
            size=size
        )
    
    def update_zhuangtai(self, zhuangtai_id: str, zhuangtai_data: XiansuoZhuangtaiUpdate, updated_by: str) -> XiansuoZhuangtaiResponse:
        """更新线索状态"""
        zhuangtai = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.id == zhuangtai_id,
            XiansuoZhuangtai.is_deleted == "N"
        ).first()
        
        if not zhuangtai:
            raise HTTPException(status_code=404, detail="线索状态不存在")
        
        # 如果更新编码，验证唯一性
        if zhuangtai_data.zhuangtai_bianma and zhuangtai_data.zhuangtai_bianma != zhuangtai.zhuangtai_bianma:
            existing_zhuangtai = self.db.query(XiansuoZhuangtai).filter(
                XiansuoZhuangtai.zhuangtai_bianma == zhuangtai_data.zhuangtai_bianma,
                XiansuoZhuangtai.is_deleted == "N",
                XiansuoZhuangtai.id != zhuangtai_id
            ).first()
            
            if existing_zhuangtai:
                raise HTTPException(status_code=400, detail="状态编码已存在")
        
        # 更新字段
        update_data = zhuangtai_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zhuangtai, field, value)
        
        zhuangtai.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(zhuangtai)
        
        return XiansuoZhuangtaiResponse.model_validate(zhuangtai)
    
    def delete_zhuangtai(self, zhuangtai_id: str, deleted_by: str) -> bool:
        """删除线索状态（软删除）"""
        zhuangtai = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.id == zhuangtai_id,
            XiansuoZhuangtai.is_deleted == "N"
        ).first()
        
        if not zhuangtai:
            raise HTTPException(status_code=404, detail="线索状态不存在")
        
        # 检查是否有关联的线索
        from models.xiansuo_guanli import Xiansuo
        xiansuo_count = self.db.query(Xiansuo).filter(
            Xiansuo.xiansuo_zhuangtai == zhuangtai.zhuangtai_bianma,
            Xiansuo.is_deleted == "N"
        ).count()
        
        if xiansuo_count > 0:
            raise HTTPException(status_code=400, detail=f"该状态下还有 {xiansuo_count} 个线索，无法删除")
        
        # 软删除
        zhuangtai.is_deleted = "Y"
        zhuangtai.updated_by = deleted_by
        
        self.db.commit()
        
        return True
    
    def get_active_zhuangtai_list(self) -> list[XiansuoZhuangtaiResponse]:
        """获取所有启用的线索状态"""
        zhuangtai_list = self.db.query(XiansuoZhuangtai).filter(
            XiansuoZhuangtai.is_deleted == "N",
            XiansuoZhuangtai.zhuangtai == "active"
        ).order_by(XiansuoZhuangtai.paixu.asc()).all()
        
        return [XiansuoZhuangtaiResponse.model_validate(zhuangtai) for zhuangtai in zhuangtai_list]
