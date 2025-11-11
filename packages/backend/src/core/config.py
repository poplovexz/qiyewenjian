"""
应用配置设置
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    
    APP_NAME: str = "代理记账营运内部系统"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30     # 30天
    
    # 数据库配置
    DATABASE_URL: PostgresDsn

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: str = ""

    # 缓存配置
    CACHE_DEFAULT_TTL: int = 900  # 15分钟
    CACHE_LONG_TTL: int = 86400   # 24小时
    CACHE_SHORT_TTL: int = 60     # 1分钟

    # CORS 配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """组装 CORS 源"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_URL:
            return self.REDIS_URL

        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        """配置类"""
        import os
        from pathlib import Path

        # 获取项目根目录（backend目录）
        backend_dir = Path(__file__).parent.parent.parent
        env_file = str(backend_dir / ".env")
        case_sensitive = True


settings = Settings()
