"""
支付通知管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime

from models.zhifu_guanli import ZhifuTongzhi, ZhifuDingdan
from models.hetong_guanli import Hetong
from models.yonghu_guanli import Yonghu
from schemas.zhifu_guanli.zhifu_tongzhi_schemas import (
    ZhifuTongzhiCreate,
    ZhifuTongzhiUpdate,
    ZhifuTongzhiResponse,
    ZhifuTongzhiListResponse,
    ZhifuTongzhiListParams
)
from core.events import publish, EventNames


class ZhifuTongzhiService:
    """支付通知管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_zhifu_tongzhi(self, tongzhi_data: ZhifuTongzhiCreate, created_by: str) -> ZhifuTongzhiResponse:
        """创建支付通知"""
        # 验证接收人是否存在
        jieshou_ren = self.db.query(Yonghu).filter(
            Yonghu.id == tongzhi_data.jieshou_ren_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not jieshou_ren:
            raise HTTPException(status_code=404, detail="接收人不存在")
        
        # 如果指定了支付订单ID，验证是否存在
        if tongzhi_data.zhifu_dingdan_id:
            zhifu_dingdan = self.db.query(ZhifuDingdan).filter(
                ZhifuDingdan.id == tongzhi_data.zhifu_dingdan_id,
                ZhifuDingdan.is_deleted == "N"
            ).first()
            
            if not zhifu_dingdan:
                raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 如果指定了合同ID，验证是否存在
        if tongzhi_data.hetong_id:
            hetong = self.db.query(Hetong).filter(
                Hetong.id == tongzhi_data.hetong_id,
                Hetong.is_deleted == "N"
            ).first()
            
            if not hetong:
                raise HTTPException(status_code=404, detail="合同不存在")
        
        # 创建支付通知
        zhifu_tongzhi = ZhifuTongzhi(
            **tongzhi_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(zhifu_tongzhi)
        self.db.commit()
        self.db.refresh(zhifu_tongzhi)
        
        # 发布通知发送事件
        publish(EventNames.NOTIFICATION_SENT, {
            "tongzhi_id": zhifu_tongzhi.id,
            "jieshou_ren_id": tongzhi_data.jieshou_ren_id,
            "tongzhi_leixing": tongzhi_data.tongzhi_leixing,
            "tongzhi_biaoti": tongzhi_data.tongzhi_biaoti,
            "youxian_ji": tongzhi_data.youxian_ji,
            "fasong_qudao": tongzhi_data.fasong_qudao,
            "created_by": created_by
        })
        
        return ZhifuTongzhiResponse.model_validate(zhifu_tongzhi)
    
    def get_zhifu_tongzhi_by_id(self, tongzhi_id: str) -> ZhifuTongzhiResponse:
        """根据ID获取支付通知"""
        zhifu_tongzhi = self.db.query(ZhifuTongzhi).filter(
            ZhifuTongzhi.id == tongzhi_id,
            ZhifuTongzhi.is_deleted == "N"
        ).first()
        
        if not zhifu_tongzhi:
            raise HTTPException(status_code=404, detail="支付通知不存在")
        
        return ZhifuTongzhiResponse.model_validate(zhifu_tongzhi)
    
    def update_zhifu_tongzhi(self, tongzhi_id: str, tongzhi_data: ZhifuTongzhiUpdate, updated_by: str) -> ZhifuTongzhiResponse:
        """更新支付通知"""
        zhifu_tongzhi = self.db.query(ZhifuTongzhi).filter(
            ZhifuTongzhi.id == tongzhi_id,
            ZhifuTongzhi.is_deleted == "N"
        ).first()
        
        if not zhifu_tongzhi:
            raise HTTPException(status_code=404, detail="支付通知不存在")
        
        # 记录原状态
        old_status = zhifu_tongzhi.tongzhi_zhuangtai
        
        # 更新字段
        update_data = tongzhi_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zhifu_tongzhi, field, value)
        
        zhifu_tongzhi.updated_by = updated_by
        zhifu_tongzhi.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_tongzhi)
        
        # 如果通知状态变为已读，发布事件
        new_status = zhifu_tongzhi.tongzhi_zhuangtai
        if old_status == "unread" and new_status == "read":
            publish(EventNames.NOTIFICATION_READ, {
                "tongzhi_id": zhifu_tongzhi.id,
                "jieshou_ren_id": zhifu_tongzhi.jieshou_ren_id,
                "tongzhi_leixing": zhifu_tongzhi.tongzhi_leixing,
                "yuedu_shijian": zhifu_tongzhi.yuedu_shijian.isoformat() if zhifu_tongzhi.yuedu_shijian else None,
                "updated_by": updated_by
            })
        
        return ZhifuTongzhiResponse.model_validate(zhifu_tongzhi)
    
    def get_zhifu_tongzhi_list(self, params: ZhifuTongzhiListParams) -> ZhifuTongzhiListResponse:
        """获取支付通知列表"""
        query = self.db.query(ZhifuTongzhi).filter(ZhifuTongzhi.is_deleted == "N")
        
        # 搜索条件
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    ZhifuTongzhi.tongzhi_biaoti.ilike(search_pattern),
                    ZhifuTongzhi.tongzhi_neirong.ilike(search_pattern)
                )
            )
        
        # 筛选条件
        if params.jieshou_ren_id:
            query = query.filter(ZhifuTongzhi.jieshou_ren_id == params.jieshou_ren_id)
        
        if params.tongzhi_leixing:
            query = query.filter(ZhifuTongzhi.tongzhi_leixing == params.tongzhi_leixing)
        
        if params.tongzhi_zhuangtai:
            query = query.filter(ZhifuTongzhi.tongzhi_zhuangtai == params.tongzhi_zhuangtai)
        
        if params.youxian_ji:
            query = query.filter(ZhifuTongzhi.youxian_ji == params.youxian_ji)
        
        if params.fasong_qudao:
            query = query.filter(ZhifuTongzhi.fasong_qudao == params.fasong_qudao)
        
        if params.start_date:
            query = query.filter(ZhifuTongzhi.fasong_shijian >= params.start_date)
        
        if params.end_date:
            query = query.filter(ZhifuTongzhi.fasong_shijian <= params.end_date)
        
        # 总数
        total = query.count()
        
        # 分页和排序
        items = query.order_by(desc(ZhifuTongzhi.fasong_shijian)).offset(
            (params.page - 1) * params.size
        ).limit(params.size).all()
        
        return ZhifuTongzhiListResponse(
            total=total,
            items=[ZhifuTongzhiResponse.model_validate(item) for item in items],
            page=params.page,
            size=params.size
        )
    
    def mark_as_read(self, tongzhi_id: str, user_id: str) -> ZhifuTongzhiResponse:
        """标记通知为已读"""
        zhifu_tongzhi = self.db.query(ZhifuTongzhi).filter(
            ZhifuTongzhi.id == tongzhi_id,
            ZhifuTongzhi.jieshou_ren_id == user_id,
            ZhifuTongzhi.is_deleted == "N"
        ).first()
        
        if not zhifu_tongzhi:
            raise HTTPException(status_code=404, detail="支付通知不存在或无权限")
        
        # 如果已经是已读状态，直接返回
        if zhifu_tongzhi.tongzhi_zhuangtai == "read":
            return ZhifuTongzhiResponse.model_validate(zhifu_tongzhi)
        
        # 标记为已读
        zhifu_tongzhi.tongzhi_zhuangtai = "read"
        zhifu_tongzhi.yuedu_shijian = datetime.now()
        zhifu_tongzhi.updated_by = user_id
        zhifu_tongzhi.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_tongzhi)
        
        # 发布通知已读事件
        publish(EventNames.NOTIFICATION_READ, {
            "tongzhi_id": zhifu_tongzhi.id,
            "jieshou_ren_id": user_id,
            "tongzhi_leixing": zhifu_tongzhi.tongzhi_leixing,
            "yuedu_shijian": zhifu_tongzhi.yuedu_shijian.isoformat(),
            "updated_by": user_id
        })
        
        return ZhifuTongzhiResponse.model_validate(zhifu_tongzhi)
    
    def get_unread_count(self, user_id: str) -> int:
        """获取用户未读通知数量"""
        return self.db.query(ZhifuTongzhi).filter(
            ZhifuTongzhi.jieshou_ren_id == user_id,
            ZhifuTongzhi.tongzhi_zhuangtai == "unread",
            ZhifuTongzhi.is_deleted == "N"
        ).count()
