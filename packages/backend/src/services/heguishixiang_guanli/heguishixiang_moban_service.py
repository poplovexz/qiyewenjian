"""
合规事项模板管理服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status

from models.heguishixiang_guanli import HeguishixiangMoban
from schemas.heguishixiang_guanli.heguishixiang_moban_schemas import (
    HeguishixiangMobanCreate,
    HeguishixiangMobanUpdate,
    HeguishixiangMobanResponse,
    HeguishixiangMobanListParams,
    HeguishixiangMobanListResponse,
    HeguishixiangMobanOptionsResponse
)
import uuid


class HeguishixiangMobanService:
    """合规事项模板管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_moban(self, moban_data: HeguishixiangMobanCreate, created_by: str) -> HeguishixiangMobanResponse:
        """创建合规事项模板"""
        # 检查编码是否已存在
        existing_moban = self.db.query(HeguishixiangMoban).filter(
            and_(
                HeguishixiangMoban.shixiang_bianma == moban_data.shixiang_bianma,
                HeguishixiangMoban.is_deleted == "N"
            )
        ).first()

        if existing_moban:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="事项编码已存在"
            )

        # 创建模板
        moban = HeguishixiangMoban(
            id=str(uuid.uuid4()),
            **moban_data.model_dump(),
            created_by=created_by,
            is_deleted="N"
        )

        self.db.add(moban)
        self.db.commit()
        self.db.refresh(moban)

        return HeguishixiangMobanResponse.model_validate(moban)

    def get_moban_by_id(self, moban_id: str) -> HeguishixiangMobanResponse:
        """根据ID获取合规事项模板"""
        moban = self.db.query(HeguishixiangMoban).filter(
            and_(
                HeguishixiangMoban.id == moban_id,
                HeguishixiangMoban.is_deleted == "N"
            )
        ).first()

        if not moban:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合规事项模板不存在"
            )

        return HeguishixiangMobanResponse.model_validate(moban)

    def update_moban(self, moban_id: str, moban_data: HeguishixiangMobanUpdate, updated_by: str) -> HeguishixiangMobanResponse:
        """更新合规事项模板"""
        moban = self.db.query(HeguishixiangMoban).filter(
            and_(
                HeguishixiangMoban.id == moban_id,
                HeguishixiangMoban.is_deleted == "N"
            )
        ).first()

        if not moban:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合规事项模板不存在"
            )

        # 检查编码是否重复
        if moban_data.shixiang_bianma and moban_data.shixiang_bianma != moban.shixiang_bianma:
            existing_moban = self.db.query(HeguishixiangMoban).filter(
                and_(
                    HeguishixiangMoban.shixiang_bianma == moban_data.shixiang_bianma,
                    HeguishixiangMoban.id != moban_id,
                    HeguishixiangMoban.is_deleted == "N"
                )
            ).first()

            if existing_moban:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="事项编码已存在"
                )

        # 更新字段
        update_data = moban_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(moban, field, value)

        moban.updated_by = updated_by
        moban.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(moban)

        return HeguishixiangMobanResponse.model_validate(moban)

    def delete_moban(self, moban_id: str, deleted_by: str) -> bool:
        """删除合规事项模板（软删除）"""
        moban = self.db.query(HeguishixiangMoban).filter(
            and_(
                HeguishixiangMoban.id == moban_id,
                HeguishixiangMoban.is_deleted == "N"
            )
        ).first()

        if not moban:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合规事项模板不存在"
            )

        # 检查是否有关联的客户配置
        from models.heguishixiang_guanli import KehuHeguishixiang
        related_configs = self.db.query(KehuHeguishixiang).filter(
            and_(
                KehuHeguishixiang.heguishixiang_moban_id == moban_id,
                KehuHeguishixiang.is_deleted == "N"
            )
        ).count()

        if related_configs > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该模板已被客户使用，无法删除"
            )

        # 执行软删除
        moban.is_deleted = "Y"
        moban.updated_by = deleted_by
        moban.updated_at = datetime.now()

        self.db.commit()
        return True

    def get_moban_list(self, params: HeguishixiangMobanListParams) -> HeguishixiangMobanListResponse:
        """获取合规事项模板列表"""
        query = self.db.query(HeguishixiangMoban).filter(HeguishixiangMoban.is_deleted == "N")

        # 搜索条件
        if params.search:
            search_pattern = f"%{params.search}%"
            query = query.filter(
                or_(
                    HeguishixiangMoban.shixiang_mingcheng.ilike(search_pattern),
                    HeguishixiangMoban.shixiang_bianma.ilike(search_pattern),
                    HeguishixiangMoban.shixiang_miaoshu.ilike(search_pattern)
                )
            )

        # 筛选条件
        if params.shixiang_leixing:
            query = query.filter(HeguishixiangMoban.shixiang_leixing == params.shixiang_leixing)

        if params.shenbao_zhouqi:
            query = query.filter(HeguishixiangMoban.shenbao_zhouqi == params.shenbao_zhouqi)

        if params.moban_zhuangtai:
            query = query.filter(HeguishixiangMoban.moban_zhuangtai == params.moban_zhuangtai)

        if params.fengxian_dengji:
            query = query.filter(HeguishixiangMoban.fengxian_dengji == params.fengxian_dengji)

        # 排序
        query = query.order_by(HeguishixiangMoban.paixu.asc(), desc(HeguishixiangMoban.created_at))

        # 分页
        total = query.count()
        offset = (params.page - 1) * params.size
        items = query.offset(offset).limit(params.size).all()

        return HeguishixiangMobanListResponse(
            items=[HeguishixiangMobanResponse.model_validate(item) for item in items],
            total=total,
            page=params.page,
            size=params.size,
            pages=(total + params.size - 1) // params.size
        )

    def get_moban_options(self) -> HeguishixiangMobanOptionsResponse:
        """获取合规事项模板选项"""
        return HeguishixiangMobanOptionsResponse(
            shixiang_leixing_options=[
                {"value": "shuiwu_shenbao", "label": "税务申报"},
                {"value": "nianbao_shenbao", "label": "年报申报"},
                {"value": "zhizhao_nianjian", "label": "执照年检"},
                {"value": "qita_heguishixiang", "label": "其他合规事项"}
            ],
            shenbao_zhouqi_options=[
                {"value": "monthly", "label": "月度"},
                {"value": "quarterly", "label": "季度"},
                {"value": "annually", "label": "年度"},
                {"value": "custom", "label": "自定义"}
            ],
            fengxian_dengji_options=[
                {"value": "low", "label": "低"},
                {"value": "medium", "label": "中"},
                {"value": "high", "label": "高"},
                {"value": "critical", "label": "严重"}
            ],
            moban_zhuangtai_options=[
                {"value": "active", "label": "启用"},
                {"value": "inactive", "label": "停用"},
                {"value": "draft", "label": "草稿"}
            ]
        )

    def get_active_mobans(self) -> List[HeguishixiangMobanResponse]:
        """获取所有启用的合规事项模板"""
        mobans = self.db.query(HeguishixiangMoban).filter(
            and_(
                HeguishixiangMoban.moban_zhuangtai == "active",
                HeguishixiangMoban.is_deleted == "N"
            )
        ).order_by(HeguishixiangMoban.paixu.asc()).all()

        return [HeguishixiangMobanResponse.model_validate(moban) for moban in mobans]
