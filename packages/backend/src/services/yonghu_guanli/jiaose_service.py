"""
角色管理服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from ...models.yonghu_guanli import Jiaose, Quanxian, JiaoseQuanxian, YonghuJiaose
from ...schemas.yonghu_guanli import (
    JiaoseCreate, JiaoseUpdate, JiaoseResponse, JiaoseList,
    QuanxianResponse
)


class JiaoseService:
    """角色管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_jiaose(self, jiaose_data: JiaoseCreate, created_by: str) -> JiaoseResponse:
        """创建角色"""
        # 检查角色名称是否已存在
        existing_role = self.db.query(Jiaose).filter(
            and_(
                Jiaose.jiaose_ming == jiaose_data.jiaose_ming,
                Jiaose.is_deleted == 'N'
            )
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )
        
        # 检查角色代码是否已存在
        if jiaose_data.jiaose_daima:
            existing_code = self.db.query(Jiaose).filter(
                and_(
                    Jiaose.jiaose_daima == jiaose_data.jiaose_daima,
                    Jiaose.is_deleted == 'N'
                )
            ).first()
            
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色代码已存在"
                )
        
        # 创建新角色
        db_jiaose = Jiaose(
            jiaose_ming=jiaose_data.jiaose_ming,
            jiaose_daima=jiaose_data.jiaose_daima,
            miaoshu=jiaose_data.miaoshu,
            zhuangtai=jiaose_data.zhuangtai or '启用',
            created_by=created_by,
            remark=jiaose_data.remark
        )
        
        self.db.add(db_jiaose)
        self.db.commit()
        self.db.refresh(db_jiaose)
        
        return JiaoseResponse.model_validate(db_jiaose)
    
    def get_jiaose_by_id(self, jiaose_id: str) -> Optional[JiaoseResponse]:
        """根据ID获取角色"""
        jiaose = self.db.query(Jiaose).filter(
            and_(
                Jiaose.id == jiaose_id,
                Jiaose.is_deleted == 'N'
            )
        ).first()
        
        if not jiaose:
            return None
        
        return JiaoseResponse.model_validate(jiaose)
    
    def get_jiaose_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> JiaoseList:
        """获取角色列表"""
        query = self.db.query(Jiaose).filter(Jiaose.is_deleted == 'N')
        
        # 搜索条件
        if search:
            search_filter = or_(
                Jiaose.jiaose_ming.contains(search),
                Jiaose.jiaose_daima.contains(search),
                Jiaose.miaoshu.contains(search)
            )
            query = query.filter(search_filter)
        
        # 状态筛选
        if zhuangtai:
            query = query.filter(Jiaose.zhuangtai == zhuangtai)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        jiaose_list = query.offset(skip).limit(limit).all()
        
        return JiaoseList(
            items=[JiaoseResponse.model_validate(jiaose) for jiaose in jiaose_list],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    
    def update_jiaose(
        self, 
        jiaose_id: str, 
        jiaose_data: JiaoseUpdate, 
        updated_by: str
    ) -> JiaoseResponse:
        """更新角色信息"""
        jiaose = self.db.query(Jiaose).filter(
            and_(
                Jiaose.id == jiaose_id,
                Jiaose.is_deleted == 'N'
            )
        ).first()
        
        if not jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查角色名称是否已被其他角色使用
        if jiaose_data.jiaose_ming and jiaose_data.jiaose_ming != jiaose.jiaose_ming:
            existing_role = self.db.query(Jiaose).filter(
                and_(
                    Jiaose.jiaose_ming == jiaose_data.jiaose_ming,
                    Jiaose.id != jiaose_id,
                    Jiaose.is_deleted == 'N'
                )
            ).first()
            
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色名称已存在"
                )
        
        # 检查角色代码是否已被其他角色使用
        if jiaose_data.jiaose_daima and jiaose_data.jiaose_daima != jiaose.jiaose_daima:
            existing_code = self.db.query(Jiaose).filter(
                and_(
                    Jiaose.jiaose_daima == jiaose_data.jiaose_daima,
                    Jiaose.id != jiaose_id,
                    Jiaose.is_deleted == 'N'
                )
            ).first()
            
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色代码已存在"
                )
        
        # 更新角色信息
        update_data = jiaose_data.model_dump(exclude_unset=True)
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(jiaose, field, value)
        
        self.db.commit()
        self.db.refresh(jiaose)
        
        return JiaoseResponse.model_validate(jiaose)
    
    def delete_jiaose(self, jiaose_id: str, deleted_by: str) -> bool:
        """删除角色（软删除）"""
        jiaose = self.db.query(Jiaose).filter(
            and_(
                Jiaose.id == jiaose_id,
                Jiaose.is_deleted == 'N'
            )
        ).first()
        
        if not jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查是否有用户使用此角色
        user_count = self.db.query(YonghuJiaose).filter(
            YonghuJiaose.jiaose_id == jiaose_id
        ).count()
        
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该角色正在被用户使用，无法删除"
            )
        
        # 软删除
        jiaose.is_deleted = 'Y'
        jiaose.updated_by = deleted_by
        jiaose.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def assign_permissions(self, jiaose_id: str, quanxian_ids: List[str], assigned_by: str) -> bool:
        """为角色分配权限"""
        jiaose = self.db.query(Jiaose).filter(
            and_(
                Jiaose.id == jiaose_id,
                Jiaose.is_deleted == 'N'
            )
        ).first()
        
        if not jiaose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 删除现有权限关联
        self.db.query(JiaoseQuanxian).filter(JiaoseQuanxian.jiaose_id == jiaose_id).delete()
        
        # 添加新的权限关联
        for quanxian_id in quanxian_ids:
            # 验证权限是否存在
            quanxian = self.db.query(Quanxian).filter(
                and_(
                    Quanxian.id == quanxian_id,
                    Quanxian.is_deleted == 'N'
                )
            ).first()
            
            if quanxian:
                jiaose_quanxian = JiaoseQuanxian(
                    jiaose_id=jiaose_id,
                    quanxian_id=quanxian_id,
                    created_by=assigned_by
                )
                self.db.add(jiaose_quanxian)
        
        self.db.commit()
        return True
    
    def get_jiaose_permissions(self, jiaose_id: str) -> List[QuanxianResponse]:
        """获取角色的权限列表"""
        permissions = self.db.query(Quanxian).join(JiaoseQuanxian).filter(
            and_(
                JiaoseQuanxian.jiaose_id == jiaose_id,
                Quanxian.is_deleted == 'N'
            )
        ).all()
        
        return [QuanxianResponse.model_validate(permission) for permission in permissions]
