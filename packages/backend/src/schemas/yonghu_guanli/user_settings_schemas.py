"""
用户个人设置相关的 Pydantic 模式
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class UserProfileResponse(BaseModel):
    """用户个人信息响应"""
    id: str
    yonghu_ming: str = Field(..., description="用户名")
    xingming: str = Field(..., description="姓名")
    shouji: Optional[str] = Field(None, description="手机号")
    youxiang: Optional[EmailStr] = Field(None, description="邮箱")
    zhuangtai: str = Field(..., description="状态")
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """更新用户个人信息"""
    xingming: Optional[str] = Field(None, min_length=1, max_length=50, description="姓名")
    shouji: Optional[str] = Field(None, max_length=20, description="手机号")
    youxiang: Optional[EmailStr] = Field(None, description="邮箱")
    
    @validator('shouji')
    def validate_shouji(cls, v):
        """验证手机号格式"""
        if v and not v.isdigit():
            raise ValueError('手机号只能包含数字')
        if v and len(v) != 11:
            raise ValueError('手机号必须是11位')
        return v

class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """验证新密码"""
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        return v

class UserPreferences(BaseModel):
    """用户偏好设置"""
    email_notification: bool = Field(True, description="邮件通知")
    sms_notification: bool = Field(True, description="短信通知")
    system_notification: bool = Field(True, description="系统消息通知")
    
    class Config:
        from_attributes = True

class UserPreferencesUpdate(BaseModel):
    """更新用户偏好设置"""
    email_notification: Optional[bool] = Field(None, description="邮件通知")
    sms_notification: Optional[bool] = Field(None, description="短信通知")
    system_notification: Optional[bool] = Field(None, description="系统消息通知")
