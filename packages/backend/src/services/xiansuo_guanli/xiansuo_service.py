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
        """生成线索编码"""
        today = datetime.now().strftime("%Y%m%d")
        
        # 查询今天已有的线索数量
        count = self.db.query(Xiansuo).filter(
            Xiansuo.xiansuo_bianma.like(f"XS{today}%"),
            Xiansuo.is_deleted == "N"
        ).count()
        
        # 生成编码：XS + 日期 + 3位序号
        return f"XS{today}{(count + 1):03d}"
    
    def create_xiansuo(self, xiansuo_data: XiansuoCreate, created_by: str) -> XiansuoResponse:
        """创建线索"""
        # 验证来源是否存在
        laiyuan = self.db.query(XiansuoLaiyuan).filter(
            XiansuoLaiyuan.id == xiansuo_data.laiyuan_id,
            XiansuoLaiyuan.is_deleted == "N"
        ).first()
        
        if not laiyuan:
            raise HTTPException(status_code=404, detail="线索来源不存在")
        
        # 生成线索编码
        xiansuo_bianma = self._generate_xiansuo_bianma()
        
        # 创建线索
        xiansuo = Xiansuo(
            xiansuo_bianma=xiansuo_bianma,
            **xiansuo_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(xiansuo)
        
        # 更新来源的线索数量
        laiyuan.xiansuo_shuliang = (laiyuan.xiansuo_shuliang or 0) + 1
        
        self.db.commit()
        self.db.refresh(xiansuo)
        
        return XiansuoResponse.model_validate(xiansuo)
    
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
