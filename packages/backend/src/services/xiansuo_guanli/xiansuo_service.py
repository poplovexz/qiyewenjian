"""
线索管理服务
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from fastapi import HTTPException
from decimal import Decimal

from models.xiansuo_guanli import Xiansuo, XiansuoLaiyuan, XiansuoGenjin
from schemas.xiansuo_guanli import (
    XiansuoCreate,
    XiansuoUpdate,
    XiansuoResponse,
    XiansuoListResponse,
    XiansuoDetailResponse,
    XiansuoStatusUpdate,
    XiansuoAssignUpdate,
    XiansuoStatistics
)


class XiansuoService:
    """线索管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_xiansuo_bianma(self) -> str:
        """
        生成线索编码（带重试机制避免并发冲突）

        Returns:
            str: 线索编码，格式：XS + 日期 + 3位序号
        """
        import random
        import string
        from datetime import datetime

        max_retries = 10
        for attempt in range(max_retries):
            today = datetime.now().strftime("%Y%m%d")

            # 查询今天已有的线索数量
            count = self.db.query(Xiansuo).filter(
                Xiansuo.xiansuo_bianma.like(f"XS{today}%"),
                Xiansuo.is_deleted == "N"
            ).count()

            # 生成编码：XS + 日期 + 3位序号
            sequence = count + 1 + attempt  # 每次重试增加序号
            xiansuo_bianma = f"XS{today}{sequence:03d}"

            # 检查是否已存在（双重检查）
            existing = self.db.query(Xiansuo).filter(
                Xiansuo.xiansuo_bianma == xiansuo_bianma,
                Xiansuo.is_deleted == "N"
            ).first()

            if not existing:
                return xiansuo_bianma

        # 如果重试失败，使用时间戳+随机后缀
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join(random.choices(string.digits, k=3))
        return f"XS{timestamp}{random_suffix}"
    
    def create_xiansuo(self, xiansuo_data: XiansuoCreate, created_by: str) -> XiansuoResponse:
        """
        创建线索（带重试机制处理并发冲突）

        Args:
            xiansuo_data: 线索创建数据
            created_by: 创建人ID

        Returns:
            XiansuoResponse: 创建的线索信息
        """
        import logging
        from sqlalchemy.exc import IntegrityError

        logger = logging.getLogger(__name__)

        # 验证来源是否存在
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == xiansuo_data.laiyuan_id,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()

        if not laiyuan:
            raise HTTPException(status_code=404, detail="线索来源不存在")

        # 重试机制处理并发冲突
        max_retries = 3
        for retry in range(max_retries):
            try:
                # 生成线索编码
                xiansuo_bianma = self._generate_xiansuo_bianma()

                # 创建线索
                xiansuo = Xiansuo(
                    xiansuo_bianma=xiansuo_bianma,
                    **xiansuo_data.model_dump(),
                    created_by=created_by
                )

                # 自动创建关联的客户记录
                logger.info(f"开始为线索 {xiansuo_bianma} 创建关联客户...")
                try:
                    kehu_id = self._create_or_get_kehu_for_xiansuo(xiansuo_data, created_by)
                    logger.info(f"客户创建结果: kehu_id={kehu_id}")
                    if kehu_id:
                        xiansuo.kehu_id = kehu_id
                        logger.info(f"✅ 为线索 {xiansuo_bianma} 创建/关联客户: {kehu_id}")
                    else:
                        logger.warning("⚠️  客户创建返回None，线索将不关联客户")
                except Exception as e:
                    logger.error(f"❌ 为线索创建客户失败，将继续创建线索: {str(e)}", exc_info=True)
                    # 即使客户创建失败，也继续创建线索

                self.db.add(xiansuo)

                # 更新来源的线索数量
                laiyuan.xiansuo_shuliang = (laiyuan.xiansuo_shuliang or 0) + 1

                self.db.commit()
                self.db.refresh(xiansuo)

                logger.info(f"✅ 线索创建成功: {xiansuo_bianma}")
                return XiansuoResponse.model_validate(xiansuo)

            except IntegrityError as e:
                self.db.rollback()
                if "xiansuo_xiansuo_bianma_key" in str(e) and retry < max_retries - 1:
                    logger.warning(f"线索编号冲突，重试 {retry + 1}/{max_retries}")
                    continue
                else:
                    logger.error(f"创建线索失败: {str(e)}")
                    raise HTTPException(status_code=500, detail="创建线索失败: 编号生成冲突")
            except Exception as e:
                self.db.rollback()
                logger.error(f"创建线索失败: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"创建线索失败: {str(e)}")

        raise HTTPException(status_code=500, detail="创建线索失败: 超过最大重试次数")
    
    def get_xiansuo_by_id(self, xiansuo_id: str, current_user_id: Optional[str] = None, has_read_all_permission: bool = False) -> Optional[XiansuoResponse]:
        """根据ID获取线索"""
        query = self.db.query(Xiansuo).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        )

        # 数据隔离：如果没有全局查看权限，只能查看自己创建的线索
        if current_user_id and not has_read_all_permission:
            query = query.filter(Xiansuo.created_by == current_user_id)

        xiansuo = query.first()
        
        if not xiansuo:
            return None
        
        return XiansuoResponse.model_validate(xiansuo)
    
    def get_xiansuo_detail(self, xiansuo_id: str) -> Optional[XiansuoDetailResponse]:
        """获取线索详情（包含关联数据）"""
        xiansuo = self.db.query(Xiansuo).options(
            joinedload(Xiansuo.laiyuan),
            joinedload(Xiansuo.genjin_jilu_list)
        ).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        ).first()
        
        if not xiansuo:
            return None
        
        # 构建详情响应
        detail = XiansuoDetailResponse.model_validate(xiansuo)
        
        # 添加跟进记录（按时间倒序）
        genjin_list = self.db.query(XiansuoGenjin).filter(
            XiansuoGenjin.xiansuo_id == xiansuo_id,
            XiansuoGenjin.is_deleted == "N"
        ).order_by(XiansuoGenjin.genjin_shijian.desc()).all()
        
        detail.genjin_jilu_list = [
            {
                "id": genjin.id,
                "xiansuo_id": genjin.xiansuo_id,
                "genjin_fangshi": genjin.genjin_fangshi,
                "genjin_shijian": genjin.genjin_shijian,
                "genjin_neirong": genjin.genjin_neirong,
                "kehu_taidu": genjin.kehu_taidu,
                "genjin_jieguo": genjin.genjin_jieguo,
                "genjin_ren_xingming": genjin.genjin_ren_xingming,
                "xiaci_genjin_shijian": genjin.xiaci_genjin_shijian
            }
            for genjin in genjin_list
        ]
        
        return detail
    
    def get_xiansuo_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        xiansuo_zhuangtai: Optional[str] = None,
        laiyuan_id: Optional[str] = None,
        fenpei_ren_id: Optional[str] = None,
        zhiliang_pinggu: Optional[str] = None,
        hangye_leixing: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        current_user_id: Optional[str] = None,
        has_read_all_permission: bool = False
    ) -> XiansuoListResponse:
        """获取线索列表"""
        query = self.db.query(Xiansuo).filter(Xiansuo.is_deleted == "N")

        # 数据隔离：如果没有全局查看权限，只能查看自己创建的线索
        if current_user_id and not has_read_all_permission:
            query = query.filter(Xiansuo.created_by == current_user_id)
        
        # 搜索条件
        if search:
            search_filter = or_(
                Xiansuo.xiansuo_bianma.contains(search),
                Xiansuo.gongsi_mingcheng.contains(search),
                Xiansuo.lianxi_ren.contains(search),
                Xiansuo.lianxi_dianhua.contains(search),
                Xiansuo.lianxi_youxiang.contains(search)
            )
            query = query.filter(search_filter)
        
        # 状态筛选
        if xiansuo_zhuangtai:
            query = query.filter(Xiansuo.xiansuo_zhuangtai == xiansuo_zhuangtai)
        
        # 来源筛选
        if laiyuan_id:
            query = query.filter(Xiansuo.laiyuan_id == laiyuan_id)
        
        # 分配人筛选
        if fenpei_ren_id:
            query = query.filter(Xiansuo.fenpei_ren_id == fenpei_ren_id)
        
        # 质量评估筛选
        if zhiliang_pinggu:
            query = query.filter(Xiansuo.zhiliang_pinggu == zhiliang_pinggu)
        
        # 行业类型筛选
        if hangye_leixing:
            query = query.filter(Xiansuo.hangye_leixing == hangye_leixing)
        
        # 时间范围筛选
        if start_date:
            query = query.filter(Xiansuo.created_at >= start_date)
        if end_date:
            query = query.filter(Xiansuo.created_at <= end_date)
        
        # 排序
        query = query.order_by(Xiansuo.created_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = (page - 1) * size
        xiansuo_list = query.offset(skip).limit(size).all()
        
        return XiansuoListResponse(
            items=[XiansuoResponse.model_validate(xiansuo) for xiansuo in xiansuo_list],
            total=total,
            page=page,
            size=size
        )
    
    def update_xiansuo(self, xiansuo_id: str, xiansuo_data: XiansuoUpdate, updated_by: str, has_update_all_permission: bool = False) -> XiansuoResponse:
        """更新线索"""
        query = self.db.query(Xiansuo).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        )

        # 数据隔离：如果没有全局编辑权限，只能编辑自己创建的线索
        if not has_update_all_permission:
            query = query.filter(Xiansuo.created_by == updated_by)

        xiansuo = query.first()
        
        if not xiansuo:
            raise HTTPException(status_code=404, detail="线索不存在")
        
        # 如果更新来源，验证来源是否存在
        if xiansuo_data.laiyuan_id and xiansuo_data.laiyuan_id != xiansuo.laiyuan_id:
            laiyuan = self.db.query(XiansuoLaiyuan).filter(
                XiansuoLaiyuan.id == xiansuo_data.laiyuan_id,
                XiansuoLaiyuan.is_deleted == "N"
            ).first()
            
            if not laiyuan:
                raise HTTPException(status_code=404, detail="线索来源不存在")
        
        # 更新字段
        update_data = xiansuo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(xiansuo, field, value)
        
        xiansuo.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(xiansuo)
        
        return XiansuoResponse.model_validate(xiansuo)
    
    def update_xiansuo_status(self, xiansuo_id: str, status_data: XiansuoStatusUpdate, updated_by: str) -> XiansuoResponse:
        """更新线索状态"""
        xiansuo = self.db.query(Xiansuo).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        ).first()
        
        if not xiansuo:
            raise HTTPException(status_code=404, detail="线索不存在")
        
        old_status = xiansuo.xiansuo_zhuangtai
        xiansuo.xiansuo_zhuangtai = status_data.xiansuo_zhuangtai
        xiansuo.updated_by = updated_by
        
        # 如果状态变为成交，设置转化信息
        if status_data.xiansuo_zhuangtai == "won" and old_status != "won":
            xiansuo.shi_zhuanhua = "Y"
            xiansuo.zhuanhua_shijian = datetime.utcnow()
            
            # 更新来源的转化数量和转化率
            laiyuan = self.db.query(XiansuoLaiyuan).filter(
                XiansuoLaiyuan.id == xiansuo.laiyuan_id
            ).first()
            
            if laiyuan:
                laiyuan.zhuanhua_shuliang = (laiyuan.zhuanhua_shuliang or 0) + 1
                if laiyuan.xiansuo_shuliang > 0:
                    laiyuan.zhuanhua_lv = (laiyuan.zhuanhua_shuliang / laiyuan.xiansuo_shuliang) * 100
        
        self.db.commit()
        self.db.refresh(xiansuo)
        
        return XiansuoResponse.model_validate(xiansuo)

    def assign_xiansuo(self, xiansuo_id: str, assign_data: XiansuoAssignUpdate, updated_by: str) -> XiansuoResponse:
        """分配线索"""
        xiansuo = self.db.query(Xiansuo).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        ).first()

        if not xiansuo:
            raise HTTPException(status_code=404, detail="线索不存在")

        # 验证分配人是否存在
        from models.yonghu_guanli import Yonghu
        fenpei_ren = self.db.query(Yonghu).filter(
            Yonghu.id == assign_data.fenpei_ren_id,
            Yonghu.is_deleted == "N"
        ).first()

        if not fenpei_ren:
            raise HTTPException(status_code=404, detail="分配人不存在")

        xiansuo.fenpei_ren_id = assign_data.fenpei_ren_id
        xiansuo.fenpei_shijian = datetime.utcnow()
        xiansuo.updated_by = updated_by

        # 如果线索状态是新线索，自动更新为跟进中
        if xiansuo.xiansuo_zhuangtai == "new":
            xiansuo.xiansuo_zhuangtai = "following"

        self.db.commit()
        self.db.refresh(xiansuo)

        return XiansuoResponse.model_validate(xiansuo)

    def delete_xiansuo(self, xiansuo_id: str, deleted_by: str, has_delete_all_permission: bool = False) -> bool:
        """删除线索（软删除）"""
        query = self.db.query(Xiansuo).filter(
            Xiansuo.id == xiansuo_id,
            Xiansuo.is_deleted == "N"
        )

        # 数据隔离：如果没有全局删除权限，只能删除自己创建的线索
        if not has_delete_all_permission:
            query = query.filter(Xiansuo.created_by == deleted_by)

        xiansuo = query.first()

        if not xiansuo:
            raise HTTPException(status_code=404, detail="线索不存在")

        # 软删除
        xiansuo.is_deleted = "Y"
        xiansuo.updated_by = deleted_by

        # 更新来源的线索数量
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == xiansuo.laiyuan_id
        ).first()

        if laiyuan and laiyuan.xiansuo_shuliang > 0:
            laiyuan.xiansuo_shuliang -= 1
            # 重新计算转化率
            if laiyuan.xiansuo_shuliang > 0:
                laiyuan.zhuanhua_lv = (laiyuan.zhuanhua_shuliang / laiyuan.xiansuo_shuliang) * 100
            else:
                laiyuan.zhuanhua_lv = 0

        self.db.commit()

        return True

    def get_xiansuo_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        fenpei_ren_id: Optional[str] = None
    ) -> XiansuoStatistics:
        """获取线索统计数据"""
        query = self.db.query(Xiansuo).filter(Xiansuo.is_deleted == "N")

        # 时间范围筛选
        if start_date:
            query = query.filter(Xiansuo.created_at >= start_date)
        if end_date:
            query = query.filter(Xiansuo.created_at <= end_date)

        # 分配人筛选
        if fenpei_ren_id:
            query = query.filter(Xiansuo.fenpei_ren_id == fenpei_ren_id)

        # 统计各状态线索数量
        total_xiansuo = query.count()
        new_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "new").count()
        following_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "following").count()
        interested_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "interested").count()
        quoted_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "quoted").count()
        won_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "won").count()
        lost_xiansuo = query.filter(Xiansuo.xiansuo_zhuangtai == "lost").count()

        # 计算转化率
        zhuanhua_lv = Decimal(0)
        if total_xiansuo > 0:
            zhuanhua_lv = Decimal(won_xiansuo) / Decimal(total_xiansuo) * 100

        # 计算平均转化周期（成交线索的平均天数）
        pingjun_zhuanhua_zhouzqi = 0
        won_xiansuo_list = query.filter(
            Xiansuo.xiansuo_zhuangtai == "won",
            Xiansuo.zhuanhua_shijian.isnot(None)
        ).all()

        if won_xiansuo_list:
            total_days = sum([
                (xiansuo.zhuanhua_shijian - xiansuo.created_at).days
                for xiansuo in won_xiansuo_list
            ])
            pingjun_zhuanhua_zhouzqi = total_days // len(won_xiansuo_list)

        # 计算平均转化金额
        pingjun_zhuanhua_jine = Decimal(0)
        if won_xiansuo_list:
            total_jine = sum([xiansuo.zhuanhua_jine for xiansuo in won_xiansuo_list])
            pingjun_zhuanhua_jine = total_jine / len(won_xiansuo_list)

        return XiansuoStatistics(
            total_xiansuo=total_xiansuo,
            new_xiansuo=new_xiansuo,
            following_xiansuo=following_xiansuo,
            interested_xiansuo=interested_xiansuo,
            quoted_xiansuo=quoted_xiansuo,
            won_xiansuo=won_xiansuo,
            lost_xiansuo=lost_xiansuo,
            zhuanhua_lv=zhuanhua_lv,
            pingjun_zhuanhua_zhouzqi=pingjun_zhuanhua_zhouzqi,
            pingjun_zhuanhua_jine=pingjun_zhuanhua_jine
        )

    def _create_or_get_kehu_for_xiansuo(self, xiansuo_data: XiansuoCreate, created_by: str) -> Optional[str]:
        """
        为线索创建或获取关联的客户记录

        Args:
            xiansuo_data: 线索创建数据
            created_by: 创建人ID

        Returns:
            Optional[str]: 客户ID，如果创建失败则返回None
        """
        from models.kehu_guanli.kehu import Kehu
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 检查是否已存在同名客户
            existing_kehu = self.db.query(Kehu).filter(
                Kehu.gongsi_mingcheng == xiansuo_data.gongsi_mingcheng,
                Kehu.is_deleted == "N"
            ).first()

            if existing_kehu:
                logger.info(f"找到已存在的客户: {existing_kehu.gongsi_mingcheng} (ID: {existing_kehu.id})")
                return existing_kehu.id

            # 生成临时的统一社会信用代码（如果线索没有提供）
            # 使用特殊前缀标识这是临时生成的
            import uuid
            temp_credit_code = f"TEMP{uuid.uuid4().hex[:14].upper()}"

            # 从线索数据中提取客户信息
            kehu_data = {
                "gongsi_mingcheng": xiansuo_data.gongsi_mingcheng,
                "tongyi_shehui_xinyong_daima": temp_credit_code,
                "faren_xingming": xiansuo_data.lianxi_ren,  # 使用联系人作为法人姓名
                "lianxi_dianhua": xiansuo_data.lianxi_dianhua,
                "lianxi_youxiang": xiansuo_data.lianxi_youxiang,
                "lianxi_dizhi": xiansuo_data.zhuce_dizhi,
                "zhuce_dizhi": xiansuo_data.zhuce_dizhi,
                "kehu_zhuangtai": "active",
                "created_by": created_by
            }

            # 创建客户记录
            kehu = Kehu(**kehu_data)
            self.db.add(kehu)
            self.db.flush()  # 刷新以获取ID，但不提交

            logger.info(f"为线索自动创建客户: {kehu.gongsi_mingcheng} (ID: {kehu.id})")
            logger.warning(f"客户使用临时信用代码: {temp_credit_code}，请后续补充完整信息")

            return kehu.id

        except Exception as e:
            logger.error(f"为线索创建客户失败: {str(e)}", exc_info=True)
            # 不要回滚，让外层的commit处理
            return None
