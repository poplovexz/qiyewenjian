"""
线索来源管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from src.models.xiansuo_guanli import XiansuoLaiyuan
from src.schemas.xiansuo_guanli import (
    XiansuoLaiyuanCreate,
    XiansuoLaiyuanUpdate,
    XiansuoLaiyuanResponse,
    XiansuoLaiyuanListResponse
)
from src.core.cache_decorator import (
    cache_xiansuo_laiyuan,
    invalidate_xiansuo_laiyuan_cache
)


class XiansuoLaiyuanService:
    """线索来源管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @invalidate_xiansuo_laiyuan_cache()
    async def create_laiyuan(self, laiyuan_data: XiansuoLaiyuanCreate, created_by: str) -> XiansuoLaiyuanResponse:
        """创建线索来源"""
        # 验证来源编码唯一性
        existing_laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.laiyuan_bianma == laiyuan_data.laiyuan_bianma,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()
        
        if existing_laiyuan:
            raise HTTPException(status_code=400, detail="来源编码已存在")
        
        # 创建线索来源
        laiyuan = XiansuoLaiyuan(
            **laiyuan_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(laiyuan)
        self.db.commit()
        self.db.refresh(laiyuan)
        
        return XiansuoLaiyuanResponse.model_validate(laiyuan)
    
    def get_laiyuan_by_id(self, laiyuan_id: str) -> Optional[XiansuoLaiyuanResponse]:
        """根据ID获取线索来源"""
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == laiyuan_id,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()
        
        if not laiyuan:
            return None
        
        return XiansuoLaiyuanResponse.model_validate(laiyuan)
    
    def get_laiyuan_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        laiyuan_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> XiansuoLaiyuanListResponse:
        """获取线索来源列表"""
        query = self.db.query(XiansuoLaiyuan).filter(XiansuoLaiyuan.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                XiansuoLaiyuan.laiyuan_mingcheng.contains(search),
                XiansuoLaiyuan.laiyuan_bianma.contains(search),
                XiansuoLaiyuan.miaoshu.contains(search)
            )
            query = query.filter(search_filter)
        
        # 类型筛选
        if laiyuan_leixing:
            query = query.filter(XiansuoLaiyuan.laiyuan_leixing == laiyuan_leixing)
        
        # 状态筛选
        if zhuangtai:
            query = query.filter(XiansuoLaiyuan.zhuangtai == zhuangtai)
        
        # 排序
        query = query.order_by(XiansuoLaiyuan.paixu.asc(), XiansuoLaiyuan.created_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = (page - 1) * size
        laiyuan_list = query.offset(skip).limit(size).all()
        
        return XiansuoLaiyuanListResponse(
            items=[XiansuoLaiyuanResponse.model_validate(laiyuan) for laiyuan in laiyuan_list],
            total=total,
            page=page,
            size=size
        )
    
    @invalidate_xiansuo_laiyuan_cache()
    async def update_laiyuan(self, laiyuan_id: str, laiyuan_data: XiansuoLaiyuanUpdate, updated_by: str) -> XiansuoLaiyuanResponse:
        """更新线索来源"""
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == laiyuan_id,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()
        
        if not laiyuan:
            raise HTTPException(status_code=404, detail="线索来源不存在")
        
        # 如果更新编码，验证唯一性
        if laiyuan_data.laiyuan_bianma and laiyuan_data.laiyuan_bianma != laiyuan.laiyuan_bianma:
            existing_laiyuan = self.db.query(XiansuoLaiyuan).filter(
                XiansuoLaiyuan.laiyuan_bianma == laiyuan_data.laiyuan_bianma,
                XiansuoLaiyuan.is_deleted == "N",
                XiansuoLaiyuan.id != laiyuan_id
            ).first()
            
            if existing_laiyuan:
                raise HTTPException(status_code=400, detail="来源编码已存在")
        
        # 更新字段
        update_data = laiyuan_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(laiyuan, field, value)
        
        laiyuan.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(laiyuan)
        
        return XiansuoLaiyuanResponse.model_validate(laiyuan)
    
    @invalidate_xiansuo_laiyuan_cache()
    async def delete_laiyuan(self, laiyuan_id: str, deleted_by: str) -> bool:
        """删除线索来源（软删除）"""
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == laiyuan_id,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()
        
        if not laiyuan:
            raise HTTPException(status_code=404, detail="线索来源不存在")
        
        # 检查是否有关联的线索
        from src.models.xiansuo_guanli import Xiansuo
        xiansuo_count = self.db.query(Xiansuo).filter(
            Xiansuo.laiyuan_id == laiyuan_id,
            Xiansuo.is_deleted == "N"
        ).count()
        
        if xiansuo_count > 0:
            raise HTTPException(status_code=400, detail=f"该来源下还有 {xiansuo_count} 个线索，无法删除")
        
        # 软删除
        laiyuan.is_deleted = "Y"
        laiyuan.updated_by = deleted_by
        
        self.db.commit()
        
        return True
    
    @cache_xiansuo_laiyuan()
    async def get_active_laiyuan_list(self) -> List[XiansuoLaiyuanResponse]:
        """获取所有启用的线索来源 - 带缓存"""
        laiyuan_list = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.is_deleted == "N",
            XiansuoLaiyuan.zhuangtai == "active"
        ).order_by(XiansuoLaiyuan.paixu.asc()).all()

        return [XiansuoLaiyuanResponse.model_validate(laiyuan) for laiyuan in laiyuan_list]
