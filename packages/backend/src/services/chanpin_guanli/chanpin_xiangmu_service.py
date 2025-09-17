"""
产品项目管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from ...models.chanpin_guanli import ChanpinFenlei, ChanpinXiangmu, ChanpinBuzou
from ...schemas.chanpin_guanli import (
    ChanpinXiangmuCreate,
    ChanpinXiangmuUpdate,
    ChanpinXiangmuResponse,
    ChanpinXiangmuListResponse,
    ChanpinXiangmuListItem,
    ChanpinXiangmuDetailResponse
)


class ChanpinXiangmuService:
    """产品项目管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_xiangmu(
        self, 
        xiangmu_data: ChanpinXiangmuCreate, 
        created_by: str
    ) -> ChanpinXiangmuResponse:
        """创建产品项目"""
        # 检查分类是否存在
        fenlei = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.id == xiangmu_data.fenlei_id,
                ChanpinFenlei.is_deleted == "N"
            )
        ).first()
        
        if not fenlei:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所属分类不存在"
            )
        
        # 检查项目编码是否已存在
        existing_xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.xiangmu_bianma == xiangmu_data.xiangmu_bianma,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()
        
        if existing_xiangmu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目编码已存在"
            )
        
        # 创建项目
        xiangmu = ChanpinXiangmu(
            **xiangmu_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(xiangmu)
        self.db.commit()
        self.db.refresh(xiangmu)
        
        # 构建响应数据
        response_data = ChanpinXiangmuResponse.model_validate(xiangmu)
        response_data.fenlei_mingcheng = fenlei.fenlei_mingcheng
        response_data.buzou_count = 0
        
        return response_data
    
    async def get_xiangmu_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        fenlei_id: Optional[str] = None,
        chanpin_leixing: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> ChanpinXiangmuListResponse:
        """获取产品项目列表"""
        query = self.db.query(
            ChanpinXiangmu,
            ChanpinFenlei.fenlei_mingcheng,
            func.count(ChanpinBuzou.id).label("buzou_count")
        ).join(
            ChanpinFenlei,
            and_(
                ChanpinFenlei.id == ChanpinXiangmu.fenlei_id,
                ChanpinFenlei.is_deleted == "N"
            )
        ).outerjoin(
            ChanpinBuzou,
            and_(
                ChanpinBuzou.xiangmu_id == ChanpinXiangmu.id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).filter(ChanpinXiangmu.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                ChanpinXiangmu.xiangmu_mingcheng.contains(search),
                ChanpinXiangmu.xiangmu_bianma.contains(search),
                ChanpinXiangmu.xiangmu_beizhu.contains(search),
                ChanpinFenlei.fenlei_mingcheng.contains(search)
            )
            query = query.filter(search_filter)
        
        # 分类筛选
        if fenlei_id:
            query = query.filter(ChanpinXiangmu.fenlei_id == fenlei_id)
        
        # 产品类型筛选
        if chanpin_leixing:
            query = query.filter(ChanpinFenlei.chanpin_leixing == chanpin_leixing)
        
        # 状态筛选
        if zhuangtai:
            query = query.filter(ChanpinXiangmu.zhuangtai == zhuangtai)
        
        # 分组和排序
        query = query.group_by(ChanpinXiangmu.id, ChanpinFenlei.fenlei_mingcheng).order_by(
            ChanpinXiangmu.paixu.asc(),
            ChanpinXiangmu.created_at.desc()
        )
        
        # 获取总数
        total = query.count()
        
        # 分页
        skip = (page - 1) * size
        results = query.offset(skip).limit(size).all()
        
        # 构建响应数据
        items = []
        for xiangmu, fenlei_mingcheng, buzou_count in results:
            item_dict = {
                "id": xiangmu.id,
                "xiangmu_mingcheng": xiangmu.xiangmu_mingcheng,
                "xiangmu_bianma": xiangmu.xiangmu_bianma,
                "fenlei_id": xiangmu.fenlei_id,
                "fenlei_mingcheng": fenlei_mingcheng,
                "yewu_baojia": xiangmu.yewu_baojia,
                "baojia_danwei": xiangmu.baojia_danwei,
                "banshi_tianshu": xiangmu.banshi_tianshu,
                "paixu": xiangmu.paixu,
                "zhuangtai": xiangmu.zhuangtai,
                "created_at": xiangmu.created_at,
                "updated_at": xiangmu.updated_at,
                "buzou_count": buzou_count or 0
            }
            item_data = ChanpinXiangmuListItem(**item_dict)
            items.append(item_data)
        
        pages = (total + size - 1) // size
        
        return ChanpinXiangmuListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    async def get_xiangmu_by_id(self, xiangmu_id: str) -> Optional[ChanpinXiangmuResponse]:
        """根据ID获取产品项目"""
        xiangmu = self.db.query(ChanpinXiangmu).options(
            joinedload(ChanpinXiangmu.fenlei)
        ).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            return None

        # 获取步骤数量
        buzou_count = self.db.query(func.count(ChanpinBuzou.id)).filter(
            and_(
                ChanpinBuzou.xiangmu_id == xiangmu_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).scalar() or 0

        response_data = ChanpinXiangmuResponse.model_validate(xiangmu)
        response_data.fenlei_mingcheng = xiangmu.fenlei.fenlei_mingcheng if xiangmu.fenlei else None
        response_data.buzou_count = buzou_count

        return response_data

    async def get_xiangmu_detail(self, xiangmu_id: str) -> Optional[ChanpinXiangmuDetailResponse]:
        """获取产品项目详情（包含步骤列表）"""
        xiangmu = self.db.query(ChanpinXiangmu).options(
            joinedload(ChanpinXiangmu.fenlei),
            joinedload(ChanpinXiangmu.buzou_list)
        ).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            return None

        response_data = ChanpinXiangmuDetailResponse.model_validate(xiangmu)
        response_data.fenlei_mingcheng = xiangmu.fenlei.fenlei_mingcheng if xiangmu.fenlei else None
        response_data.buzou_count = len([b for b in xiangmu.buzou_list if b.is_deleted == "N"])

        # 过滤已删除的步骤
        response_data.buzou_list = [
            buzou for buzou in response_data.buzou_list
            if buzou.zhuangtai != "deleted"
        ]

        return response_data

    async def update_xiangmu(
        self,
        xiangmu_id: str,
        xiangmu_data: ChanpinXiangmuUpdate,
        updated_by: str
    ) -> ChanpinXiangmuResponse:
        """更新产品项目"""
        xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品项目不存在"
            )

        # 检查分类是否存在（如果要更新分类）
        if xiangmu_data.fenlei_id and xiangmu_data.fenlei_id != xiangmu.fenlei_id:
            fenlei = self.db.query(ChanpinFenlei).filter(
                and_(
                    ChanpinFenlei.id == xiangmu_data.fenlei_id,
                    ChanpinFenlei.is_deleted == "N"
                )
            ).first()

            if not fenlei:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="所属分类不存在"
                )

        # 检查项目编码是否已被其他项目使用
        if xiangmu_data.xiangmu_bianma and xiangmu_data.xiangmu_bianma != xiangmu.xiangmu_bianma:
            existing_xiangmu = self.db.query(ChanpinXiangmu).filter(
                and_(
                    ChanpinXiangmu.xiangmu_bianma == xiangmu_data.xiangmu_bianma,
                    ChanpinXiangmu.id != xiangmu_id,
                    ChanpinXiangmu.is_deleted == "N"
                )
            ).first()

            if existing_xiangmu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="项目编码已存在"
                )

        # 更新字段
        update_data = xiangmu_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(xiangmu, field, value)

        xiangmu.updated_by = updated_by

        self.db.commit()
        self.db.refresh(xiangmu)

        return await self.get_xiangmu_by_id(xiangmu_id)

    async def delete_xiangmu(self, xiangmu_id: str, deleted_by: str) -> bool:
        """删除产品项目"""
        xiangmu = self.db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.id == xiangmu_id,
                ChanpinXiangmu.is_deleted == "N"
            )
        ).first()

        if not xiangmu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="产品项目不存在"
            )

        # 检查是否有关联的产品步骤
        buzou_count = self.db.query(func.count(ChanpinBuzou.id)).filter(
            and_(
                ChanpinBuzou.xiangmu_id == xiangmu_id,
                ChanpinBuzou.is_deleted == "N"
            )
        ).scalar() or 0

        if buzou_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该项目下还有 {buzou_count} 个步骤，无法删除"
            )

        # 软删除
        xiangmu.is_deleted = "Y"
        xiangmu.updated_by = deleted_by

        self.db.commit()

        return True
