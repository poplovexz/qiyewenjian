"""
合同乙方主体服务层
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from models.hetong_guanli import HetongYifangZhuti
from schemas.hetong_guanli import (
    HetongYifangZhutiCreate,
    HetongYifangZhutiUpdate,
    HetongYifangZhutiResponse,
    HetongYifangZhutiListResponse
)


class HetongYifangZhutiService:
    """合同乙方主体服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_yifang_zhuti(self, zhuti_data: HetongYifangZhutiCreate, created_by: str) -> HetongYifangZhutiResponse:
        """创建乙方主体"""
        # 验证主体名称唯一性
        existing_zhuti = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.zhuti_mingcheng == zhuti_data.zhuti_mingcheng,
            HetongYifangZhuti.is_deleted == "N"
        ).first()
        
        if existing_zhuti:
            raise HTTPException(status_code=400, detail="主体名称已存在")
        
        # 如果有证件号码，验证唯一性
        if zhuti_data.zhengjianhao:
            existing_zhengjianhao = self.db.query(HetongYifangZhuti).filter(
                HetongYifangZhuti.zhengjianhao == zhuti_data.zhengjianhao,
                HetongYifangZhuti.is_deleted == "N"
            ).first()
            
            if existing_zhengjianhao:
                raise HTTPException(status_code=400, detail="证件号码已存在")
        
        # 创建乙方主体
        zhuti = HetongYifangZhuti(
            **zhuti_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(zhuti)
        self.db.commit()
        self.db.refresh(zhuti)
        
        return HetongYifangZhutiResponse.model_validate(zhuti)
    
    def get_yifang_zhuti_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        zhuti_leixing: Optional[str] = None,
        zhuti_zhuangtai: Optional[str] = None
    ) -> HetongYifangZhutiListResponse:
        """获取乙方主体列表"""
        query = self.db.query(HetongYifangZhuti).filter(HetongYifangZhuti.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                HetongYifangZhuti.zhuti_mingcheng.contains(search),
                HetongYifangZhuti.lianxi_ren.contains(search),
                HetongYifangZhuti.lianxi_dianhua.contains(search),
                HetongYifangZhuti.zhengjianhao.contains(search)
            )
            query = query.filter(search_filter)
        
        # 筛选条件
        if zhuti_leixing:
            query = query.filter(HetongYifangZhuti.zhuti_leixing == zhuti_leixing)
        
        if zhuti_zhuangtai:
            query = query.filter(HetongYifangZhuti.zhuti_zhuangtai == zhuti_zhuangtai)
        
        # 排序
        query = query.order_by(HetongYifangZhuti.created_at.desc())
        
        # 分页
        total = query.count()
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()
        
        return HetongYifangZhutiListResponse(
            total=total,
            items=[HetongYifangZhutiResponse.model_validate(item) for item in items],
            page=page,
            size=size
        )
    
    def get_yifang_zhuti_by_id(self, zhuti_id: str) -> HetongYifangZhutiResponse:
        """根据ID获取乙方主体"""
        zhuti = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.id == zhuti_id,
            HetongYifangZhuti.is_deleted == "N"
        ).first()
        
        if not zhuti:
            raise HTTPException(status_code=404, detail="乙方主体不存在")
        
        return HetongYifangZhutiResponse.model_validate(zhuti)
    
    def update_yifang_zhuti(self, zhuti_id: str, zhuti_data: HetongYifangZhutiUpdate) -> HetongYifangZhutiResponse:
        """更新乙方主体"""
        zhuti = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.id == zhuti_id,
            HetongYifangZhuti.is_deleted == "N"
        ).first()
        
        if not zhuti:
            raise HTTPException(status_code=404, detail="乙方主体不存在")
        
        # 验证主体名称唯一性（如果要更新名称）
        if zhuti_data.zhuti_mingcheng and zhuti_data.zhuti_mingcheng != zhuti.zhuti_mingcheng:
            existing_zhuti = self.db.query(HetongYifangZhuti).filter(
                HetongYifangZhuti.zhuti_mingcheng == zhuti_data.zhuti_mingcheng,
                HetongYifangZhuti.id != zhuti_id,
                HetongYifangZhuti.is_deleted == "N"
            ).first()
            
            if existing_zhuti:
                raise HTTPException(status_code=400, detail="主体名称已存在")
        
        # 验证证件号码唯一性（如果要更新证件号码）
        if zhuti_data.zhengjianhao and zhuti_data.zhengjianhao != zhuti.zhengjianhao:
            existing_zhengjianhao = self.db.query(HetongYifangZhuti).filter(
                HetongYifangZhuti.zhengjianhao == zhuti_data.zhengjianhao,
                HetongYifangZhuti.id != zhuti_id,
                HetongYifangZhuti.is_deleted == "N"
            ).first()
            
            if existing_zhengjianhao:
                raise HTTPException(status_code=400, detail="证件号码已存在")
        
        # 更新字段
        update_data = zhuti_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zhuti, field, value)
        
        zhuti.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(zhuti)
        
        return HetongYifangZhutiResponse.model_validate(zhuti)
    
    def delete_yifang_zhuti(self, zhuti_id: str) -> bool:
        """删除乙方主体（软删除）"""
        zhuti = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.id == zhuti_id,
            HetongYifangZhuti.is_deleted == "N"
        ).first()
        
        if not zhuti:
            raise HTTPException(status_code=404, detail="乙方主体不存在")
        
        # 检查是否有关联的合同
        from models.hetong_guanli import Hetong
        related_hetong = self.db.query(Hetong).filter(
            Hetong.yifang_zhuti_id == zhuti_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if related_hetong:
            raise HTTPException(status_code=400, detail="该主体已关联合同，不能删除")
        
        zhuti.is_deleted = "Y"
        zhuti.updated_at = datetime.now()
        self.db.commit()
        
        return True
    
    def get_active_yifang_zhuti_list(self) -> list[HetongYifangZhutiResponse]:
        """获取所有启用状态的乙方主体（用于下拉选择）"""
        zhuti_list = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.zhuti_zhuangtai == "active",
            HetongYifangZhuti.is_deleted == "N"
        ).order_by(HetongYifangZhuti.zhuti_mingcheng).all()
        
        return [HetongYifangZhutiResponse.model_validate(zhuti) for zhuti in zhuti_list]
