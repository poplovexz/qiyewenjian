"""
产品分类管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from models.chanpin_guanli import ChanpinFenlei, ChanpinXiangmu
from schemas.chanpin_guanli import (
    ChanpinFenleiCreate,
    ChanpinFenleiUpdate,
    ChanpinFenleiResponse,
    ChanpinFenleiListResponse,
    ChanpinFenleiListItem,
    ChanpinFenleiOption
)

class ChanpinFenleiService:
    """产品分类管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_fenlei(
        self, 
        fenlei_data: ChanpinFenleiCreate, 
        created_by: str
    ) -> ChanpinFenleiResponse:
        """创建产品分类"""
        # 检查分类编码是否已存在
        existing_fenlei = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.fenlei_bianma == fenlei_data.fenlei_bianma,
                ChanpinFenlei.is_deleted == "N"
            )
        ).first()
        
        if existing_fenlei:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类编码已存在"
            )
        
        # 创建分类
        fenlei = ChanpinFenlei(
            **fenlei_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(fenlei)
        self.db.commit()
        self.db.refresh(fenlei)
        
        # 构建响应数据
        response_data = ChanpinFenleiResponse.model_validate(fenlei)
        response_data.xiangmu_count = 0
        
        return response_data
    
    async def get_fenlei_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        chanpin_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> ChanpinFenleiListResponse:
        """获取产品分类列表"""
        query = self.db.query(
            ChanpinFenlei,
            func.count(ChanpinXiangmu.id).label("xiangmu_count")
        ).outerjoin(
            ChanpinXiangmu,
            and_(
                ChanpinXiangmu.fenlei_id == ChanpinFenlei.id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).filter(ChanpinFenlei.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                ChanpinFenlei.fenlei_mingcheng.contains(search),
                ChanpinFenlei.fenlei_bianma.contains(search),
                ChanpinFenlei.miaoshu.contains(search)
            )
            query = query.filter(search_filter)
        
        # 产品类型筛选
        if chanpin_leixing:
            query = query.filter(ChanpinFenlei.chanpin_leixing == chanpin_leixing)
        
        # 状态筛选
        if zhuangtai:
            query = query.filter(ChanpinFenlei.zhuangtai == zhuangtai)
        
        # 分组和排序
        query = query.group_by(ChanpinFenlei.id).order_by(
            ChanpinFenlei.paixu.asc(),
            ChanpinFenlei.created_at.desc()
        )
        
        # 获取总数
        total = query.count()
        
        # 分页
        skip = (page - 1) * size
        results = query.offset(skip).limit(size).all()
        
        # 构建响应数据
        items = []
        for fenlei, xiangmu_count in results:
            item_data = ChanpinFenleiListItem.model_validate(fenlei)
            item_data.xiangmu_count = xiangmu_count or 0
            items.append(item_data)
        
        pages = (total + size - 1) // size
        
        return ChanpinFenleiListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    async def get_fenlei_by_id(self, fenlei_id: str) -> Optional[ChanpinFenleiResponse]:
        """根据ID获取产品分类"""
        fenlei = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.id == fenlei_id,
                ChanpinFenlei.is_deleted == "N"
            )
        ).first()

        if not fenlei:
            return None

        # 获取项目数量
        xiangmu_count = self.db.query(func.count(ChanpinXiangmu.id)).filter(
            and_(
                ChanpinXiangmu.fenlei_id == fenlei_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).scalar() or 0

        response_data = ChanpinFenleiResponse.model_validate(fenlei)
        response_data.xiangmu_count = xiangmu_count

        return response_data

    async def update_fenlei(
        self,
        fenlei_id: str,
        fenlei_data: ChanpinFenleiUpdate,
        updated_by: str
    ) -> ChanpinFenleiResponse:
        """更新产品分类"""
        fenlei = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.id == fenlei_id,
                ChanpinFenlei.is_deleted == "N"
            )
        ).first()

        if not fenlei:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品分类不存在"
            )

        # 检查分类编码是否已被其他分类使用
        if fenlei_data.fenlei_bianma and fenlei_data.fenlei_bianma != fenlei.fenlei_bianma:
            existing_fenlei = self.db.query(ChanpinFenlei).filter(
                and_(
                    ChanpinFenlei.fenlei_bianma == fenlei_data.fenlei_bianma,
                    ChanpinFenlei.id != fenlei_id,
                    ChanpinFenlei.is_deleted == "N"
                )
            ).first()

            if existing_fenlei:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类编码已存在"
                )

        # 更新字段
        update_data = fenlei_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fenlei, field, value)

        fenlei.updated_by = updated_by

        self.db.commit()
        self.db.refresh(fenlei)

        return await self.get_fenlei_by_id(fenlei_id)

    async def delete_fenlei(self, fenlei_id: str, deleted_by: str) -> bool:
        """删除产品分类"""
        fenlei = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.id == fenlei_id,
                ChanpinFenlei.is_deleted == "N"
            )
        ).first()

        if not fenlei:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品分类不存在"
            )

        # 检查是否有关联的产品项目
        xiangmu_count = self.db.query(func.count(ChanpinXiangmu.id)).filter(
            and_(
                ChanpinXiangmu.fenlei_id == fenlei_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).scalar() or 0

        if xiangmu_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下还有 {xiangmu_count} 个产品项目，无法删除"
            )

        # 软删除
        fenlei.is_deleted = "Y"
        fenlei.updated_by = deleted_by

        self.db.commit()

        return True

    async def get_fenlei_options(
        self,
        chanpin_leixing: Optional[str] = None
    ) -> List[ChanpinFenleiOption]:
        """获取产品分类选项（用于下拉选择）"""
        query = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.is_deleted == "N",
                ChanpinFenlei.zhuangtai == "active"
            )
        )

        if chanpin_leixing:
            query = query.filter(ChanpinFenlei.chanpin_leixing == chanpin_leixing)

        fenlei_list = query.order_by(
            ChanpinFenlei.paixu.asc(),
            ChanpinFenlei.fenlei_mingcheng.asc()
        ).all()

        return [ChanpinFenleiOption.model_validate(fenlei) for fenlei in fenlei_list]
