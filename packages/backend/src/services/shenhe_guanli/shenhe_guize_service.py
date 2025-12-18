"""
审核规则配置服务
"""
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException

from models.shenhe_guanli import ShenheGuize
from schemas.shenhe_guanli import (
    ShenheGuizeCreate,
    ShenheGuizeUpdate,
    ShenheGuizeResponse,
    ShenheGuizeListParams
)


class ShenheGuizeService:
    """审核规则配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_shenhe_guize(self, guize_data: ShenheGuizeCreate, created_by: str) -> ShenheGuizeResponse:
        """创建审核规则"""
        # 检查规则名称是否重复
        existing_rule = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_mingcheng == guize_data.guize_mingcheng,
            ShenheGuize.is_deleted == "N"
        ).first()
        
        if existing_rule:
            raise HTTPException(status_code=400, detail="规则名称已存在")
        
        # 验证触发条件和流程配置的JSON格式
        try:
            if isinstance(guize_data.chufa_tiaojian, dict):
                chufa_tiaojian_str = json.dumps(guize_data.chufa_tiaojian, ensure_ascii=False)
            else:
                chufa_tiaojian_str = guize_data.chufa_tiaojian
                
            if isinstance(guize_data.shenhe_liucheng_peizhi, dict):
                liucheng_peizhi_str = json.dumps(guize_data.shenhe_liucheng_peizhi, ensure_ascii=False)
            else:
                liucheng_peizhi_str = guize_data.shenhe_liucheng_peizhi
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"JSON格式错误: {str(e)}")
        
        # 创建审核规则
        guize = ShenheGuize(
            id=str(uuid.uuid4()),
            guize_mingcheng=guize_data.guize_mingcheng,
            guize_leixing=guize_data.guize_leixing,
            chufa_tiaojian=chufa_tiaojian_str,
            shenhe_liucheng_peizhi=liucheng_peizhi_str,
            shi_qiyong=guize_data.shi_qiyong,
            paixu=guize_data.paixu,
            guize_miaoshu=guize_data.guize_miaoshu,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        
        self.db.add(guize)
        self.db.commit()
        self.db.refresh(guize)
        
        return self._to_response(guize)
    
    def get_shenhe_guize_list(self, params: ShenheGuizeListParams) -> Dict[str, Any]:
        """获取审核规则列表（不包含工作流模板）"""
        # 🔧 修复：排除工作流模板类型，工作流模板应该只在工作流配置页面显示
        query = self.db.query(ShenheGuize).filter(
            ShenheGuize.is_deleted == "N",
            ShenheGuize.guize_leixing != "workflow_template"  # 排除工作流模板
        )

        # 搜索条件
        if params.search:
            search_filter = or_(
                ShenheGuize.guize_mingcheng.contains(params.search),
                ShenheGuize.guize_miaoshu.contains(params.search)
            )
            query = query.filter(search_filter)

        # 筛选条件
        if params.guize_leixing:
            query = query.filter(ShenheGuize.guize_leixing == params.guize_leixing)

        if params.shi_qiyong:
            query = query.filter(ShenheGuize.shi_qiyong == params.shi_qiyong)
        
        # 排序
        if params.sort_by:
            sort_column = getattr(ShenheGuize, params.sort_by, None)
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
    
    def get_shenhe_guize_by_id(self, guize_id: str) -> ShenheGuizeResponse:
        """根据ID获取审核规则"""
        guize = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == guize_id,
            ShenheGuize.is_deleted == "N"
        ).first()

        if not guize:
            raise HTTPException(status_code=404, detail="审核规则不存在")

        # 注意：允许读取工作流模板（用于显示），但不允许修改/删除
        # 工作流模板的修改/删除应该通过工作流API进行

        return self._to_response(guize)
    
    def update_shenhe_guize(self, guize_id: str, guize_data: ShenheGuizeUpdate, updated_by: str) -> ShenheGuizeResponse:
        """更新审核规则"""
        guize = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == guize_id,
            ShenheGuize.is_deleted == "N"
        ).first()

        if not guize:
            raise HTTPException(status_code=404, detail="审核规则不存在")

        # 🔧 修复：防止通过审核规则API修改工作流模板
        if guize.guize_leixing == "workflow_template":
            raise HTTPException(status_code=403, detail="工作流模板请在工作流配置页面管理")

        # 检查规则名称是否重复
        if guize_data.guize_mingcheng and guize_data.guize_mingcheng != guize.guize_mingcheng:
            existing_rule = self.db.query(ShenheGuize).filter(
                ShenheGuize.guize_mingcheng == guize_data.guize_mingcheng,
                ShenheGuize.id != guize_id,
                ShenheGuize.is_deleted == "N"
            ).first()
            
            if existing_rule:
                raise HTTPException(status_code=400, detail="规则名称已存在")
        
        # 更新字段
        update_data = guize_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["chufa_tiaojian", "shenhe_liucheng_peizhi"] and isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            setattr(guize, field, value)
        
        guize.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(guize)
        
        return self._to_response(guize)
    
    def delete_shenhe_guize(self, guize_id: str) -> bool:
        """删除审核规则"""
        guize = self.db.query(ShenheGuize).filter(
            ShenheGuize.id == guize_id,
            ShenheGuize.is_deleted == "N"
        ).first()

        if not guize:
            raise HTTPException(status_code=404, detail="审核规则不存在")

        # 🔧 修复：防止通过审核规则API删除工作流模板
        if guize.guize_leixing == "workflow_template":
            raise HTTPException(status_code=403, detail="工作流模板请在工作流配置页面管理")

        # 检查是否有关联的审核流程
        from models.shenhe_guanli import ShenheLiucheng
        related_workflows = self.db.query(ShenheLiucheng).filter(
            ShenheLiucheng.chufa_guize_id == guize_id,
            ShenheLiucheng.is_deleted == "N"
        ).count()
        
        if related_workflows > 0:
            raise HTTPException(status_code=400, detail="该规则已被使用，无法删除")
        
        guize.is_deleted = "Y"
        guize.updated_at = datetime.now()
        
        self.db.commit()
        return True
    
    def get_active_rules_by_type(self, guize_leixing: str) -> List[ShenheGuizeResponse]:
        """根据类型获取启用的审核规则"""
        rules = self.db.query(ShenheGuize).filter(
            ShenheGuize.guize_leixing == guize_leixing,
            ShenheGuize.shi_qiyong == "Y",
            ShenheGuize.is_deleted == "N"
        ).order_by(ShenheGuize.paixu).all()
        
        return [self._to_response(rule) for rule in rules]
    
    def _to_response(self, guize: ShenheGuize) -> ShenheGuizeResponse:
        """转换为响应模型"""
        # 解析JSON字段
        try:
            chufa_tiaojian = json.loads(guize.chufa_tiaojian) if isinstance(guize.chufa_tiaojian, str) else guize.chufa_tiaojian
        except (json.JSONDecodeError, TypeError):
            chufa_tiaojian = {}

        try:
            shenhe_liucheng_peizhi = json.loads(guize.shenhe_liucheng_peizhi) if isinstance(guize.shenhe_liucheng_peizhi, str) else guize.shenhe_liucheng_peizhi
        except (json.JSONDecodeError, TypeError):
            shenhe_liucheng_peizhi = {}
        
        return ShenheGuizeResponse(
            id=guize.id,
            guize_mingcheng=guize.guize_mingcheng,
            guize_leixing=guize.guize_leixing,
            chufa_tiaojian=chufa_tiaojian,
            shenhe_liucheng_peizhi=shenhe_liucheng_peizhi,
            shi_qiyong=guize.shi_qiyong,
            paixu=guize.paixu,
            guize_miaoshu=guize.guize_miaoshu,
            created_at=guize.created_at,
            updated_at=guize.updated_at,
            created_by=guize.created_by
        )
