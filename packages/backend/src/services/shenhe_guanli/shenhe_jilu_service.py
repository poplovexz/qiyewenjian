"""
审核记录服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from fastapi import HTTPException

from models.shenhe_guanli import ShenheJilu, ShenheLiucheng
from schemas.shenhe_guanli import (
    ShenheJiluResponse,
    ShenheJiluListParams,
    ShenheJiluUpdate
)


class ShenheJiluService:
    """审核记录服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_shenhe_jilu_list(self, params: ShenheJiluListParams) -> Dict[str, Any]:
        """获取审核记录列表"""
        query = self.db.query(ShenheJilu).filter(ShenheJilu.is_deleted == "N")
        
        # 筛选条件
        if params.liucheng_id:
            query = query.filter(ShenheJilu.liucheng_id == params.liucheng_id)
        
        if params.shenhe_ren_id:
            query = query.filter(ShenheJilu.shenhe_ren_id == params.shenhe_ren_id)
        
        if params.jilu_zhuangtai:
            query = query.filter(ShenheJilu.jilu_zhuangtai == params.jilu_zhuangtai)
        
        # 排序
        if params.sort_by:
            sort_column = getattr(ShenheJilu, params.sort_by, None)
            if sort_column:
                if params.sort_order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        
        # 分页
        total = query.count()
        offset = (params.page - 1) * params.size
        items = query.offset(offset).limit(params.size).all()
        
        return {
            "items": [self._to_response(item) for item in items],
            "total": total,
            "page": params.page,
            "size": params.size,
            "pages": (total + params.size - 1) // params.size
        }
    
    def get_shenhe_jilu_by_workflow(self, workflow_id: str) -> List[ShenheJiluResponse]:
        """根据流程ID获取审核记录"""
        records = self.db.query(ShenheJilu).filter(
            ShenheJilu.liucheng_id == workflow_id,
            ShenheJilu.is_deleted == "N"
        ).order_by(ShenheJilu.buzhou_bianhao).all()
        
        return [self._to_response(record) for record in records]
    
    def get_shenhe_jilu_by_id(self, jilu_id: str) -> ShenheJiluResponse:
        """根据ID获取审核记录详情"""
        jilu = self.db.query(ShenheJilu).options(
            joinedload(ShenheJilu.shenhe_liucheng)
        ).filter(
            ShenheJilu.id == jilu_id,
            ShenheJilu.is_deleted == "N"
        ).first()
        
        if not jilu:
            raise HTTPException(status_code=404, detail="审核记录不存在")
        
        return self._to_response(jilu)
    
    def update_shenhe_jilu(self, jilu_id: str, jilu_data: ShenheJiluUpdate, updated_by: str) -> ShenheJiluResponse:
        """更新审核记录"""
        jilu = self.db.query(ShenheJilu).filter(
            ShenheJilu.id == jilu_id,
            ShenheJilu.is_deleted == "N"
        ).first()
        
        if not jilu:
            raise HTTPException(status_code=404, detail="审核记录不存在")
        
        # 更新字段
        update_data = jilu_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(jilu, field, value)
        
        jilu.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(jilu)
        
        return self._to_response(jilu)
    
    def get_user_audit_statistics(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取用户审核统计"""
        query = self.db.query(ShenheJilu).filter(
            ShenheJilu.shenhe_ren_id == user_id,
            ShenheJilu.is_deleted == "N"
        )
        
        # 时间范围筛选
        if start_date:
            query = query.filter(ShenheJilu.created_at >= start_date)
        if end_date:
            query = query.filter(ShenheJilu.created_at <= end_date)
        
        # 统计各种状态的数量
        total_count = query.count()
        pending_count = query.filter(ShenheJilu.jilu_zhuangtai == "daichuli").count()
        processed_count = query.filter(ShenheJilu.jilu_zhuangtai == "yichuli").count()
        skipped_count = query.filter(ShenheJilu.jilu_zhuangtai == "yitiaoguo").count()
        
        # 统计审核结果
        approved_count = query.filter(ShenheJilu.shenhe_jieguo == "tongguo").count()
        rejected_count = query.filter(ShenheJilu.shenhe_jieguo == "jujue").count()
        forwarded_count = query.filter(ShenheJilu.shenhe_jieguo == "zhuanfa").count()
        
        # 计算平均处理时间
        processed_records = query.filter(
            ShenheJilu.jilu_zhuangtai == "yichuli",
            ShenheJilu.shenhe_shijian.isnot(None)
        ).all()
        
        avg_processing_time = None
        if processed_records:
            total_time = sum([
                (record.shenhe_shijian - record.created_at).total_seconds()
                for record in processed_records
                if record.shenhe_shijian
            ])
            avg_processing_time = total_time / len(processed_records) / 3600  # 转换为小时
        
        return {
            "total_count": total_count,
            "pending_count": pending_count,
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "forwarded_count": forwarded_count,
            "avg_processing_time_hours": round(avg_processing_time, 2) if avg_processing_time else None,
            "processing_rate": round(processed_count / total_count * 100, 2) if total_count > 0 else 0
        }
    
    def get_overdue_audit_records(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取超期的审核记录"""
        query = self.db.query(ShenheJilu).join(
            ShenheLiucheng, ShenheJilu.liucheng_id == ShenheLiucheng.id
        ).filter(
            ShenheJilu.jilu_zhuangtai == "daichuli",
            ShenheJilu.qiwang_chuli_shijian < datetime.now(),
            ShenheJilu.is_deleted == "N",
            ShenheLiucheng.shenhe_zhuangtai == "shenhzhong",
            ShenheLiucheng.is_deleted == "N"
        )
        
        if user_id:
            query = query.filter(ShenheJilu.shenhe_ren_id == user_id)
        
        records = query.all()
        
        result = []
        for record in records:
            workflow = record.shenhe_liucheng
            overdue_hours = (datetime.now() - record.qiwang_chuli_shijian).total_seconds() / 3600
            
            result.append({
                "record_id": record.id,
                "workflow_id": workflow.id,
                "workflow_number": workflow.liucheng_bianhao,
                "audit_type": workflow.shenhe_leixing,
                "step_name": record.buzhou_mingcheng,
                "auditor_id": record.shenhe_ren_id,
                "expected_time": record.qiwang_chuli_shijian,
                "overdue_hours": round(overdue_hours, 2),
                "created_at": record.created_at
            })
        
        return result
    
    @staticmethod
    def _to_response(jilu: ShenheJilu) -> ShenheJiluResponse:
        """转换为响应模型"""
        return ShenheJiluResponse(
            id=jilu.id,
            liucheng_id=jilu.liucheng_id,
            buzhou_bianhao=jilu.buzhou_bianhao,
            buzhou_mingcheng=jilu.buzhou_mingcheng,
            shenhe_ren_id=jilu.shenhe_ren_id,
            shenhe_jieguo=jilu.shenhe_jieguo,
            shenhe_yijian=jilu.shenhe_yijian,
            shenhe_shijian=jilu.shenhe_shijian,
            fujian_lujing=jilu.fujian_lujing,
            fujian_miaoshu=jilu.fujian_miaoshu,
            jilu_zhuangtai=jilu.jilu_zhuangtai,
            qiwang_chuli_shijian=jilu.qiwang_chuli_shijian,
            beizhu=jilu.beizhu,
            created_at=jilu.created_at,
            updated_at=jilu.updated_at,
            created_by=jilu.created_by
        )
