"""
支付订单管理服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from fastapi import HTTPException
from datetime import datetime
from decimal import Decimal
import uuid

from models.zhifu_guanli import ZhifuDingdan
from models.hetong_guanli import Hetong, HetongYifangZhuti
from models.kehu_guanli import Kehu
from schemas.zhifu_guanli.zhifu_dingdan_schemas import (
    ZhifuDingdanCreate,
    ZhifuDingdanUpdate,
    ZhifuDingdanResponse,
    ZhifuDingdanListResponse,
    ZhifuDingdanListParams,
    ZhifuDingdanStatistics
)
from core.events import publish, EventNames


class ZhifuDingdanService:
    """支付订单管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_zhifu_dingdan(self, dingdan_data: ZhifuDingdanCreate, created_by: str) -> ZhifuDingdanResponse:
        """创建支付订单"""
        # 验证合同是否存在
        hetong = self.db.query(Hetong).filter(
            Hetong.id == dingdan_data.hetong_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == dingdan_data.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 生成订单编号
        dingdan_bianhao = self._generate_dingdan_bianhao()
        
        # 创建支付订单
        zhifu_dingdan = ZhifuDingdan(
            dingdan_bianhao=dingdan_bianhao,
            chuangjian_shijian=datetime.now(),
            **dingdan_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(zhifu_dingdan)
        self.db.commit()
        self.db.refresh(zhifu_dingdan)
        
        # 发布支付订单创建事件
        publish(EventNames.PAYMENT_ORDER_CREATED, {
            "zhifu_dingdan_id": zhifu_dingdan.id,
            "hetong_id": dingdan_data.hetong_id,
            "kehu_id": dingdan_data.kehu_id,
            "dingdan_jine": float(dingdan_data.dingdan_jine),
            "zhifu_leixing": dingdan_data.zhifu_leixing,
            "created_by": created_by
        })
        
        return ZhifuDingdanResponse.model_validate(zhifu_dingdan)
    
    def get_zhifu_dingdan_by_id(self, dingdan_id: str) -> ZhifuDingdanResponse:
        """根据ID获取支付订单"""
        zhifu_dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not zhifu_dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        return ZhifuDingdanResponse.model_validate(zhifu_dingdan)
    
    def update_zhifu_dingdan(self, dingdan_id: str, dingdan_data: ZhifuDingdanUpdate, updated_by: str) -> ZhifuDingdanResponse:
        """更新支付订单"""
        zhifu_dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not zhifu_dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 记录原状态
        old_status = zhifu_dingdan.zhifu_zhuangtai
        
        # 更新字段
        update_data = dingdan_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zhifu_dingdan, field, value)
        
        zhifu_dingdan.updated_by = updated_by
        zhifu_dingdan.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(zhifu_dingdan)
        
        # 如果支付状态发生变化，发布事件
        new_status = zhifu_dingdan.zhifu_zhuangtai
        if old_status != new_status:
            if new_status == "paid":
                publish(EventNames.PAYMENT_SUCCESS, {
                    "zhifu_dingdan_id": zhifu_dingdan.id,
                    "hetong_id": zhifu_dingdan.hetong_id,
                    "kehu_id": zhifu_dingdan.kehu_id,
                    "dingdan_jine": float(zhifu_dingdan.dingdan_jine),
                    "zhifu_shijian": zhifu_dingdan.zhifu_shijian.isoformat() if zhifu_dingdan.zhifu_shijian else None,
                    "updated_by": updated_by
                })
            elif new_status == "failed":
                publish(EventNames.PAYMENT_FAILED, {
                    "zhifu_dingdan_id": zhifu_dingdan.id,
                    "hetong_id": zhifu_dingdan.hetong_id,
                    "kehu_id": zhifu_dingdan.kehu_id,
                    "updated_by": updated_by
                })
        
        return ZhifuDingdanResponse.model_validate(zhifu_dingdan)
    
    def get_zhifu_dingdan_list(self, params: ZhifuDingdanListParams) -> ZhifuDingdanListResponse:
        """获取支付订单列表"""
        query = self.db.query(ZhifuDingdan).filter(ZhifuDingdan.is_deleted == "N")

        # 搜索条件
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    ZhifuDingdan.dingdan_bianhao.ilike(search_pattern),
                    ZhifuDingdan.dingdan_mingcheng.ilike(search_pattern)
                )
            )

        # 筛选条件
        if params.hetong_id:
            query = query.filter(ZhifuDingdan.hetong_id == params.hetong_id)

        if params.kehu_id:
            query = query.filter(ZhifuDingdan.kehu_id == params.kehu_id)

        if params.zhifu_leixing:
            query = query.filter(ZhifuDingdan.zhifu_leixing == params.zhifu_leixing)

        if params.zhifu_zhuangtai:
            query = query.filter(ZhifuDingdan.zhifu_zhuangtai == params.zhifu_zhuangtai)

        if params.start_date:
            query = query.filter(ZhifuDingdan.chuangjian_shijian >= params.start_date)

        if params.end_date:
            query = query.filter(ZhifuDingdan.chuangjian_shijian <= params.end_date)

        # 总数
        total = query.count()

        # 分页和排序
        items = query.order_by(desc(ZhifuDingdan.chuangjian_shijian)).offset(
            (params.page - 1) * params.size
        ).limit(params.size).all()

        # 构建响应，包含合同和客户信息
        response_items = []
        for item in items:
            item_dict = ZhifuDingdanResponse.model_validate(item).model_dump()

            # 查询关联的合同信息
            hetong = self.db.query(Hetong).filter(
                Hetong.id == item.hetong_id,
                Hetong.is_deleted == "N"
            ).first()

            if hetong:
                item_dict['hetong_bianhao'] = hetong.hetong_bianhao
                item_dict['hetong_mingcheng'] = hetong.hetong_mingcheng

            # 查询关联的客户信息
            kehu = self.db.query(Kehu).filter(
                Kehu.id == item.kehu_id,
                Kehu.is_deleted == "N"
            ).first()

            if kehu:
                item_dict['kehu_mingcheng'] = kehu.gongsi_mingcheng

            # 查询关联的乙方主体信息（收款方）
            # 优先使用订单的乙方主体ID，如果没有则使用合同的乙方主体ID
            yifang_zhuti_id = item.yifang_zhuti_id
            if not yifang_zhuti_id and hetong:
                yifang_zhuti_id = hetong.yifang_zhuti_id

            if yifang_zhuti_id:
                yifang_zhuti = self.db.query(HetongYifangZhuti).filter(
                    HetongYifangZhuti.id == yifang_zhuti_id,
                    HetongYifangZhuti.is_deleted == "N"
                ).first()

                if yifang_zhuti:
                    item_dict['yifang_zhuti_mingcheng'] = yifang_zhuti.zhuti_mingcheng
                    item_dict['yifang_kaihuhang'] = yifang_zhuti.kaihuhang
                    item_dict['yifang_yinhangzhanghu'] = yifang_zhuti.yinhangzhanghu

            response_items.append(ZhifuDingdanResponse(**item_dict))

        return ZhifuDingdanListResponse(
            total=total,
            items=response_items,
            page=params.page,
            size=params.size
        )
    
    def get_zhifu_dingdan_statistics(self) -> ZhifuDingdanStatistics:
        """获取支付订单统计信息"""
        # 基础查询
        base_query = self.db.query(ZhifuDingdan).filter(ZhifuDingdan.is_deleted == "N")
        
        # 总订单数
        total_count = base_query.count()
        
        # 各状态订单数
        pending_count = base_query.filter(ZhifuDingdan.zhifu_zhuangtai == "pending").count()
        paid_count = base_query.filter(ZhifuDingdan.zhifu_zhuangtai == "paid").count()
        failed_count = base_query.filter(ZhifuDingdan.zhifu_zhuangtai == "failed").count()
        
        # 金额统计
        total_amount = base_query.with_entities(func.sum(ZhifuDingdan.dingdan_jine)).scalar() or Decimal('0')
        paid_amount = base_query.filter(ZhifuDingdan.zhifu_zhuangtai == "paid").with_entities(func.sum(ZhifuDingdan.shifu_jine)).scalar() or Decimal('0')
        pending_amount = base_query.filter(ZhifuDingdan.zhifu_zhuangtai == "pending").with_entities(func.sum(ZhifuDingdan.yingfu_jine)).scalar() or Decimal('0')
        
        return ZhifuDingdanStatistics(
            total_count=total_count,
            pending_count=pending_count,
            paid_count=paid_count,
            failed_count=failed_count,
            total_amount=total_amount,
            paid_amount=paid_amount,
            pending_amount=pending_amount
        )
    
    def _generate_dingdan_bianhao(self) -> str:
        """生成订单编号"""
        # 格式：ZF + YYYYMMDD + 4位随机数
        today = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().int)[:4]
        return f"ZF{today}{random_suffix}"

    def get_by_dingdan_hao(self, dingdan_hao: str) -> Optional[ZhifuDingdan]:
        """
        根据订单号获取支付订单

        Args:
            dingdan_hao: 订单号（dingdan_bianhao）

        Returns:
            支付订单对象或None
        """
        return self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.dingdan_bianhao == dingdan_hao,
            ZhifuDingdan.is_deleted == "N"
        ).first()

    def update_status(
        self,
        dingdan_id: str,
        zhuangtai: str,
        disanfang_dingdan_hao: Optional[str] = None
    ) -> ZhifuDingdan:
        """
        更新订单状态

        Args:
            dingdan_id: 订单ID
            zhuangtai: 新状态
            disanfang_dingdan_hao: 第三方订单号

        Returns:
            更新后的订单对象
        """
        dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()

        if not dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")

        dingdan.zhifu_zhuangtai = zhuangtai

        if disanfang_dingdan_hao:
            dingdan.disanfang_dingdan_hao = disanfang_dingdan_hao

        if zhuangtai == 'paid':
            dingdan.zhifu_shijian = datetime.now()
            dingdan.shifu_jine = dingdan.yingfu_jine

        self.db.commit()
        self.db.refresh(dingdan)

        # 发布订单状态更新事件
        publish(EventNames.PAYMENT_ORDER_STATUS_CHANGED, {
            "zhifu_dingdan_id": dingdan.id,
            "old_status": dingdan.zhifu_zhuangtai,
            "new_status": zhuangtai,
            "disanfang_dingdan_hao": disanfang_dingdan_hao
        })

        return dingdan
