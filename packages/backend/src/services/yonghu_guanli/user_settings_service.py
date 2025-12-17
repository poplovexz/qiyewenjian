"""
用户个人设置服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.yonghu_guanli.yonghu import Yonghu
from models.yonghu_guanli.user_preferences import UserPreferences
from schemas.yonghu_guanli.user_settings_schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    PasswordChange,
    UserPreferences as UserPreferencesSchema,
    UserPreferencesUpdate
)
from core.security.password_handler import verify_password, get_password_hash


class UserSettingsService:
    """用户设置服务"""

    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: str) -> UserProfileResponse:
        """获取用户个人信息"""
        user = self.db.query(Yonghu).filter(
            Yonghu.id == user_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserProfileResponse.model_validate(user)
    
    def update_user_profile(
        self,
        user_id: str,
        profile_update: UserProfileUpdate
    ) -> UserProfileResponse:
        """更新用户个人信息"""
        user = self.db.query(Yonghu).filter(
            Yonghu.id == user_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        # 设置更新人
        user.updated_by = user_id
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return UserProfileResponse.model_validate(user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新用户信息失败: {str(e)}"
            )
    
    def change_password(
        self,
        user_id: str,
        password_change: PasswordChange
    ) -> Dict[str, str]:
        """修改密码"""
        user = self.db.query(Yonghu).filter(
            Yonghu.id == user_id,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码
        if not verify_password(password_change.old_password, user.mima):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )

        # 设置新密码
        user.mima = get_password_hash(password_change.new_password)
        user.updated_by = user_id
        
        try:
            self.db.commit()
            return {"message": "密码修改成功"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"修改密码失败: {str(e)}"
            )
    
    def get_user_preferences(self, user_id: str) -> UserPreferencesSchema:
        """获取用户偏好设置"""
        # 获取所有偏好设置
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id,
            UserPreferences.is_deleted == "N"
        ).all()
        
        # 转换为字典
        prefs_dict = {
            pref.preference_key: pref.preference_value == "true"
            for pref in preferences
        }
        
        # 返回默认值或已保存的值
        return UserPreferencesSchema(
            email_notification=prefs_dict.get("email_notification", True),
            sms_notification=prefs_dict.get("sms_notification", True),
            system_notification=prefs_dict.get("system_notification", True)
        )
    
    def update_user_preferences(
        self,
        user_id: str,
        preferences_update: UserPreferencesUpdate
    ) -> UserPreferencesSchema:
        """更新用户偏好设置"""
        update_data = preferences_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            # 查找或创建偏好设置
            pref = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id,
                UserPreferences.preference_key == key,
                UserPreferences.is_deleted == "N"
            ).first()
            
            if pref:
                # 更新现有偏好
                pref.preference_value = str(value).lower()
                pref.updated_by = user_id
            else:
                # 创建新偏好
                pref = UserPreferences(
                    user_id=user_id,
                    preference_key=key,
                    preference_value=str(value).lower(),
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(pref)
        
        try:
            self.db.commit()
            return self.get_user_preferences(user_id)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新用户偏好失败: {str(e)}"
            )

