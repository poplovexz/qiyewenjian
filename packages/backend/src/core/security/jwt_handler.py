"""
JWT 令牌处理器
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ...models import Yonghu


# JWT 安全方案
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT 令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证 JWT 令牌
    
    Args:
        token: JWT 令牌字符串
        
    Returns:
        解码后的数据
        
    Raises:
        HTTPException: 令牌无效时抛出异常
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        yonghu_ming: str = payload.get("sub")
        if yonghu_ming is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Yonghu:
    """
    获取当前用户
    
    Args:
        credentials: HTTP 认证凭据
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 用户不存在或令牌无效时抛出异常
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    yonghu_ming: str = payload.get("sub")
    
    user = db.query(Yonghu).filter(
        Yonghu.yonghu_ming == yonghu_ming,
        Yonghu.is_deleted == "N"
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.zhuangtai != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def create_refresh_token(yonghu_ming: str) -> str:
    """
    创建刷新令牌
    
    Args:
        yonghu_ming: 用户名
        
    Returns:
        刷新令牌字符串
    """
    data = {"sub": yonghu_ming, "type": "refresh"}
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return create_access_token(data, expires_delta)
