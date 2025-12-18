"""
认证服务
"""
from datetime import datetime
from typing import Optional, List, Set
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Yonghu, Jiaose, YonghuJiaose
from core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    get_user_permissions
)
from core.config import settings
from schemas.yonghu_guanli import LoginRequest, TokenResponse, UserInfo


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, yonghu_ming: str, mima: str) -> Optional[Yonghu]:
        """
        验证用户身份
        
        Args:
            yonghu_ming: 用户名
            mima: 密码
            
        Returns:
            用户对象或 None
        """
        user = self.db.query(Yonghu).filter(
            Yonghu.yonghu_ming == yonghu_ming,
            Yonghu.is_deleted == "N"
        ).first()
        
        if not user:
            return None
        
        if not verify_password(mima, user.mima):
            return None
        
        return user
    
    def login(self, login_data: LoginRequest) -> dict:
        """
        用户登录
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            登录响应数据
            
        Raises:
            HTTPException: 登录失败时抛出异常
        """
        # 验证用户身份
        user = self.authenticate_user(login_data.yonghu_ming, login_data.mima)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if user.zhuangtai != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已被禁用"
            )
        
        # 更新登录信息
        user.zuihou_denglu = datetime.utcnow()

        try:
            login_count = int(user.denglu_cishu or 0)
        except (TypeError, ValueError):
            login_count = 0

        user.denglu_cishu = str(login_count + 1)
        self.db.commit()
        
        # 生成令牌
        access_token = create_access_token(
            data={"sub": user.yonghu_ming}
        )
        refresh_token = create_refresh_token(user.yonghu_ming)
        
        # 获取用户角色和权限
        user_roles = self.get_user_roles(user)
        user_permissions = list(get_user_permissions(user, self.db))
        
        # 构建用户信息
        user_info = UserInfo(
            id=str(user.id),
            yonghu_ming=user.yonghu_ming,
            youxiang=user.youxiang,
            xingming=user.xingming,
            shouji=user.shouji,
            zhuangtai=user.zhuangtai,
            zuihou_denglu=user.zuihou_denglu,
            denglu_cishu=user.denglu_cishu,
            roles=user_roles,
            permissions=user_permissions
        )
        
        # 构建令牌信息
        token_info = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return {
            "message": "登录成功",
            "user": user_info,
            "token": token_info
        }
    
    def get_user_roles(self, user: Yonghu) -> List[str]:
        """
        获取用户角色列表
        
        Args:
            user: 用户对象
            
        Returns:
            角色编码列表
        """
        user_roles = self.db.query(YonghuJiaose).join(Jiaose).filter(
            YonghuJiaose.yonghu_id == user.id,
            Jiaose.zhuangtai == "active",
            Jiaose.is_deleted == "N"
        ).all()
        
        roles = []
        for user_role in user_roles:
            role = self.db.query(Jiaose).filter(Jiaose.id == user_role.jiaose_id).first()
            if role:
                roles.append(role.jiaose_bianma)
        
        return roles
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的令牌信息
            
        Raises:
            HTTPException: 刷新令牌无效时抛出异常
        """
        from core.security.jwt_handler import verify_token
        
        try:
            payload = verify_token(refresh_token)
            
            # 检查令牌类型
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            yonghu_ming = payload.get("sub")
            
            # 验证用户是否存在且有效
            user = self.db.query(Yonghu).filter(
                Yonghu.yonghu_ming == yonghu_ming,
                Yonghu.zhuangtai == "active",
                Yonghu.is_deleted == "N"
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在或已被禁用"
                )
            
            # 生成新的令牌
            new_access_token = create_access_token(
                data={"sub": user.yonghu_ming}
            )
            new_refresh_token = create_refresh_token(user.yonghu_ming)
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌无效"
            )
    
    def change_password(self, user: Yonghu, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            是否修改成功
            
        Raises:
            HTTPException: 旧密码错误时抛出异常
        """
        # 验证旧密码
        if not verify_password(old_password, user.mima):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        
        # 更新密码
        user.mima = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
