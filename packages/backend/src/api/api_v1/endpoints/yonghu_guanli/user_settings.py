"""
用户个人设置API端点
"""
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli.yonghu import Yonghu
from schemas.yonghu_guanli.user_settings_schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    PasswordChange,
    UserPreferences,
    UserPreferencesUpdate
)
from services.yonghu_guanli.user_settings_service import UserSettingsService


router = APIRouter()


@router.get("/me/profile", response_model=UserProfileResponse, summary="获取个人信息")
def get_my_profile(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的个人信息
    """
    service = UserSettingsService(db)
    return service.get_user_profile(current_user.id)


@router.put("/me/profile", response_model=UserProfileResponse, summary="更新个人信息")
def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的个人信息
    
    可更新字段：
    - xingming: 姓名
    - shouji: 手机号
    - youxiang: 邮箱
    """
    service = UserSettingsService(db)
    return service.update_user_profile(current_user.id, profile_update)


@router.put("/me/password", response_model=Dict[str, str], summary="修改密码")
def change_my_password(
    password_change: PasswordChange,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前登录用户的密码
    
    需要提供：
    - old_password: 旧密码
    - new_password: 新密码（至少6位）
    """
    service = UserSettingsService(db)
    return service.change_password(current_user.id, password_change)


@router.get("/me/preferences", response_model=UserPreferences, summary="获取个人偏好设置")
def get_my_preferences(
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的偏好设置
    
    包括：
    - email_notification: 邮件通知
    - sms_notification: 短信通知
    - system_notification: 系统消息通知
    """
    service = UserSettingsService(db)
    return service.get_user_preferences(current_user.id)


@router.put("/me/preferences", response_model=UserPreferences, summary="更新个人偏好设置")
def update_my_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: Yonghu = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的偏好设置
    
    可更新字段：
    - email_notification: 邮件通知
    - sms_notification: 短信通知
    - system_notification: 系统消息通知
    """
    service = UserSettingsService(db)
    return service.update_user_preferences(current_user.id, preferences_update)

