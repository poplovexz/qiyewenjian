"""
用户管理服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from models.yonghu_guanli import Yonghu, Jiaose, Quanxian, YonghuJiaose, JiaoseQuanxian
from schemas.yonghu_guanli import (
    YonghuCreate, YonghuUpdate, YonghuResponse, YonghuList,
    JiaoseResponse,
    QuanxianResponse
)
from core.security import get_password_hash

class YonghuService:
    """用户管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_yonghu(self, yonghu_data: YonghuCreate, created_by: str) -> YonghuResponse:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.db.query(Yonghu).filter(
            and_(
                Yonghu.yonghu_ming == yonghu_data.yonghu_ming,
                Yonghu.is_deleted == 'N'
            )
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if yonghu_data.youxiang:
            existing_email = self.db.query(Yonghu).filter(
                and_(
                    Yonghu.youxiang == yonghu_data.youxiang,
                    Yonghu.is_deleted == 'N'
                )
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 创建新用户
        db_yonghu = Yonghu(
            yonghu_ming=yonghu_data.yonghu_ming,
            mima=get_password_hash(yonghu_data.mima),
            youxiang=yonghu_data.youxiang,
            xingming=yonghu_data.xingming,
            shouji=yonghu_data.shouji,
            zhuangtai=yonghu_data.zhuangtai or '正常',
            created_by=created_by,
            remark=yonghu_data.remark
        )
        
        self.db.add(db_yonghu)
        self.db.commit()
        self.db.refresh(db_yonghu)
        
        return YonghuResponse.model_validate(db_yonghu)
    
    def get_yonghu_by_id(self, yonghu_id: str) -> Optional[YonghuResponse]:
        """根据ID获取用户"""
        yonghu = self.db.query(Yonghu).filter(
            and_(
                Yonghu.id == yonghu_id,
                Yonghu.is_deleted == 'N'
            )
        ).first()
        
        if not yonghu:
            return None
        
        return YonghuResponse.model_validate(yonghu)
    
    def get_yonghu_list(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        zhuangtai: Optional[str] = None
    ) -> YonghuList:
        """获取用户列表"""
        query = self.db.query(Yonghu).filter(Yonghu.is_deleted == 'N')

        # 搜索条件
        if search:
            search_filter = or_(
                Yonghu.yonghu_ming.contains(search),
                Yonghu.xingming.contains(search),
                Yonghu.youxiang.contains(search),
                Yonghu.shouji.contains(search)
            )
            query = query.filter(search_filter)

        # 状态筛选
        if zhuangtai:
            query = query.filter(Yonghu.zhuangtai == zhuangtai)

        # 获取总数
        total = query.count()

        # 计算跳过的记录数
        skip = (page - 1) * size

        # 分页查询
        yonghu_list = query.offset(skip).limit(size).all()

        return YonghuList(
            items=[YonghuResponse.model_validate(yonghu) for yonghu in yonghu_list],
            total=total,
            page=page,
            size=size
        )
    
    def update_yonghu(
        self, 
        yonghu_id: str, 
        yonghu_data: YonghuUpdate, 
        updated_by: str
    ) -> YonghuResponse:
        """更新用户信息"""
        yonghu = self.db.query(Yonghu).filter(
            and_(
                Yonghu.id == yonghu_id,
                Yonghu.is_deleted == 'N'
            )
        ).first()
        
        if not yonghu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查用户名是否已被其他用户使用
        if yonghu_data.yonghu_ming and yonghu_data.yonghu_ming != yonghu.yonghu_ming:
            existing_user = self.db.query(Yonghu).filter(
                and_(
                    Yonghu.yonghu_ming == yonghu_data.yonghu_ming,
                    Yonghu.id != yonghu_id,
                    Yonghu.is_deleted == 'N'
                )
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
        
        # 检查邮箱是否已被其他用户使用
        if yonghu_data.youxiang and yonghu_data.youxiang != yonghu.youxiang:
            existing_email = self.db.query(Yonghu).filter(
                and_(
                    Yonghu.youxiang == yonghu_data.youxiang,
                    Yonghu.id != yonghu_id,
                    Yonghu.is_deleted == 'N'
                )
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 更新用户信息
        update_data = yonghu_data.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要加密
        if 'mima' in update_data:
            update_data['mima'] = get_password_hash(update_data['mima'])
        
        # 设置更新信息
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(yonghu, field, value)
        
        self.db.commit()
        self.db.refresh(yonghu)
        
        return YonghuResponse.model_validate(yonghu)
    
    def delete_yonghu(self, yonghu_id: str, deleted_by: str) -> bool:
        """删除用户（软删除）"""
        yonghu = self.db.query(Yonghu).filter(
            and_(
                Yonghu.id == yonghu_id,
                Yonghu.is_deleted == 'N'
            )
        ).first()
        
        if not yonghu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 软删除
        yonghu.is_deleted = 'Y'
        yonghu.updated_by = deleted_by
        yonghu.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def assign_roles(self, yonghu_id: str, jiaose_ids: List[str], assigned_by: str) -> bool:
        """为用户分配角色"""
        yonghu = self.db.query(Yonghu).filter(
            and_(
                Yonghu.id == yonghu_id,
                Yonghu.is_deleted == 'N'
            )
        ).first()
        
        if not yonghu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 删除现有角色关联
        self.db.query(YonghuJiaose).filter(YonghuJiaose.yonghu_id == yonghu_id).delete()
        
        # 添加新的角色关联
        for jiaose_id in jiaose_ids:
            # 验证角色是否存在
            jiaose = self.db.query(Jiaose).filter(
                and_(
                    Jiaose.id == jiaose_id,
                    Jiaose.is_deleted == 'N'
                )
            ).first()
            
            if jiaose:
                yonghu_jiaose = YonghuJiaose(
                    yonghu_id=yonghu_id,
                    jiaose_id=jiaose_id,
                    created_by=assigned_by
                )
                self.db.add(yonghu_jiaose)
        
        self.db.commit()
        return True
    
    def get_yonghu_roles(self, yonghu_id: str) -> List[JiaoseResponse]:
        """获取用户的角色列表"""
        roles = self.db.query(Jiaose).join(YonghuJiaose).filter(
            and_(
                YonghuJiaose.yonghu_id == yonghu_id,
                Jiaose.is_deleted == 'N'
            )
        ).all()
        
        return [JiaoseResponse.model_validate(role) for role in roles]
    
    def get_yonghu_permissions(self, yonghu_id: str) -> List[QuanxianResponse]:
        """获取用户的权限列表"""
        permissions = self.db.query(Quanxian).join(JiaoseQuanxian).join(YonghuJiaose).filter(
            and_(
                YonghuJiaose.yonghu_id == yonghu_id,
                Quanxian.is_deleted == 'N'
            )
        ).distinct().all()
        
        return [QuanxianResponse.model_validate(permission) for permission in permissions]
