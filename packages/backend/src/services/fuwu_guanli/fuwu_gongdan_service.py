"""
服务工单管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import json

from models.fuwu_guanli import FuwuGongdan, FuwuGongdanXiangmu, FuwuGongdanRizhi
from models.hetong_guanli import Hetong
from models.kehu_guanli import Kehu
from models.yonghu_guanli import Yonghu
from schemas.fuwu_guanli.fuwu_gongdan_schemas import (
    FuwuGongdanCreate,
    FuwuGongdanUpdate,
    FuwuGongdanResponse,
    FuwuGongdanDetailResponse,
    FuwuGongdanListResponse,
    FuwuGongdanListParams,
    FuwuGongdanStatistics,
    FuwuGongdanXiangmuCreate,
    FuwuGongdanXiangmuUpdate,
    FuwuGongdanXiangmuResponse,
    FuwuGongdanRizhiCreate,
    FuwuGongdanRizhiResponse
)


class FuwuGongdanService:
    """服务工单管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_gongdan(self, gongdan_data: FuwuGongdanCreate, created_by: str) -> FuwuGongdanDetailResponse:
        """创建服务工单"""
        # 验证合同是否存在
        hetong = self.db.query(Hetong).filter(
            Hetong.id == gongdan_data.hetong_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        # 验证客户是否存在
        kehu = self.db.query(Kehu).filter(
            Kehu.id == gongdan_data.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 验证执行人是否存在（如果指定）
        if gongdan_data.zhixing_ren_id:
            zhixing_ren = self.db.query(Yonghu).filter(
                Yonghu.id == gongdan_data.zhixing_ren_id,
                Yonghu.is_deleted == "N"
            ).first()
            
            if not zhixing_ren:
                raise HTTPException(status_code=404, detail="执行人不存在")
        
        # 生成工单编号
        gongdan_bianhao = FuwuGongdan.generate_gongdan_bianhao()
        
        # 创建工单
        gongdan = FuwuGongdan(
            gongdan_bianhao=gongdan_bianhao,
            **gongdan_data.model_dump(exclude={"xiangmu_list"}),
            created_by=created_by
        )
        
        self.db.add(gongdan)
        self.db.flush()  # 获取工单ID
        
        # 创建工单项目
        if gongdan_data.xiangmu_list:
            for idx, xiangmu_data in enumerate(gongdan_data.xiangmu_list):
                xiangmu_dict = xiangmu_data.model_dump()
                xiangmu_dict['paixu'] = idx + 1  # 覆盖排序值
                xiangmu = FuwuGongdanXiangmu(
                    gongdan_id=gongdan.id,
                    **xiangmu_dict,
                    created_by=created_by
                )
                self.db.add(xiangmu)
        
        # 创建工单日志
        rizhi = FuwuGongdanRizhi(
            gongdan_id=gongdan.id,
            caozuo_leixing="created",
            caozuo_neirong=f"创建工单：{gongdan.gongdan_biaoti}",
            caozuo_ren_id=created_by,
            created_by=created_by
        )
        self.db.add(rizhi)
        
        self.db.commit()
        self.db.refresh(gongdan)
        
        return self.get_gongdan_detail(gongdan.id)
    
    def get_gongdan_detail(self, gongdan_id: str) -> FuwuGongdanDetailResponse:
        """获取工单详情"""
        gongdan = self.db.query(FuwuGongdan).options(
            joinedload(FuwuGongdan.xiangmu_list),
            joinedload(FuwuGongdan.rizhi_list)
        ).filter(
            FuwuGongdan.id == gongdan_id,
            FuwuGongdan.is_deleted == "N"
        ).first()
        
        if not gongdan:
            raise HTTPException(status_code=404, detail="工单不存在")
        
        # 构建响应数据
        response_data = {
            **gongdan.__dict__,
            "is_overdue": gongdan.is_overdue,
            "progress_percentage": gongdan.progress_percentage,
            "xiangmu_list": [
                FuwuGongdanXiangmuResponse.model_validate(xiangmu)
                for xiangmu in gongdan.xiangmu_list
            ],
            "rizhi_list": [
                FuwuGongdanRizhiResponse.model_validate(rizhi)
                for rizhi in gongdan.rizhi_list
            ]
        }
        
        return FuwuGongdanDetailResponse.model_validate(response_data)
    
    def update_gongdan(self, gongdan_id: str, gongdan_data: FuwuGongdanUpdate, updated_by: str) -> FuwuGongdanDetailResponse:
        """更新工单"""
        gongdan = self.db.query(FuwuGongdan).filter(
            FuwuGongdan.id == gongdan_id,
            FuwuGongdan.is_deleted == "N"
        ).first()
        
        if not gongdan:
            raise HTTPException(status_code=404, detail="工单不存在")
        
        # 记录状态变更
        old_status = gongdan.gongdan_zhuangtai
        update_data = gongdan_data.model_dump(exclude_unset=True)
        
        # 更新工单
        for field, value in update_data.items():
            setattr(gongdan, field, value)
        
        gongdan.updated_at = datetime.now()
        
        # 如果状态发生变更，记录日志
        if "gongdan_zhuangtai" in update_data and update_data["gongdan_zhuangtai"] != old_status:
            self._add_status_change_log(gongdan.id, old_status, update_data["gongdan_zhuangtai"], updated_by)
        
        # 如果分配了执行人，记录分配日志
        if "zhixing_ren_id" in update_data and update_data["zhixing_ren_id"]:
            gongdan.fenpei_shijian = datetime.now()
            gongdan.fenpei_ren_id = updated_by
            self._add_assignment_log(gongdan.id, update_data["zhixing_ren_id"], updated_by)
        
        self.db.commit()
        self.db.refresh(gongdan)
        
        return self.get_gongdan_detail(gongdan.id)
    
    def get_gongdan_list(self, params: FuwuGongdanListParams) -> FuwuGongdanListResponse:
        """获取工单列表"""
        query = self.db.query(FuwuGongdan).filter(FuwuGongdan.is_deleted == "N")
        
        # 应用过滤条件
        if params.gongdan_bianhao:
            query = query.filter(FuwuGongdan.gongdan_bianhao.ilike(f"%{params.gongdan_bianhao}%"))
        
        if params.gongdan_biaoti:
            query = query.filter(FuwuGongdan.gongdan_biaoti.ilike(f"%{params.gongdan_biaoti}%"))
        
        if params.fuwu_leixing:
            query = query.filter(FuwuGongdan.fuwu_leixing == params.fuwu_leixing)
        
        if params.gongdan_zhuangtai:
            query = query.filter(FuwuGongdan.gongdan_zhuangtai == params.gongdan_zhuangtai)
        
        if params.youxian_ji:
            query = query.filter(FuwuGongdan.youxian_ji == params.youxian_ji)
        
        if params.zhixing_ren_id:
            query = query.filter(FuwuGongdan.zhixing_ren_id == params.zhixing_ren_id)
        
        if params.kehu_id:
            query = query.filter(FuwuGongdan.kehu_id == params.kehu_id)
        
        if params.hetong_id:
            query = query.filter(FuwuGongdan.hetong_id == params.hetong_id)
        
        if params.is_overdue is not None:
            if params.is_overdue:
                query = query.filter(
                    FuwuGongdan.jihua_jieshu_shijian < datetime.now(),
                    FuwuGongdan.gongdan_zhuangtai.notin_(["completed", "cancelled"])
                )
            else:
                query = query.filter(
                    or_(
                        FuwuGongdan.jihua_jieshu_shijian >= datetime.now(),
                        FuwuGongdan.gongdan_zhuangtai.in_(["completed", "cancelled"])
                    )
                )
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        gongdan_list = query.order_by(desc(FuwuGongdan.created_at)).offset(offset).limit(params.size).all()
        
        # 构建响应数据
        items = []
        for gongdan in gongdan_list:
            item_data = {
                **gongdan.__dict__,
                "is_overdue": gongdan.is_overdue,
                "progress_percentage": gongdan.progress_percentage
            }
            items.append(FuwuGongdanResponse.model_validate(item_data))
        
        pages = (total + params.size - 1) // params.size
        
        return FuwuGongdanListResponse(
            total=total,
            items=items,
            page=params.page,
            size=params.size,
            pages=pages
        )
    
    def _add_status_change_log(self, gongdan_id: str, old_status: str, new_status: str, operator_id: str):
        """添加状态变更日志"""
        status_map = {
            "created": "已创建",
            "assigned": "已分配", 
            "in_progress": "进行中",
            "pending_review": "待审核",
            "completed": "已完成",
            "cancelled": "已取消"
        }
        
        rizhi = FuwuGongdanRizhi(
            gongdan_id=gongdan_id,
            caozuo_leixing="status_changed",
            caozuo_neirong=f"状态变更：{status_map.get(old_status, old_status)} → {status_map.get(new_status, new_status)}",
            caozuo_ren_id=operator_id,
            created_by=operator_id
        )
        self.db.add(rizhi)
    
    def _add_assignment_log(self, gongdan_id: str, zhixing_ren_id: str, operator_id: str):
        """添加分配日志"""
        # 获取执行人信息
        zhixing_ren = self.db.query(Yonghu).filter(Yonghu.id == zhixing_ren_id).first()
        zhixing_ren_name = zhixing_ren.xingming if zhixing_ren else "未知用户"
        
        rizhi = FuwuGongdanRizhi(
            gongdan_id=gongdan_id,
            caozuo_leixing="assigned",
            caozuo_neirong=f"工单已分配给：{zhixing_ren_name}",
            caozuo_ren_id=operator_id,
            created_by=operator_id
        )
        self.db.add(rizhi)

    def create_gongdan_from_hetong(self, hetong_id: str, created_by: str) -> FuwuGongdanDetailResponse:
        """基于合同创建服务工单"""
        # 获取合同信息
        hetong = self.db.query(Hetong).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")

        if hetong.hetong_zhuangtai != "signed":
            raise HTTPException(status_code=400, detail="只能为已签署的合同创建服务工单")

        # 检查是否已经创建过工单
        existing_gongdan = self.db.query(FuwuGongdan).filter(
            FuwuGongdan.hetong_id == hetong_id,
            FuwuGongdan.is_deleted == "N"
        ).first()

        if existing_gongdan:
            raise HTTPException(status_code=400, detail="该合同已经创建过服务工单")

        # 根据合同类型确定服务类型和默认项目
        fuwu_leixing = "daili_jizhang"  # 默认代理记账
        default_xiangmu_list = self._get_default_xiangmu_by_service_type(fuwu_leixing)

        # 计算计划结束时间（默认30天后）
        jihua_jieshu_shijian = datetime.now() + timedelta(days=30)

        # 创建工单数据
        gongdan_data = FuwuGongdanCreate(
            hetong_id=hetong_id,
            kehu_id=hetong.kehu_id,
            gongdan_biaoti=f"{hetong.hetong_mingcheng} - 服务工单",
            gongdan_miaoshu=f"基于合同 {hetong.hetong_bianhao} 自动创建的服务工单",
            fuwu_leixing=fuwu_leixing,
            youxian_ji="medium",
            jihua_jieshu_shijian=jihua_jieshu_shijian,
            xiangmu_list=default_xiangmu_list
        )

        return self.create_gongdan(gongdan_data, created_by)

    def _get_default_xiangmu_by_service_type(self, fuwu_leixing: str) -> List[FuwuGongdanXiangmuCreate]:
        """根据服务类型获取默认项目列表"""
        if fuwu_leixing == "daili_jizhang":
            return [
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="建账设置",
                    xiangmu_miaoshu="设置会计科目、期初余额等",
                    paixu=1,
                    jihua_gongshi=2.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="凭证录入",
                    xiangmu_miaoshu="录入当月业务凭证",
                    paixu=2,
                    jihua_gongshi=8.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="账务处理",
                    xiangmu_miaoshu="结转损益、计提折旧等",
                    paixu=3,
                    jihua_gongshi=4.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="报表编制",
                    xiangmu_miaoshu="编制资产负债表、利润表等",
                    paixu=4,
                    jihua_gongshi=3.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="纳税申报",
                    xiangmu_miaoshu="增值税、企业所得税等申报",
                    paixu=5,
                    jihua_gongshi=2.0
                )
            ]
        elif fuwu_leixing == "shuiwu_shenbao":
            return [
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="税务资料收集",
                    xiangmu_miaoshu="收集申报所需的各类税务资料",
                    paixu=1,
                    jihua_gongshi=1.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="申报表填写",
                    xiangmu_miaoshu="填写各类税务申报表",
                    paixu=2,
                    jihua_gongshi=2.0
                ),
                FuwuGongdanXiangmuCreate(
                    xiangmu_mingcheng="网上申报",
                    xiangmu_miaoshu="通过税务系统进行网上申报",
                    paixu=3,
                    jihua_gongshi=1.0
                )
            ]
        else:
            return []

    def assign_gongdan(self, gongdan_id: str, zhixing_ren_id: str, fenpei_beizhu: Optional[str], assigned_by: str) -> FuwuGongdanDetailResponse:
        """分配工单"""
        gongdan_update = FuwuGongdanUpdate(
            zhixing_ren_id=zhixing_ren_id,
            gongdan_zhuangtai="assigned",
            fenpei_beizhu=fenpei_beizhu
        )

        return self.update_gongdan(gongdan_id, gongdan_update, assigned_by)

    def start_gongdan(self, gongdan_id: str, started_by: str) -> FuwuGongdanDetailResponse:
        """开始工单"""
        gongdan_update = FuwuGongdanUpdate(
            gongdan_zhuangtai="in_progress",
            shiji_kaishi_shijian=datetime.now()
        )

        return self.update_gongdan(gongdan_id, gongdan_update, started_by)

    def complete_gongdan(self, gongdan_id: str, wancheng_qingkuang: str, jiaofei_wenjian: Optional[str], completed_by: str) -> FuwuGongdanDetailResponse:
        """完成工单"""
        gongdan_update = FuwuGongdanUpdate(
            gongdan_zhuangtai="completed",
            shiji_jieshu_shijian=datetime.now(),
            wancheng_qingkuang=wancheng_qingkuang,
            jiaofei_wenjian=jiaofei_wenjian
        )

        return self.update_gongdan(gongdan_id, gongdan_update, completed_by)

    def cancel_gongdan(self, gongdan_id: str, cancel_reason: str, cancelled_by: str) -> FuwuGongdanDetailResponse:
        """取消工单"""
        gongdan_update = FuwuGongdanUpdate(
            gongdan_zhuangtai="cancelled"
        )

        result = self.update_gongdan(gongdan_id, gongdan_update, cancelled_by)

        # 添加取消日志
        rizhi = FuwuGongdanRizhi(
            gongdan_id=gongdan_id,
            caozuo_leixing="cancelled",
            caozuo_neirong=f"工单已取消，原因：{cancel_reason}",
            caozuo_ren_id=cancelled_by,
            created_by=cancelled_by
        )
        self.db.add(rizhi)
        self.db.commit()

        return result

    def add_gongdan_comment(self, gongdan_id: str, comment: str, operator_id: str, fujian_lujing: Optional[str] = None) -> FuwuGongdanRizhiResponse:
        """添加工单评论"""
        # 验证工单是否存在
        gongdan = self.db.query(FuwuGongdan).filter(
            FuwuGongdan.id == gongdan_id,
            FuwuGongdan.is_deleted == "N"
        ).first()

        if not gongdan:
            raise HTTPException(status_code=404, detail="工单不存在")

        # 创建评论日志
        rizhi = FuwuGongdanRizhi(
            gongdan_id=gongdan_id,
            caozuo_leixing="commented",
            caozuo_neirong=comment,
            caozuo_ren_id=operator_id,
            fujian_lujing=fujian_lujing,
            created_by=operator_id
        )

        self.db.add(rizhi)
        self.db.commit()
        self.db.refresh(rizhi)

        return FuwuGongdanRizhiResponse.model_validate(rizhi)

    def get_gongdan_statistics(self, kehu_id: Optional[str] = None, zhixing_ren_id: Optional[str] = None) -> FuwuGongdanStatistics:
        """获取工单统计信息"""
        query = self.db.query(FuwuGongdan).filter(FuwuGongdan.is_deleted == "N")

        # 应用过滤条件
        if kehu_id:
            query = query.filter(FuwuGongdan.kehu_id == kehu_id)

        if zhixing_ren_id:
            query = query.filter(FuwuGongdan.zhixing_ren_id == zhixing_ren_id)

        # 统计各状态数量
        total_count = query.count()
        created_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "created").count()
        assigned_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "assigned").count()
        in_progress_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "in_progress").count()
        pending_review_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "pending_review").count()
        completed_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "completed").count()
        cancelled_count = query.filter(FuwuGongdan.gongdan_zhuangtai == "cancelled").count()

        # 统计逾期数量
        overdue_count = query.filter(
            FuwuGongdan.jihua_jieshu_shijian < datetime.now(),
            FuwuGongdan.gongdan_zhuangtai.notin_(["completed", "cancelled"])
        ).count()

        # 计算平均完成天数
        completed_gongdan_list = query.filter(
            FuwuGongdan.gongdan_zhuangtai == "completed",
            FuwuGongdan.shiji_kaishi_shijian.isnot(None),
            FuwuGongdan.shiji_jieshu_shijian.isnot(None)
        ).all()

        if completed_gongdan_list:
            total_days = sum([
                (gongdan.shiji_jieshu_shijian - gongdan.shiji_kaishi_shijian).days
                for gongdan in completed_gongdan_list
            ])
            avg_completion_days = total_days / len(completed_gongdan_list)
        else:
            avg_completion_days = 0.0

        # 计算完成率
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0.0

        return FuwuGongdanStatistics(
            total_count=total_count,
            created_count=created_count,
            assigned_count=assigned_count,
            in_progress_count=in_progress_count,
            pending_review_count=pending_review_count,
            completed_count=completed_count,
            cancelled_count=cancelled_count,
            overdue_count=overdue_count,
            avg_completion_days=avg_completion_days,
            completion_rate=completion_rate
        )
