"""
支付流水管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime
from decimal import Decimal
import uuid

from ...models.zhifu_guanli import ZhifuLiushui, ZhifuDingdan
from ...models.kehu_guanli import Kehu
from ...schemas.zhifu_guanli.zhifu_liushui_schemas import (
    ZhifuLiushuiCreate,
    ZhifuLiushuiUpdate,
    ZhifuLiushuiResponse,
    ZhifuLiushuiListResponse,
    ZhifuLiushuiListParams
)
from ...core.events import publish, EventNames


class ZhifuLiushuiService:
    """支付流水管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_zhifu_liushui(self, liushui_data: ZhifuLiushuiCreate, created_by: str) -> ZhifuLiushuiResponse:
        """创建支付流水"""
        # 验证支付订单是否存在
        zhifu_dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == liushui_data.zhifu_dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not zhifu_dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == liushui_data.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 生成流水编号
        liushui_bianhao = self._generate_liushui_bianhao()
        
        # 创建支付流水
        zhifu_liushui = ZhifuLiushui(
            liushui_bianhao=liushui_bianhao,
            **liushui_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(zhifu_liushui)
        
        # 如果是收入流水，更新订单的实付金额
        if liushui_data.liushui_leixing == "income":
            zhifu_dingdan.shifu_jine = (zhifu_dingdan.shifu_jine or Decimal('0')) + liushui_data.jiaoyijine
            
            # 检查是否已完全支付
            if zhifu_dingdan.shifu_jine >= zhifu_dingdan.yingfu_jine:
                zhifu_dingdan.zhifu_zhuangtai = "paid"
                zhifu_dingdan.zhifu_shijian = liushui_data.jiaoyishijian
        
        self.db.commit()
        self.db.refresh(zhifu_liushui)
        
        # 发布财务记录创建事件
        publish(EventNames.FINANCIAL_RECORD_CREATED, {
            "liushui_id": zhifu_liushui.id,
            "zhifu_dingdan_id": liushui_data.zhifu_dingdan_id,
            "kehu_id": liushui_data.kehu_id,
            "liushui_leixing": liushui_data.liushui_leixing,
            "jiaoyijine": float(liushui_data.jiaoyijine),
            "zhifu_fangshi": liushui_data.zhifu_fangshi,
            "created_by": created_by
        })
        
        return ZhifuLiushuiResponse.model_validate(zhifu_liushui)
    
    def get_zhifu_liushui_by_id(self, liushui_id: str) -> ZhifuLiushuiResponse:
        """根据ID获取支付流水"""
        zhifu_liushui = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == liushui_id,
            ZhifuLiushui.is_deleted == "N"
        ).first()
        
        if not zhifu_liushui:
            raise HTTPException(status_code=404, detail="支付流水不存在")
        
        return ZhifuLiushuiResponse.model_validate(zhifu_liushui)
    
    def update_zhifu_liushui(self, liushui_id: str, liushui_data: ZhifuLiushuiUpdate, updated_by: str) -> ZhifuLiushuiResponse:
        """更新支付流水"""
        zhifu_liushui = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == liushui_id,
            ZhifuLiushui.is_deleted == "N"
        ).first()
        
        if not zhifu_liushui:
            raise HTTPException(status_code=404, detail="支付流水不存在")
        
        # 更新字段
        update_data = liushui_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zhifu_liushui, field, value)
        
        zhifu_liushui.updated_by = updated_by
        zhifu_liushui.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_liushui)
        
        return ZhifuLiushuiResponse.model_validate(zhifu_liushui)
    
    def get_zhifu_liushui_list(self, params: ZhifuLiushuiListParams) -> ZhifuLiushuiListResponse:
        """获取支付流水列表"""
        query = self.db.query(ZhifuLiushui).filter(ZhifuLiushui.is_deleted == "N")
        
        # 搜索条件
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    ZhifuLiushui.liushui_bianhao.ilike(search_pattern),
                    ZhifuLiushui.disanfang_liushui_hao.ilike(search_pattern),
                    ZhifuLiushui.zhifu_zhanghu.ilike(search_pattern)
                )
            )
        
        # 筛选条件
        if params.zhifu_dingdan_id:
            query = query.filter(ZhifuLiushui.zhifu_dingdan_id == params.zhifu_dingdan_id)
        
        if params.kehu_id:
            query = query.filter(ZhifuLiushui.kehu_id == params.kehu_id)
        
        if params.liushui_leixing:
            query = query.filter(ZhifuLiushui.liushui_leixing == params.liushui_leixing)
        
        if params.zhifu_fangshi:
            query = query.filter(ZhifuLiushui.zhifu_fangshi == params.zhifu_fangshi)
        
        if params.liushui_zhuangtai:
            query = query.filter(ZhifuLiushui.liushui_zhuangtai == params.liushui_zhuangtai)
        
        if params.duizhang_zhuangtai:
            query = query.filter(ZhifuLiushui.duizhang_zhuangtai == params.duizhang_zhuangtai)
        
        if params.start_date:
            query = query.filter(ZhifuLiushui.jiaoyishijian >= params.start_date)
        
        if params.end_date:
            query = query.filter(ZhifuLiushui.jiaoyishijian <= params.end_date)
        
        # 总数
        total = query.count()
        
        # 分页和排序
        items = query.order_by(desc(ZhifuLiushui.jiaoyishijian)).offset(
            (params.page - 1) * params.size
        ).limit(params.size).all()
        
        return ZhifuLiushuiListResponse(
            total=total,
            items=[ZhifuLiushuiResponse.model_validate(item) for item in items],
            page=params.page,
            size=params.size
        )
    
    def confirm_liushui_by_finance(self, liushui_id: str, confirmed_by: str) -> ZhifuLiushuiResponse:
        """财务确认流水"""
        zhifu_liushui = self.db.query(ZhifuLiushui).filter(
            ZhifuLiushui.id == liushui_id,
            ZhifuLiushui.is_deleted == "N"
        ).first()
        
        if not zhifu_liushui:
            raise HTTPException(status_code=404, detail="支付流水不存在")
        
        # 更新财务确认信息
        zhifu_liushui.caiwu_queren_ren = confirmed_by
        zhifu_liushui.caiwu_queren_shijian = datetime.now()
        zhifu_liushui.duizhang_zhuangtai = "matched"
        zhifu_liushui.updated_by = confirmed_by
        zhifu_liushui.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_liushui)
        
        return ZhifuLiushuiResponse.model_validate(zhifu_liushui)
    
    def _generate_liushui_bianhao(self) -> str:
        """生成流水编号"""
        # 格式：LS + YYYYMMDD + 6位随机数
        today = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().int)[:6]
        return f"LS{today}{random_suffix}"
