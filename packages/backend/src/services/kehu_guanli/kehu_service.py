"""
客户管理服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from src.models.kehu_guanli import Kehu
from src.schemas.kehu_guanli.kehu_schemas import (
    KehuCreate, 
    KehuUpdate, 
    KehuResponse,
    KehuListResponse
)


class KehuService:
    """客户管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_kehu(self, kehu_data: KehuCreate, created_by: str) -> KehuResponse:
        """创建客户"""
        # 验证统一社会信用代码唯一性
        existing_kehu = self.db.query(Kehu).filter(
            Kehu.tongyi_shehui_xinyong_daima == kehu_data.tongyi_shehui_xinyong_daima,
            Kehu.is_deleted == "N"
        ).first()
        
        if existing_kehu:
            raise HTTPException(status_code=400, detail="统一社会信用代码已存在")
        
        # 创建客户
        kehu = Kehu(
            **kehu_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(kehu)
        self.db.commit()
        self.db.refresh(kehu)
        
        return KehuResponse.model_validate(kehu)
    
    def get_kehu_by_id(self, kehu_id: str) -> Optional[KehuResponse]:
        """根据ID获取客户"""
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            return None
        
        return KehuResponse.model_validate(kehu)
    
    def get_kehu_list(
        self,
        page: int = 1,
        size: int = 100,
        search: Optional[str] = None,
        kehu_zhuangtai: Optional[str] = None
    ) -> KehuListResponse:
        """获取客户列表"""
        query = self.db.query(Kehu).filter(Kehu.is_deleted == "N")
        
        # 搜索条件
        if search:
            search_filter = or_(
                Kehu.gongsi_mingcheng.contains(search),
                Kehu.tongyi_shehui_xinyong_daima.contains(search),
                Kehu.faren_xingming.contains(search),
                Kehu.lianxi_dianhua.contains(search),
                Kehu.lianxi_youxiang.contains(search)
            )
            query = query.filter(search_filter)
        
        # 状态筛选
        if kehu_zhuangtai:
            query = query.filter(Kehu.kehu_zhuangtai == kehu_zhuangtai)
        
        # 总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * size
        kehu_list = query.offset(offset).limit(size).all()
        
        return KehuListResponse(
            total=total,
            items=[KehuResponse.model_validate(kehu) for kehu in kehu_list],
            page=page,
            size=size
        )
    
    def update_kehu(self, kehu_id: str, kehu_data: KehuUpdate, updated_by: str) -> KehuResponse:
        """更新客户"""
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 如果更新统一社会信用代码，验证唯一性
        if kehu_data.tongyi_shehui_xinyong_daima and kehu_data.tongyi_shehui_xinyong_daima != kehu.tongyi_shehui_xinyong_daima:
            existing_kehu = self.db.query(Kehu).filter(
                Kehu.tongyi_shehui_xinyong_daima == kehu_data.tongyi_shehui_xinyong_daima,
                Kehu.id != kehu_id,
                Kehu.is_deleted == "N"
            ).first()
            
            if existing_kehu:
                raise HTTPException(status_code=400, detail="统一社会信用代码已存在")
        
        # 更新字段
        update_data = kehu_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kehu, field, value)
        
        kehu.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(kehu)
        
        return KehuResponse.model_validate(kehu)
    
    def delete_kehu(self, kehu_id: str, deleted_by: str) -> bool:
        """删除客户（软删除）"""
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 软删除
        kehu.is_deleted = "Y"
        kehu.updated_by = deleted_by
        
        self.db.commit()
        
        return True
    
    def update_kehu_status(self, kehu_id: str, new_status: str, updated_by: str) -> KehuResponse:
        """更新客户状态"""
        kehu = self.db.query(Kehu).filter(
            Kehu.id == kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not kehu:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 验证状态值
        allowed_statuses = ["active", "renewing", "terminated"]
        if new_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"无效的客户状态: {new_status}")
        
        kehu.kehu_zhuangtai = new_status
        kehu.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(kehu)
        
        return KehuResponse.model_validate(kehu)
