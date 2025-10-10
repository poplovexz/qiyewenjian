"""
服务记录管理服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from models.kehu_guanli import FuwuJilu, Kehu
from schemas.kehu_guanli.fuwu_jilu_schemas import (
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

    def get_service_statistics(self, kehu_id: Optional[str] = None) -> dict:
        """获取服务记录统计信息"""
        from sqlalchemy import func

        query = self.db.query(FuwuJilu).filter(FuwuJilu.is_deleted == "N")

        # 如果指定客户ID，只统计该客户的记录
        if kehu_id:
            query = query.filter(FuwuJilu.kehu_id == kehu_id)

        # 总记录数
        total_records = query.count()

        # 按沟通方式统计
        communication_stats = query.with_entities(
            FuwuJilu.goutong_fangshi,
            func.count(FuwuJilu.id).label('count')
        ).group_by(FuwuJilu.goutong_fangshi).all()

        # 按问题类型统计
        problem_stats = query.filter(
            FuwuJilu.wenti_leixing.isnot(None)
        ).with_entities(
            FuwuJilu.wenti_leixing,
            func.count(FuwuJilu.id).label('count')
        ).group_by(FuwuJilu.wenti_leixing).all()

        # 按处理状态统计
        status_stats = query.with_entities(
            FuwuJilu.chuli_zhuangtai,
            func.count(FuwuJilu.id).label('count')
        ).group_by(FuwuJilu.chuli_zhuangtai).all()

        # 本月记录数
        from datetime import datetime, timedelta
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_records = query.filter(
            FuwuJilu.created_at >= current_month_start
        ).count()

        return {
            "total_records": total_records,
            "monthly_records": monthly_records,
            "communication_distribution": {method: count for method, count in communication_stats},
            "problem_type_distribution": {ptype: count for ptype, count in problem_stats},
            "status_distribution": {status: count for status, count in status_stats},
            "pending_count": dict(status_stats).get("pending", 0),
            "processing_count": dict(status_stats).get("processing", 0),
            "completed_count": dict(status_stats).get("completed", 0)
        }

    def batch_update_status(self, record_ids: List[str], new_status: str, chuli_jieguo: Optional[str], updated_by: str) -> dict:
        """批量更新服务记录状态"""
        # 验证状态值
        allowed_statuses = ["pending", "processing", "completed", "cancelled"]
        if new_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"无效的处理状态: {new_status}")

        # 查询要更新的记录
        records = self.db.query(FuwuJilu).filter(
            FuwuJilu.id.in_(record_ids),
            FuwuJilu.is_deleted == "N"
        ).all()

        if not records:
            raise HTTPException(status_code=404, detail="未找到要更新的服务记录")

        # 批量更新
        updated_count = 0
        for record in records:
            record.chuli_zhuangtai = new_status
            if chuli_jieguo:
                record.chuli_jieguo = chuli_jieguo
            record.chuli_ren_id = updated_by
            record.updated_by = updated_by
            updated_count += 1

        self.db.commit()

        return {
            "updated_count": updated_count,
            "total_requested": len(record_ids),
            "new_status": new_status
        }

    def batch_delete(self, record_ids: List[str], deleted_by: str) -> dict:
        """批量删除服务记录（软删除）"""
        # 查询要删除的记录
        records = self.db.query(FuwuJilu).filter(
            FuwuJilu.id.in_(record_ids),
            FuwuJilu.is_deleted == "N"
        ).all()

        if not records:
            raise HTTPException(status_code=404, detail="未找到要删除的服务记录")

        # 批量软删除
        deleted_count = 0
        for record in records:
            record.is_deleted = "Y"
            record.updated_by = deleted_by
            deleted_count += 1

        self.db.commit()

        return {
            "deleted_count": deleted_count,
            "total_requested": len(record_ids)
        }

    def get_customer_service_summary(self, kehu_id: str) -> dict:
        """获取客户服务记录摘要"""
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()

        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")

        # 获取该客户的服务统计
        stats = self.get_service_statistics(kehu_id)

        # 最近的服务记录
        recent_records = self.db.query(FuwuJilu).filter(
            FuwuJilu.kehu_id == kehu_id,
            FuwuJilu.is_deleted == "N"
        ).order_by(FuwuJilu.created_at.desc()).limit(5).all()

        # 待处理的问题数量
        pending_issues = self.db.query(FuwuJilu).filter(
            FuwuJilu.kehu_id == kehu_id,
            FuwuJilu.chuli_zhuangtai.in_(["pending", "processing"]),
            FuwuJilu.is_deleted == "N"
        ).count()

        return {
            "customer_info": {
                "id": kehu.id,
                "gongsi_mingcheng": kehu.gongsi_mingcheng,
                "kehu_zhuangtai": kehu.kehu_zhuangtai
            },
            "service_statistics": stats,
            "recent_records": [FuwuJiluResponse.model_validate(record) for record in recent_records],
            "pending_issues": pending_issues
        }
