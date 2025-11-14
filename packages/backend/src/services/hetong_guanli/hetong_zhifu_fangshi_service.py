"""
合同支付方式服务层
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException

from models.hetong_guanli import HetongZhifuFangshi, HetongYifangZhuti
from models.zhifu_guanli import ZhifuPeizhi
from schemas.hetong_guanli import (
    HetongZhifuFangshiCreate,
    HetongZhifuFangshiUpdate,
    HetongZhifuFangshiResponse,
    HetongZhifuFangshiListResponse
)


class HetongZhifuFangshiService:
    """合同支付方式服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_zhifu_fangshi(self, fangshi_data: HetongZhifuFangshiCreate, created_by: str) -> HetongZhifuFangshiResponse:
        """创建支付方式"""
        # 验证乙方主体存在
        yifang_zhuti = self.db.query(HetongYifangZhuti).filter(
            HetongYifangZhuti.id == fangshi_data.yifang_zhuti_id,
            HetongYifangZhuti.is_deleted == "N"
        ).first()
        
        if not yifang_zhuti:
            raise HTTPException(status_code=404, detail="乙方主体不存在")
        
        # 如果设置为默认，需要将同一主体的其他支付方式设为非默认
        if fangshi_data.shi_moren == "Y":
            self.db.query(HetongZhifuFangshi).filter(
                HetongZhifuFangshi.yifang_zhuti_id == fangshi_data.yifang_zhuti_id,
                HetongZhifuFangshi.shi_moren == "Y",
                HetongZhifuFangshi.is_deleted == "N"
            ).update({"shi_moren": "N"})
        
        # 创建支付方式
        fangshi = HetongZhifuFangshi(
            **fangshi_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(fangshi)
        self.db.commit()
        self.db.refresh(fangshi)
        
        return HetongZhifuFangshiResponse.model_validate(fangshi)
    
    def get_zhifu_fangshi_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        yifang_zhuti_id: Optional[str] = None,
        zhifu_zhuangtai: Optional[str] = None
    ) -> HetongZhifuFangshiListResponse:
        """获取支付方式列表"""
        # 使用joinedload加载关联数据
        query = self.db.query(HetongZhifuFangshi).options(
            joinedload(HetongZhifuFangshi.yifang_zhuti),
            joinedload(HetongZhifuFangshi.zhifu_peizhi)
        ).filter(HetongZhifuFangshi.is_deleted == "N")

        # 搜索条件
        if search:
            query = query.filter(HetongZhifuFangshi.zhifu_mingcheng.contains(search))

        # 筛选条件
        if yifang_zhuti_id:
            query = query.filter(HetongZhifuFangshi.yifang_zhuti_id == yifang_zhuti_id)

        if zhifu_zhuangtai:
            query = query.filter(HetongZhifuFangshi.zhifu_zhuangtai == zhifu_zhuangtai)

        # 排序
        query = query.order_by(HetongZhifuFangshi.paixu, HetongZhifuFangshi.created_at.desc())

        # 分页
        total = query.count()
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()

        return HetongZhifuFangshiListResponse(
            total=total,
            items=[HetongZhifuFangshiResponse.model_validate(item) for item in items],
            page=page,
            size=size
        )
    
    def get_zhifu_fangshi_by_id(self, fangshi_id: str) -> HetongZhifuFangshiResponse:
        """根据ID获取支付方式"""
        fangshi = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.id == fangshi_id,
            HetongZhifuFangshi.is_deleted == "N"
        ).first()
        
        if not fangshi:
            raise HTTPException(status_code=404, detail="支付方式不存在")
        
        return HetongZhifuFangshiResponse.model_validate(fangshi)
    
    def update_zhifu_fangshi(self, fangshi_id: str, fangshi_data: HetongZhifuFangshiUpdate) -> HetongZhifuFangshiResponse:
        """更新支付方式"""
        fangshi = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.id == fangshi_id,
            HetongZhifuFangshi.is_deleted == "N"
        ).first()
        
        if not fangshi:
            raise HTTPException(status_code=404, detail="支付方式不存在")
        
        # 如果设置为默认，需要将同一主体的其他支付方式设为非默认
        if fangshi_data.shi_moren == "Y":
            self.db.query(HetongZhifuFangshi).filter(
                HetongZhifuFangshi.yifang_zhuti_id == fangshi.yifang_zhuti_id,
                HetongZhifuFangshi.shi_moren == "Y",
                HetongZhifuFangshi.id != fangshi_id,
                HetongZhifuFangshi.is_deleted == "N"
            ).update({"shi_moren": "N"})
        
        # 更新字段
        update_data = fangshi_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fangshi, field, value)
        
        fangshi.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(fangshi)
        
        return HetongZhifuFangshiResponse.model_validate(fangshi)
    
    def delete_zhifu_fangshi(self, fangshi_id: str) -> bool:
        """删除支付方式（软删除）"""
        fangshi = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.id == fangshi_id,
            HetongZhifuFangshi.is_deleted == "N"
        ).first()
        
        if not fangshi:
            raise HTTPException(status_code=404, detail="支付方式不存在")
        
        fangshi.is_deleted = "Y"
        fangshi.updated_at = datetime.now()
        self.db.commit()
        
        return True
    
    def get_zhifu_fangshi_by_yifang_zhuti(self, yifang_zhuti_id: str) -> list[HetongZhifuFangshiResponse]:
        """根据乙方主体ID获取支付方式列表"""
        fangshi_list = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.yifang_zhuti_id == yifang_zhuti_id,
            HetongZhifuFangshi.zhifu_zhuangtai == "active",
            HetongZhifuFangshi.is_deleted == "N"
        ).order_by(HetongZhifuFangshi.paixu, HetongZhifuFangshi.created_at.desc()).all()
        
        return [HetongZhifuFangshiResponse.model_validate(fangshi) for fangshi in fangshi_list]
    
    def get_default_zhifu_fangshi(self, yifang_zhuti_id: str) -> Optional[HetongZhifuFangshiResponse]:
        """获取乙方主体的默认支付方式"""
        fangshi = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.yifang_zhuti_id == yifang_zhuti_id,
            HetongZhifuFangshi.shi_moren == "Y",
            HetongZhifuFangshi.zhifu_zhuangtai == "active",
            HetongZhifuFangshi.is_deleted == "N"
        ).first()
        
        if fangshi:
            return HetongZhifuFangshiResponse.model_validate(fangshi)
        return None

    def set_default_zhifu_fangshi(self, zhifu_fangshi_id: str, updated_by: str) -> HetongZhifuFangshiResponse:
        """设置默认支付方式"""
        # 获取支付方式
        fangshi = self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.id == zhifu_fangshi_id,
            HetongZhifuFangshi.is_deleted == "N"
        ).first()

        if not fangshi:
            raise HTTPException(status_code=404, detail="支付方式不存在")

        # 将同一主体的其他支付方式设为非默认
        self.db.query(HetongZhifuFangshi).filter(
            HetongZhifuFangshi.yifang_zhuti_id == fangshi.yifang_zhuti_id,
            HetongZhifuFangshi.shi_moren == "Y",
            HetongZhifuFangshi.id != zhifu_fangshi_id,
            HetongZhifuFangshi.is_deleted == "N"
        ).update({"shi_moren": "N"})

        # 设置当前支付方式为默认
        fangshi.shi_moren = "Y"
        fangshi.updated_by = updated_by

        self.db.commit()
        self.db.refresh(fangshi)

        return HetongZhifuFangshiResponse.model_validate(fangshi)
