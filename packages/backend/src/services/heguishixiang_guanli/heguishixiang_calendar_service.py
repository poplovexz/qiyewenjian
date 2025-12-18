"""
合规日历服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from models.heguishixiang_guanli import HeguishixiangShili, HeguishixiangMoban
from models.kehu_guanli import Kehu


class HeguishixiangCalendarService:
    """合规日历服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_calendar_data(
        self,
        year: int,
        month: Optional[int] = None,
        kehu_id: Optional[str] = None,
        shixiang_leixing: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取合规日历数据"""
        
        # 构建查询
        query = self.db.query(HeguishixiangShili).join(
            HeguishixiangMoban,
            HeguishixiangShili.heguishixiang_moban_id == HeguishixiangMoban.id
        ).join(
            Kehu,
            HeguishixiangShili.kehu_id == Kehu.id
        ).filter(
            and_(
                HeguishixiangShili.is_deleted == "N",
                HeguishixiangMoban.is_deleted == "N",
                Kehu.is_deleted == "N"
            )
        )

        # 时间范围筛选
        if month:
            # 月度视图
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        else:
            # 年度视图
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)

        query = query.filter(
            and_(
                HeguishixiangShili.jihua_jieshu_shijian >= start_date,
                HeguishixiangShili.jihua_jieshu_shijian <= end_date
            )
        )

        # 其他筛选条件
        if kehu_id:
            query = query.filter(HeguishixiangShili.kehu_id == kehu_id)

        if shixiang_leixing:
            query = query.filter(HeguishixiangMoban.shixiang_leixing == shixiang_leixing)

        # 获取数据
        shili_list = query.all()

        # 构建日历数据
        calendar_data = {}
        
        for shili in shili_list:
            date_key = shili.jihua_jieshu_shijian.strftime("%Y-%m-%d")
            
            if date_key not in calendar_data:
                calendar_data[date_key] = []

            # 计算状态和紧急程度
            status_info = self._get_status_info(shili)
            
            calendar_data[date_key].append({
                "id": shili.id,
                "shili_bianhao": shili.shili_bianhao,
                "shili_mingcheng": shili.shili_mingcheng,
                "shenbao_qijian": shili.shenbao_qijian,
                "shili_zhuangtai": shili.shili_zhuangtai,
                "jihua_jieshu_shijian": shili.jihua_jieshu_shijian.isoformat(),
                "kehu_mingcheng": shili.kehu.gongsi_mingcheng,
                "shixiang_leixing": shili.heguishixiang_moban.shixiang_leixing,
                "shixiang_mingcheng": shili.heguishixiang_moban.shixiang_mingcheng,
                "fengxian_dengji": shili.fengxian_dengji,
                "yuqi_tianshu": shili.yuqi_tianshu,
                "wancheng_jindu": shili.wancheng_jindu,
                "status_info": status_info
            })

        return {
            "year": year,
            "month": month,
            "calendar_data": calendar_data,
            "summary": self._get_calendar_summary(shili_list, year, month)
        }

    def get_upcoming_items(
        self,
        days: int = 7,
        kehu_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取即将到期的合规事项"""
        
        end_date = datetime.now() + timedelta(days=days)
        
        query = self.db.query(HeguishixiangShili).join(
            HeguishixiangMoban,
            HeguishixiangShili.heguishixiang_moban_id == HeguishixiangMoban.id
        ).join(
            Kehu,
            HeguishixiangShili.kehu_id == Kehu.id
        ).filter(
            and_(
                HeguishixiangShili.is_deleted == "N",
                HeguishixiangMoban.is_deleted == "N",
                Kehu.is_deleted == "N",
                HeguishixiangShili.shili_zhuangtai.in_(["pending", "in_progress"]),
                HeguishixiangShili.jihua_jieshu_shijian <= end_date,
                HeguishixiangShili.jihua_jieshu_shijian >= datetime.now()
            )
        )

        if kehu_id:
            query = query.filter(HeguishixiangShili.kehu_id == kehu_id)

        shili_list = query.order_by(HeguishixiangShili.jihua_jieshu_shijian.asc()).all()

        return [
            {
                "id": shili.id,
                "shili_bianhao": shili.shili_bianhao,
                "shili_mingcheng": shili.shili_mingcheng,
                "shenbao_qijian": shili.shenbao_qijian,
                "shili_zhuangtai": shili.shili_zhuangtai,
                "jihua_jieshu_shijian": shili.jihua_jieshu_shijian.isoformat(),
                "kehu_mingcheng": shili.kehu.gongsi_mingcheng,
                "shixiang_leixing": shili.heguishixiang_moban.shixiang_leixing,
                "shixiang_mingcheng": shili.heguishixiang_moban.shixiang_mingcheng,
                "fengxian_dengji": shili.fengxian_dengji,
                "days_remaining": (shili.jihua_jieshu_shijian.date() - datetime.now().date()).days,
                "status_info": self._get_status_info(shili)
            }
            for shili in shili_list
        ]

    def get_overdue_items(
        self,
        kehu_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取逾期的合规事项"""
        
        query = self.db.query(HeguishixiangShili).join(
            HeguishixiangMoban,
            HeguishixiangShili.heguishixiang_moban_id == HeguishixiangMoban.id
        ).join(
            Kehu,
            HeguishixiangShili.kehu_id == Kehu.id
        ).filter(
            and_(
                HeguishixiangShili.is_deleted == "N",
                HeguishixiangMoban.is_deleted == "N",
                Kehu.is_deleted == "N",
                HeguishixiangShili.shili_zhuangtai.in_(["pending", "in_progress", "overdue"]),
                HeguishixiangShili.jihua_jieshu_shijian < datetime.now()
            )
        )

        if kehu_id:
            query = query.filter(HeguishixiangShili.kehu_id == kehu_id)

        shili_list = query.order_by(HeguishixiangShili.jihua_jieshu_shijian.desc()).all()

        return [
            {
                "id": shili.id,
                "shili_bianhao": shili.shili_bianhao,
                "shili_mingcheng": shili.shili_mingcheng,
                "shenbao_qijian": shili.shenbao_qijian,
                "shili_zhuangtai": shili.shili_zhuangtai,
                "jihua_jieshu_shijian": shili.jihua_jieshu_shijian.isoformat(),
                "kehu_mingcheng": shili.kehu.gongsi_mingcheng,
                "shixiang_leixing": shili.heguishixiang_moban.shixiang_leixing,
                "shixiang_mingcheng": shili.heguishixiang_moban.shixiang_mingcheng,
                "fengxian_dengji": shili.fengxian_dengji,
                "yuqi_tianshu": (datetime.now().date() - shili.jihua_jieshu_shijian.date()).days,
                "status_info": self._get_status_info(shili)
            }
            for shili in shili_list
        ]

    def get_statistics(
        self,
        year: int,
        month: Optional[int] = None,
        kehu_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取合规统计数据"""
        
        # 构建基础查询
        query = self.db.query(HeguishixiangShili).join(
            HeguishixiangMoban,
            HeguishixiangShili.heguishixiang_moban_id == HeguishixiangMoban.id
        ).filter(
            and_(
                HeguishixiangShili.is_deleted == "N",
                HeguishixiangMoban.is_deleted == "N"
            )
        )

        # 时间范围筛选
        if month:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        else:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)

        query = query.filter(
            and_(
                HeguishixiangShili.jihua_jieshu_shijian >= start_date,
                HeguishixiangShili.jihua_jieshu_shijian <= end_date
            )
        )

        if kehu_id:
            query = query.filter(HeguishixiangShili.kehu_id == kehu_id)

        # 统计各种状态的数量
        total_count = query.count()
        completed_count = query.filter(HeguishixiangShili.shili_zhuangtai == "completed").count()
        pending_count = query.filter(HeguishixiangShili.shili_zhuangtai == "pending").count()
        in_progress_count = query.filter(HeguishixiangShili.shili_zhuangtai == "in_progress").count()
        overdue_count = query.filter(
            and_(
                HeguishixiangShili.shili_zhuangtai.in_(["pending", "in_progress", "overdue"]),
                HeguishixiangShili.jihua_jieshu_shijian < datetime.now()
            )
        ).count()

        # 按事项类型统计
        type_stats = self.db.query(
            HeguishixiangMoban.shixiang_leixing,
            func.count(HeguishixiangShili.id).label("count")
        ).join(
            HeguishixiangShili,
            HeguishixiangMoban.id == HeguishixiangShili.heguishixiang_moban_id
        ).filter(
            and_(
                HeguishixiangShili.is_deleted == "N",
                HeguishixiangMoban.is_deleted == "N",
                HeguishixiangShili.jihua_jieshu_shijian >= start_date,
                HeguishixiangShili.jihua_jieshu_shijian <= end_date
            )
        ).group_by(HeguishixiangMoban.shixiang_leixing).all()

        return {
            "total_count": total_count,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "in_progress_count": in_progress_count,
            "overdue_count": overdue_count,
            "completion_rate": round(completed_count / total_count * 100, 2) if total_count > 0 else 0,
            "overdue_rate": round(overdue_count / total_count * 100, 2) if total_count > 0 else 0,
            "type_statistics": [
                {
                    "shixiang_leixing": stat.shixiang_leixing,
                    "count": stat.count
                }
                for stat in type_stats
            ]
        }

    @staticmethod
    def _get_status_info(shili: HeguishixiangShili) -> Dict[str, Any]:
        """获取状态信息"""
        now = datetime.now()
        deadline = shili.jihua_jieshu_shijian
        days_remaining = (deadline.date() - now.date()).days

        if shili.shili_zhuangtai == "completed":
            return {
                "status": "completed",
                "color": "success",
                "urgency": "none",
                "message": "已完成"
            }
        elif days_remaining < 0:
            return {
                "status": "overdue",
                "color": "danger",
                "urgency": "critical",
                "message": f"已逾期 {abs(days_remaining)} 天"
            }
        elif days_remaining == 0:
            return {
                "status": "due_today",
                "color": "danger",
                "urgency": "urgent",
                "message": "今日到期"
            }
        elif days_remaining <= 3:
            return {
                "status": "due_soon",
                "color": "warning",
                "urgency": "high",
                "message": f"{days_remaining} 天后到期"
            }
        elif days_remaining <= 7:
            return {
                "status": "upcoming",
                "color": "primary",
                "urgency": "medium",
                "message": f"{days_remaining} 天后到期"
            }
        else:
            return {
                "status": "normal",
                "color": "info",
                "urgency": "low",
                "message": f"{days_remaining} 天后到期"
            }

    @staticmethod
    def _get_calendar_summary(
        shili_list: List[HeguishixiangShili],
        year: int,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取日历摘要信息"""
        
        total_count = len(shili_list)
        completed_count = sum(1 for shili in shili_list if shili.shili_zhuangtai == "completed")
        overdue_count = sum(1 for shili in shili_list if shili.jihua_jieshu_shijian < datetime.now() and shili.shili_zhuangtai != "completed")
        
        return {
            "period": f"{year}年{month}月" if month else f"{year}年",
            "total_count": total_count,
            "completed_count": completed_count,
            "overdue_count": overdue_count,
            "completion_rate": round(completed_count / total_count * 100, 2) if total_count > 0 else 0
        }
