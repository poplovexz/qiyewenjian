"""
线索报价管理服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from decimal import Decimal

from models.xiansuo_guanli import XiansuoBaojia, XiansuoBaojiaXiangmu, Xiansuo
from models.chanpin_guanli import ChanpinFenlei, ChanpinXiangmu
from schemas.xiansuo_guanli.xiansuo_baojia_schemas import (
    XiansuoBaojiaCreate,
    XiansuoBaojiaUpdate,
    XiansuoBaojiaResponse,
    XiansuoBaojiaListResponse,
    XiansuoBaojiaListItem,
    XiansuoBaojiaListParams,
    XiansuoBaojiaStatistics,
    ChanpinDataForBaojia,
    ChanpinFenleiOption,
    ChanpinXiangmuOption
)
from core.cache_decorator import invalidate_xiansuo_cache


class XiansuoBaojiaService:
    """线索报价管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _validate_daili_jizhang_limit(self, xiangmu_list: list) -> None:
        """
        验证代理记账服务数量限制

        Args:
            xiangmu_list: 报价项目列表

        Raises:
            HTTPException: 如果包含多个代理记账服务
        """
        # 获取所有项目ID
        xiangmu_ids = [item.chanpin_xiangmu_id for item in xiangmu_list]

        # 查询这些项目的分类信息
        xiangmu_with_fenlei = self.db.query(ChanpinXiangmu).options(
            joinedload(ChanpinXiangmu.fenlei)
        ).filter(
            and_(
                ChanpinXiangmu.id.in_(xiangmu_ids),
                ChanpinXiangmu.is_deleted == "N"
            )
        ).all()

        # 统计代理记账服务数量
        daili_jizhang_count = sum(
            1 for xiangmu in xiangmu_with_fenlei
            if xiangmu.fenlei and xiangmu.fenlei.chanpin_leixing == "daili_jizhang"
        )

        if daili_jizhang_count > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="代理记账服务只能选择一个，请检查报价项目"
            )

    @invalidate_xiansuo_cache()
    async def create_baojia(
        self,
        baojia_data: XiansuoBaojiaCreate,
        created_by: str
    ) -> XiansuoBaojiaResponse:
        """创建报价"""
        # 验证代理记账服务数量限制
        if baojia_data.xiangmu_list:
            self._validate_daili_jizhang_limit(baojia_data.xiangmu_list)

        # 检查线索是否存在
        xiansuo = self.db.query(Xiansuo).filter(
            and_(
                Xiansuo.id == baojia_data.xiansuo_id,
                Xiansuo.is_deleted == "N"
            )
        ).first()

        if not xiansuo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="线索不存在"
            )
        
        # 创建报价（带重试机制避免编码重复）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                baojia = XiansuoBaojia(
                    xiansuo_id=baojia_data.xiansuo_id,
                    baojia_bianma=XiansuoBaojia.generate_baojia_bianma(),
                    baojia_mingcheng=baojia_data.baojia_mingcheng,
                    youxiao_qi=baojia_data.youxiao_qi,
                    beizhu=baojia_data.beizhu,
                    created_by=created_by
                )

                self.db.add(baojia)
                self.db.flush()  # 获取ID
                break  # 成功则跳出循环

            except Exception as e:
                if "duplicate key" in str(e).lower() and attempt < max_retries - 1:
                    # 如果是重复键错误且还有重试机会，则重试
                    self.db.rollback()
                    continue
                else:
                    # 其他错误或重试次数用完，抛出异常
                    raise e
        
        # 创建报价项目
        total_amount = Decimal("0.00")
        for idx, xiangmu_data in enumerate(baojia_data.xiangmu_list):
            # 获取产品项目信息
            chanpin_xiangmu = self.db.query(ChanpinXiangmu).filter(
                and_(
                    ChanpinXiangmu.id == xiangmu_data.chanpin_xiangmu_id,
                    ChanpinXiangmu.is_deleted == "N",
                    ChanpinXiangmu.zhuangtai == "active"
                )
            ).first()
            
            if not chanpin_xiangmu:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"产品项目不存在: {xiangmu_data.chanpin_xiangmu_id}"
                )
            
            # 创建报价项目
            baojia_xiangmu = XiansuoBaojiaXiangmu(
                baojia_id=baojia.id,
                chanpin_xiangmu_id=xiangmu_data.chanpin_xiangmu_id,
                xiangmu_mingcheng=xiangmu_data.xiangmu_mingcheng if xiangmu_data.xiangmu_mingcheng is not None else chanpin_xiangmu.xiangmu_mingcheng,
                shuliang=xiangmu_data.shuliang,
                danjia=xiangmu_data.danjia if xiangmu_data.danjia is not None else chanpin_xiangmu.yewu_baojia,
                danwei=xiangmu_data.danwei if xiangmu_data.danwei is not None else chanpin_xiangmu.baojia_danwei,
                paixu=xiangmu_data.paixu if xiangmu_data.paixu is not None else idx,
                beizhu=xiangmu_data.beizhu,
                created_by=created_by
            )
            
            # 计算小计
            baojia_xiangmu.calculate_xiaoji()
            total_amount += baojia_xiangmu.xiaoji
            
            self.db.add(baojia_xiangmu)
        
        # 更新总金额
        baojia.zongji_jine = total_amount
        
        self.db.commit()
        self.db.refresh(baojia)
        
        return await self.get_baojia_detail(baojia.id)
    
    async def get_baojia_detail(self, baojia_id: str) -> XiansuoBaojiaResponse:
        """获取报价详情"""
        baojia = self.db.query(XiansuoBaojia).options(
            joinedload(XiansuoBaojia.xiangmu_list)
        ).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()
        
        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        return XiansuoBaojiaResponse.model_validate(baojia)

    async def get_baojia_detail_with_xiansuo(self, baojia_id: str) -> "XiansuoBaojiaDetailResponse":
        """获取包含线索信息的报价详情"""
        from schemas.xiansuo_guanli.xiansuo_baojia_schemas import XiansuoBaojiaDetailResponse, XiansuoInfoForBaojia

        baojia = self.db.query(XiansuoBaojia).options(
            joinedload(XiansuoBaojia.xiangmu_list)
        ).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()

        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )

        # 获取线索信息
        xiansuo = self.db.query(Xiansuo).filter(
            and_(
                Xiansuo.id == baojia.xiansuo_id,
                Xiansuo.is_deleted == "N"
            )
        ).first()

        if not xiansuo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的线索不存在"
            )

        # 构建响应数据
        baojia_dict = {
            "id": baojia.id,
            "xiansuo_id": baojia.xiansuo_id,
            "baojia_bianma": baojia.baojia_bianma,
            "baojia_mingcheng": baojia.baojia_mingcheng,
            "youxiao_qi": baojia.youxiao_qi,
            "zongji_jine": baojia.zongji_jine,
            "baojia_zhuangtai": baojia.baojia_zhuangtai,
            "is_expired": baojia.is_expired,
            "beizhu": baojia.beizhu,
            "xiangmu_list": baojia.xiangmu_list,
            "xiansuo_info": {
                "id": xiansuo.id,
                "gongsi_mingcheng": xiansuo.gongsi_mingcheng,
                "lianxi_ren": xiansuo.lianxi_ren,
                "lianxi_dianhua": xiansuo.lianxi_dianhua,
                "lianxi_youxiang": xiansuo.lianxi_youxiang,
                "kehu_id": xiansuo.kehu_id
            },
            "created_at": baojia.created_at,
            "updated_at": baojia.updated_at,
            "created_by": baojia.created_by
        }

        return XiansuoBaojiaDetailResponse.model_validate(baojia_dict)
    
    @invalidate_xiansuo_cache()
    async def update_baojia(
        self,
        baojia_id: str,
        baojia_data: XiansuoBaojiaUpdate,
        updated_by: str
    ) -> XiansuoBaojiaResponse:
        """更新报价"""
        # 验证代理记账服务数量限制
        if baojia_data.xiangmu_list:
            self._validate_daili_jizhang_limit(baojia_data.xiangmu_list)

        baojia = self.db.query(XiansuoBaojia).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()

        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )

        # 检查是否可以编辑
        if baojia.baojia_zhuangtai in ['accepted', 'rejected']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已接受或已拒绝的报价不能编辑"
            )
        
        # 更新基本信息（排除状态字段，状态只能通过专用接口修改）
        update_data = baojia_data.model_dump(exclude_unset=True, exclude={'xiangmu_list', 'baojia_zhuangtai'})
        for field, value in update_data.items():
            setattr(baojia, field, value)
        
        baojia.updated_by = updated_by
        baojia.updated_at = datetime.now()
        
        # 更新项目列表
        if baojia_data.xiangmu_list is not None:
            # 删除原有项目
            self.db.query(XiansuoBaojiaXiangmu).filter(
                XiansuoBaojiaXiangmu.baojia_id == baojia_id
            ).delete()
            
            # 创建新项目（更新时保持历史价格，避免被产品调价影响）
            total_amount = Decimal("0.00")
            for idx, xiangmu_data in enumerate(baojia_data.xiangmu_list):
                # 获取产品信息（仅用于验证存在性和获取默认值）
                chanpin_xiangmu = self.db.query(ChanpinXiangmu).filter(
                    and_(
                        ChanpinXiangmu.id == xiangmu_data.chanpin_xiangmu_id,
                        ChanpinXiangmu.is_deleted == "N",
                        ChanpinXiangmu.zhuangtai == "active"
                    )
                ).first()

                if not chanpin_xiangmu:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"产品项目不存在: {xiangmu_data.chanpin_xiangmu_id}"
                    )

                # 更新时：只有明确传入价格时才使用新价格，否则保持历史价格不变
                # 这样避免产品调价后影响历史报价
                baojia_xiangmu = XiansuoBaojiaXiangmu(
                    baojia_id=baojia.id,
                    chanpin_xiangmu_id=xiangmu_data.chanpin_xiangmu_id,
                    xiangmu_mingcheng=xiangmu_data.xiangmu_mingcheng if xiangmu_data.xiangmu_mingcheng is not None else chanpin_xiangmu.xiangmu_mingcheng,
                    shuliang=xiangmu_data.shuliang,
                    # 价格处理：如果传入了价格使用传入的，否则使用产品默认价格
                    danjia=xiangmu_data.danjia if xiangmu_data.danjia is not None else chanpin_xiangmu.yewu_baojia,
                    danwei=xiangmu_data.danwei if xiangmu_data.danwei is not None else chanpin_xiangmu.baojia_danwei,
                    paixu=xiangmu_data.paixu if xiangmu_data.paixu is not None else idx,
                    beizhu=xiangmu_data.beizhu,
                    created_by=updated_by
                )
                
                baojia_xiangmu.calculate_xiaoji()
                total_amount += baojia_xiangmu.xiaoji
                
                self.db.add(baojia_xiangmu)
            
            # 更新总金额
            baojia.zongji_jine = total_amount
        
        self.db.commit()
        self.db.refresh(baojia)
        
        return await self.get_baojia_detail(baojia.id)
    
    @invalidate_xiansuo_cache()
    async def delete_baojia(self, baojia_id: str, deleted_by: str) -> bool:
        """删除报价"""
        baojia = self.db.query(XiansuoBaojia).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()
        
        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        # 检查是否可以删除
        if baojia.baojia_zhuangtai == 'accepted':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已接受的报价不能删除"
            )
        
        # 软删除
        baojia.is_deleted = "Y"
        baojia.deleted_by = deleted_by
        baojia.deleted_at = datetime.now()
        
        self.db.commit()
        return True
    
    async def get_baojia_list(
        self, 
        params: XiansuoBaojiaListParams
    ) -> XiansuoBaojiaListResponse:
        """获取报价列表"""
        query = self.db.query(XiansuoBaojia).filter(
            XiansuoBaojia.is_deleted == "N"
        )
        
        # 筛选条件
        if params.xiansuo_id:
            query = query.filter(XiansuoBaojia.xiansuo_id == params.xiansuo_id)
        
        if params.baojia_zhuangtai:
            query = query.filter(XiansuoBaojia.baojia_zhuangtai == params.baojia_zhuangtai)
        
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    XiansuoBaojia.baojia_bianma.ilike(search_pattern),
                    XiansuoBaojia.baojia_mingcheng.ilike(search_pattern)
                )
            )
        
        # 总数
        total = query.count()
        
        # 分页
        items = query.order_by(desc(XiansuoBaojia.created_at)).offset(
            (params.page - 1) * params.size
        ).limit(params.size).all()
        
        # 转换为响应模型
        baojia_items = []
        for baojia in items:
            xiangmu_count = self.db.query(XiansuoBaojiaXiangmu).filter(
                XiansuoBaojiaXiangmu.baojia_id == baojia.id
            ).count()
            
            baojia_items.append(XiansuoBaojiaListItem(
                id=baojia.id,
                baojia_bianma=baojia.baojia_bianma,
                baojia_mingcheng=baojia.baojia_mingcheng,
                zongji_jine=baojia.zongji_jine,
                baojia_zhuangtai=baojia.baojia_zhuangtai,
                youxiao_qi=baojia.youxiao_qi,
                is_expired=baojia.is_expired,
                xiangmu_count=xiangmu_count,
                created_at=baojia.created_at,
                created_by=baojia.created_by
            ))
        
        return XiansuoBaojiaListResponse(
            items=baojia_items,
            total=total,
            page=params.page,
            size=params.size,
            pages=(total + params.size - 1) // params.size
        )

    async def get_baojia_by_xiansuo(self, xiansuo_id: str) -> List[XiansuoBaojiaResponse]:
        """获取指定线索的报价列表"""
        baojia_list = self.db.query(XiansuoBaojia).options(
            joinedload(XiansuoBaojia.xiangmu_list)
        ).filter(
            and_(
                XiansuoBaojia.xiansuo_id == xiansuo_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).order_by(desc(XiansuoBaojia.created_at)).all()

        return [XiansuoBaojiaResponse.model_validate(baojia) for baojia in baojia_list]

    async def get_baojia_statistics(self) -> XiansuoBaojiaStatistics:
        """获取报价统计"""
        # 基础统计
        total_count = self.db.query(XiansuoBaojia).filter(
            XiansuoBaojia.is_deleted == "N"
        ).count()

        # 按状态统计
        status_stats = self.db.query(
            XiansuoBaojia.baojia_zhuangtai,
            func.count(XiansuoBaojia.id).label('count'),
            func.sum(XiansuoBaojia.zongji_jine).label('amount')
        ).filter(
            XiansuoBaojia.is_deleted == "N"
        ).group_by(XiansuoBaojia.baojia_zhuangtai).all()

        # 初始化统计数据
        stats = {
            'draft_count': 0,
            'sent_count': 0,
            'accepted_count': 0,
            'rejected_count': 0,
            'expired_count': 0,
            'total_amount': Decimal("0.00"),
            'accepted_amount': Decimal("0.00")
        }

        # 填充统计数据
        # FLK-F402: 使用 baojia_status 避免覆盖导入的 status
        for baojia_status, count, amount in status_stats:
            stats[f'{baojia_status}_count'] = count
            stats['total_amount'] += amount or Decimal("0.00")
            if baojia_status == 'accepted':
                stats['accepted_amount'] = amount or Decimal("0.00")

        return XiansuoBaojiaStatistics(
            total_count=total_count,
            **stats
        )

    async def get_chanpin_data_for_baojia(self) -> ChanpinDataForBaojia:
        """获取报价用产品数据"""
        # 获取产品分类
        fenlei_list = self.db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.is_deleted == "N",
                ChanpinFenlei.zhuangtai == "active"
            )
        ).order_by(ChanpinFenlei.paixu, ChanpinFenlei.fenlei_mingcheng).all()

        # 获取产品项目
        xiangmu_list = self.db.query(ChanpinXiangmu).options(
            joinedload(ChanpinXiangmu.fenlei)
        ).filter(
            and_(
                ChanpinXiangmu.is_deleted == "N",
                ChanpinXiangmu.zhuangtai == "active"
            )
        ).order_by(ChanpinXiangmu.paixu, ChanpinXiangmu.xiangmu_mingcheng).all()

        # 分类数据
        zengzhi_fenlei = []
        daili_jizhang_fenlei = []

        for fenlei in fenlei_list:
            fenlei_option = ChanpinFenleiOption.model_validate(fenlei)
            if fenlei.chanpin_leixing == "zengzhi":
                zengzhi_fenlei.append(fenlei_option)
            elif fenlei.chanpin_leixing == "daili_jizhang":
                daili_jizhang_fenlei.append(fenlei_option)

        # 项目数据
        zengzhi_xiangmu = []
        daili_jizhang_xiangmu = []

        import logging
        logger = logging.getLogger(__name__)

        logger.error(f"=== 处理产品项目 ===")
        logger.error(f"总项目数: {len(xiangmu_list)}")

        for xiangmu in xiangmu_list:
            logger.error(f"\n处理项目: {xiangmu.xiangmu_mingcheng}")
            logger.error(f"  分类: {xiangmu.fenlei.fenlei_mingcheng if xiangmu.fenlei else 'None'}")
            logger.error(f"  分类类型: {xiangmu.fenlei.chanpin_leixing if xiangmu.fenlei else 'None'}")

            try:
                xiangmu_option = ChanpinXiangmuOption.model_validate(xiangmu)
                logger.error(f"  ✅ 序列化成功")

                if xiangmu.fenlei.chanpin_leixing == "zengzhi":
                    zengzhi_xiangmu.append(xiangmu_option)
                    logger.error(f"  ➡️ 添加到增值服务")
                elif xiangmu.fenlei.chanpin_leixing == "daili_jizhang":
                    daili_jizhang_xiangmu.append(xiangmu_option)
                    logger.error(f"  ➡️ 添加到代理记账")
            except Exception as e:
                logger.error(f"  ❌ 序列化失败: {e}")

        logger.error(f"\n=== 最终统计 ===")
        logger.error(f"增值服务项目数: {len(zengzhi_xiangmu)}")
        logger.error(f"代理记账项目数: {len(daili_jizhang_xiangmu)}")

        return ChanpinDataForBaojia(
            zengzhi_fenlei=zengzhi_fenlei,
            daili_jizhang_fenlei=daili_jizhang_fenlei,
            zengzhi_xiangmu=zengzhi_xiangmu,
            daili_jizhang_xiangmu=daili_jizhang_xiangmu
        )

    @invalidate_xiansuo_cache()
    async def update_baojia_status(
        self,
        baojia_id: str,
        new_status: str,
        updated_by: str
    ) -> XiansuoBaojiaResponse:
        """更新报价状态（包含业务链路联动）"""
        baojia = self.db.query(XiansuoBaojia).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()

        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )

        # 验证状态转换
        valid_statuses = ['draft', 'sent', 'accepted', 'rejected', 'expired']
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的报价状态: {new_status}"
            )

        old_status = baojia.baojia_zhuangtai

        # 更新报价状态
        baojia.baojia_zhuangtai = new_status
        baojia.updated_by = updated_by
        baojia.updated_at = datetime.now()

        # 业务链路联动处理
        if new_status == 'accepted' and old_status != 'accepted':
            # 报价被接受时的联动逻辑
            await self._handle_baojia_accepted(baojia, updated_by)
        elif new_status == 'rejected' and old_status != 'rejected':
            # 报价被拒绝时的联动逻辑
            await self._handle_baojia_rejected(baojia, updated_by)

        self.db.commit()
        self.db.refresh(baojia)

        return await self.get_baojia_detail(baojia.id)

    async def _handle_baojia_accepted(self, baojia: XiansuoBaojia, updated_by: str):
        """处理报价被接受的业务联动"""
        from .xiansuo_service import XiansuoService
        from schemas.xiansuo_guanli import XiansuoStatusUpdate

        xiansuo_service = XiansuoService(self.db)

        # 1. 更新线索状态为"已报价"或"成交"
        try:
            status_update = XiansuoStatusUpdate(xiansuo_zhuangtai="quoted")
            xiansuo_service.update_xiansuo_status(
                baojia.xiansuo_id,
                status_update,
                updated_by
            )
        except Exception as e:
            # 记录日志但不阻断流程
            print(f"更新线索状态失败: {e}")

        # 2. 记录转化金额到线索
        try:
            xiansuo = self.db.query(Xiansuo).filter(
                Xiansuo.id == baojia.xiansuo_id
            ).first()
            if xiansuo:
                xiansuo.zhuanhua_jine = baojia.zongji_jine
                xiansuo.updated_by = updated_by
                xiansuo.updated_at = datetime.now()
        except Exception as e:
            print(f"更新线索转化金额失败: {e}")

        # 3. TODO: 可以在这里添加创建客户记录的逻辑
        # 4. TODO: 可以在这里添加创建合同草稿的逻辑

    async def _handle_baojia_rejected(self, baojia: XiansuoBaojia, updated_by: str):
        """处理报价被拒绝的业务联动"""
        # 1. 可以记录拒绝原因
        # 2. 可以更新线索状态
        # 3. 可以触发后续跟进流程
        pass

    async def check_expired_baojia(self) -> int:
        """检查并更新过期报价"""
        expired_baojia_list = self.db.query(XiansuoBaojia).filter(
            and_(
                XiansuoBaojia.is_deleted == "N",
                XiansuoBaojia.baojia_zhuangtai.in_(['draft', 'sent']),
                XiansuoBaojia.youxiao_qi < datetime.now()
            )
        ).all()

        count = 0
        for baojia in expired_baojia_list:
            baojia.baojia_zhuangtai = 'expired'
            baojia.updated_at = datetime.now()
            count += 1

        if count > 0:
            self.db.commit()

        return count

    @invalidate_xiansuo_cache()
    async def confirm_baojia(self, baojia_id: str, queren_ren_id: str) -> XiansuoBaojiaResponse:
        """确认报价"""
        # 获取报价信息
        baojia = self.db.query(XiansuoBaojia).options(
            joinedload(XiansuoBaojia.xiangmu_list),
            joinedload(XiansuoBaojia.xiansuo)
        ).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()

        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )

        # 检查报价状态是否可以确认
        if baojia.baojia_zhuangtai not in ['draft', 'sent']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"报价状态为 {baojia.baojia_zhuangtai}，无法确认"
            )

        # 检查报价是否过期
        if baojia.is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报价已过期，无法确认"
            )

        # 更新报价状态和确认信息
        baojia.baojia_zhuangtai = 'accepted'
        baojia.queren_ren_id = queren_ren_id
        baojia.queren_shijian = datetime.now()
        baojia.updated_at = datetime.now()

        try:
            self.db.commit()

            # 发布报价确认事件
            from core.events import publish, EventNames
            publish(EventNames.BAOJIA_CONFIRMED, {
                "baojia_id": baojia_id,
                "xiansuo_id": baojia.xiansuo_id,
                "queren_ren_id": queren_ren_id,
                "baojia_bianma": baojia.baojia_bianma,
                "zongji_jine": float(baojia.zongji_jine)
            })

            # 返回更新后的报价详情
            return await self.get_baojia_detail(baojia_id)

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"确认报价失败: {str(e)}"
            )

    @invalidate_xiansuo_cache()
    async def reject_baojia(self, baojia_id: str, queren_ren_id: str, reject_reason: str = None) -> XiansuoBaojiaResponse:
        """拒绝报价"""
        # 获取报价信息
        baojia = self.db.query(XiansuoBaojia).options(
            joinedload(XiansuoBaojia.xiangmu_list),
            joinedload(XiansuoBaojia.xiansuo)
        ).filter(
            and_(
                XiansuoBaojia.id == baojia_id,
                XiansuoBaojia.is_deleted == "N"
            )
        ).first()

        if not baojia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )

        # 检查报价状态是否可以拒绝
        if baojia.baojia_zhuangtai not in ['draft', 'sent']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"报价状态为 {baojia.baojia_zhuangtai}，无法拒绝"
            )

        # 更新报价状态和确认信息
        baojia.baojia_zhuangtai = 'rejected'
        baojia.queren_ren_id = queren_ren_id
        baojia.queren_shijian = datetime.now()
        baojia.updated_at = datetime.now()

        # 如果有拒绝原因，可以记录在备注中
        if reject_reason:
            original_beizhu = baojia.beizhu or ""
            baojia.beizhu = f"{original_beizhu}\n[拒绝原因] {reject_reason}".strip()

        try:
            self.db.commit()

            # 发布报价拒绝事件
            from core.events import publish, EventNames
            publish(EventNames.BAOJIA_REJECTED, {
                "baojia_id": baojia_id,
                "xiansuo_id": baojia.xiansuo_id,
                "queren_ren_id": queren_ren_id,
                "baojia_bianma": baojia.baojia_bianma,
                "reject_reason": reject_reason or "未提供拒绝原因"
            })

            # 返回更新后的报价详情
            return await self.get_baojia_detail(baojia_id)

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"拒绝报价失败: {str(e)}"
            )
