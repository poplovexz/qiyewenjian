"""
API 限流防护

支持多种限流策略：
- 滑动窗口限流（推荐，精确度高）
- 固定窗口限流（简单高效）
- 令牌桶限流（适合突发流量）

使用方式：
1. 装饰器方式: @rate_limit(max_requests=100, window_seconds=60)
2. 依赖注入: Depends(RateLimiter(max_requests=100, window_seconds=60))
"""
import time
from typing import Optional, Callable
from functools import wraps

from fastapi import Request

from core.redis_client import redis_client
from core.logging import get_logger
from core.exceptions import RateLimitException
from core.error_codes import ErrorCode

logger = get_logger(__name__)


class RateLimiter:
    """
    滑动窗口限流器

    Args:
        max_requests: 窗口内最大请求数
        window_seconds: 时间窗口（秒）
        key_prefix: 缓存键前缀
        key_func: 自定义限流键生成函数
    """

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        key_prefix: str = "rate_limit",
        key_func: Optional[Callable[[Request], str]] = None
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request: Request) -> str:
        """默认限流键：基于客户端 IP"""
        # 优先从代理头获取真实 IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.headers.get("X-Real-IP") or (
                request.client.host if request.client else "unknown"
            )
        return f"{self.key_prefix}:{client_ip}:{request.url.path}"

    async def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """
        检查请求是否被允许

        Returns:
            (is_allowed, rate_info)
            rate_info 包含: remaining, limit, reset_at
        """
        # Redis 不可用时，放行所有请求
        if not redis_client.is_connected:
            logger.warning("Redis 不可用，跳过限流检查")
            return True, {"remaining": -1, "limit": self.max_requests, "reset_at": 0}

        key = self.key_func(request)
        now = time.time()
        window_start = now - self.window_seconds

        try:
            # 使用 Redis Pipeline 执行滑动窗口限流
            pipe = redis_client.redis.pipeline()

            # 1. 移除窗口外的旧记录
            pipe.zremrangebyscore(key, 0, window_start)

            # 2. 获取当前窗口内的请求数
            pipe.zcard(key)

            # 3. 添加当前请求（使用时间戳作为 score 和 member）
            pipe.zadd(key, {str(now): now})

            # 4. 设置键过期时间
            pipe.expire(key, self.window_seconds + 1)

            results = await pipe.execute()
            current_count = results[1]  # zcard 结果

            # 计算剩余配额
            remaining = max(0, self.max_requests - current_count - 1)
            reset_at = int(now + self.window_seconds)

            rate_info = {
                "remaining": remaining,
                "limit": self.max_requests,
                "reset_at": reset_at,
                "window_seconds": self.window_seconds
            }

            if current_count >= self.max_requests:
                logger.warning(
                    f"限流触发: {key} ({current_count}/{self.max_requests})"
                )
                return False, rate_info

            return True, rate_info

        except Exception as e:
            logger.error(f"限流检查失败: {e}")
            # 出错时放行，避免影响正常服务
            return True, {"remaining": -1, "limit": self.max_requests, "reset_at": 0}

    async def __call__(self, request: Request) -> dict:
        """FastAPI 依赖注入接口"""
        is_allowed, rate_info = await self.is_allowed(request)

        # 添加限流信息到响应头（通过 request.state 传递）
        request.state.rate_limit_info = rate_info

        if not is_allowed:
            raise RateLimitException(
                ErrorCode.RATE_LIMIT_EXCEEDED,
                details={
                    "retry_after": rate_info.get("window_seconds", 60),
                    "limit": rate_info.get("limit"),
                }
            )

        return rate_info


# 预定义的限流器实例
default_limiter = RateLimiter(max_requests=100, window_seconds=60)
strict_limiter = RateLimiter(max_requests=10, window_seconds=60)
auth_limiter = RateLimiter(max_requests=5, window_seconds=60, key_prefix="auth_limit")


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_prefix: str = "rate_limit"
):
    """限流装饰器，用于路由函数"""
    limiter = RateLimiter(max_requests, window_seconds, key_prefix)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            # 从 kwargs 中获取 request
            if request is None:
                request = kwargs.get('request')
            if request is None:
                # 尝试从 args 中查找 Request 对象
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                await limiter(request)

            return await func(*args, **kwargs)
        return wrapper
    return decorator

