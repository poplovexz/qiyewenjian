"""
线索跟进记录管理服务
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.xiansuo_guanli import XiansuoGenjin, Xiansuo
from models.yonghu_guanli import Yonghu
from schemas.xiansuo_guanli import (
    XiansuoGenjinCreate,
    XiansuoGenjinUpdate,
    XiansuoGenjinResponse,
    XiansuoGenjinListResponse
)


class XiansuoGenjinService:
    """线索跟进记录管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_genjin(self, genjin_data: XiansuoGenjinCreate, created_by: str) -> XiansuoGenjinResponse:
        """创建线索跟进记录"""
        # 验证线索是否存在
        xiansuo = self.db.query(Xiansuo).filter(
            Xiansuo.id == genjin_data.xiansuo_id,
            Xiansuo.is_deleted == "N"
        ).first()
        
        if not xiansuo:
            raise HTTPException(status_code=404, detail="线索不存在")
        
        # 获取跟进人信息
        genjin_ren = self.db.query(Yonghu).filter(
            Yonghu.id == created_by,
            Yonghu.is_deleted == "N"
        ).first()
        
        # 设置跟进时间
        genjin_shijian = genjin_data.genjin_shijian or datetime.utcnow()
        
        # 创建跟进记录
        genjin = XiansuoGenjin(
            xiansuo_id=genjin_data.xiansuo_id,
            genjin_fangshi=genjin_data.genjin_fangshi,
            genjin_shijian=genjin_shijian,
            genjin_neirong=genjin_data.genjin_neirong,
            kehu_fankui=genjin_data.kehu_fankui,
            kehu_taidu=genjin_data.kehu_taidu,
            xiaci_genjin_shijian=genjin_data.xiaci_genjin_shijian,
            xiaci_genjin_neirong=genjin_data.xiaci_genjin_neirong,
            genjin_jieguo=genjin_data.genjin_jieguo,
            fujian_lujing=genjin_data.fujian_lujing,
            genjin_ren_id=created_by,
            genjin_ren_xingming=genjin_ren.xingming if genjin_ren else None,
            created_by=created_by
        )
        
        self.db.add(genjin)
        
        # 更新线索的跟进信息
        if xiansuo.shouci_genjin_shijian is None:
            xiansuo.shouci_genjin_shijian = genjin_shijian
        
        xiansuo.zuijin_genjin_shijian = genjin_shijian
        xiansuo.xiaci_genjin_shijian = genjin_data.xiaci_genjin_shijian
        xiansuo.genjin_cishu = (xiansuo.genjin_cishu or 0) + 1
        xiansuo.updated_by = created_by
        
        self.db.commit()
        self.db.refresh(genjin)
        
        return XiansuoGenjinResponse.model_validate(genjin)
    
    def get_genjin_by_id(self, genjin_id: str) -> Optional[XiansuoGenjinResponse]:
        """根据ID获取跟进记录"""
        genjin = self.db.query(XiansuoGenjin).filter(
            XiansuoGenjin.id == genjin_id,
            XiansuoGenjin.is_deleted == "N"
        ).first()
        
        if not genjin:
            return None
        
        return XiansuoGenjinResponse.model_validate(genjin)
    
    def get_genjin_list(
        self,
        page: int = 1,
        size: int = 20,
        xiansuo_id: Optional[str] = None,
        genjin_ren_id: Optional[str] = None,
        genjin_fangshi: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> XiansuoGenjinListResponse:
        """获取跟进记录列表"""
        query = self.db.query(XiansuoGenjin).filter(XiansuoGenjin.is_deleted == "N")
        
        # 线索筛选
        if xiansuo_id:
            query = query.filter(XiansuoGenjin.xiansuo_id == xiansuo_id)
        
        # 跟进人筛选
        if genjin_ren_id:
            query = query.filter(XiansuoGenjin.genjin_ren_id == genjin_ren_id)
        
        # 跟进方式筛选
        if genjin_fangshi:
            query = query.filter(XiansuoGenjin.genjin_fangshi == genjin_fangshi)
        
        # 时间范围筛选
        if start_date:
            query = query.filter(XiansuoGenjin.genjin_shijian >= start_date)
        if end_date:
            query = query.filter(XiansuoGenjin.genjin_shijian <= end_date)
        
        # 排序
        query = query.order_by(XiansuoGenjin.genjin_shijian.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = (page - 1) * size
        genjin_list = query.offset(skip).limit(size).all()
        
        return XiansuoGenjinListResponse(
            items=[XiansuoGenjinResponse.model_validate(genjin) for genjin in genjin_list],
            total=total,
            page=page,
            size=size
        )
    
    def update_genjin(self, genjin_id: str, genjin_data: XiansuoGenjinUpdate, updated_by: str) -> XiansuoGenjinResponse:
        """更新跟进记录"""
        genjin = self.db.query(XiansuoGenjin).filter(
            XiansuoGenjin.id == genjin_id,
            XiansuoGenjin.is_deleted == "N"
        ).first()
        
        if not genjin:
            raise HTTPException(status_code=404, detail="跟进记录不存在")
        
        # 更新字段
        update_data = genjin_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(genjin, field, value)
        
        genjin.updated_by = updated_by
        
        # 如果更新了下次跟进时间，同步更新线索表
        if genjin_data.xiaci_genjin_shijian is not None:
            xiansuo = self.db.query(Xiansuo).filter(
                Xiansuo.id == genjin.xiansuo_id,
                Xiansuo.is_deleted == "N"
            ).first()
            
            if xiansuo:
                xiansuo.xiaci_genjin_shijian = genjin_data.xiaci_genjin_shijian
                xiansuo.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(genjin)
        
        return XiansuoGenjinResponse.model_validate(genjin)
    
    def delete_genjin(self, genjin_id: str, deleted_by: str) -> bool:
        """删除跟进记录（软删除）"""
        genjin = self.db.query(XiansuoGenjin).filter(
            XiansuoGenjin.id == genjin_id,
            XiansuoGenjin.is_deleted == "N"
        ).first()
        
        if not genjin:
            raise HTTPException(status_code=404, detail="跟进记录不存在")
        
        # 软删除
        genjin.is_deleted = "Y"
        genjin.updated_by = deleted_by
        
        # 更新线索的跟进次数
        xiansuo = self.db.query(Xiansuo).filter(
            Xiansuo.id == genjin.xiansuo_id,
            Xiansuo.is_deleted == "N"
        ).first()
        
        if xiansuo and xiansuo.genjin_cishu > 0:
            xiansuo.genjin_cishu -= 1
            xiansuo.updated_by = deleted_by
        
        self.db.commit()
        
        return True
    
    def get_xiansuo_genjin_list(self, xiansuo_id: str) -> list[XiansuoGenjinResponse]:
        """获取指定线索的所有跟进记录"""
        genjin_list = self.db.query(XiansuoGenjin).filter(
            XiansuoGenjin.xiansuo_id == xiansuo_id,
            XiansuoGenjin.is_deleted == "N"
        ).order_by(XiansuoGenjin.genjin_shijian.desc()).all()
        
        return [XiansuoGenjinResponse.model_validate(genjin) for genjin in genjin_list]
