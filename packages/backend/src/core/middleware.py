"""
企业级中间件

包含：
- 请求日志中间件
- 请求追踪 ID 中间件
- 性能监控中间件
- 全局限流中间件
"""
import time
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from core.logging import (
    generate_request_id,
    set_request_context,
    clear_request_context,
    get_logger,
    request_id_var
)

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    功能：
    - 为每个请求生成唯一 Request ID
    - 记录请求开始和结束
    - 计算请求耗时
    - 在响应头中返回 X-Request-ID
    """

    # 不需要详细日志的路径
    SKIP_PATHS = {"/health", "/", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求头获取或生成 Request ID
        request_id = request.headers.get("X-Request-ID") or generate_request_id()

        # 获取用户 ID（如果已认证）
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)

        # 设置请求上下文
        set_request_context(
            request_id=request_id,
            user_id=user_id,
            request_path=request.url.path
        )

        # 记录请求开始
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)

        # 跳过健康检查等路径的详细日志
        should_log = path not in self.SKIP_PATHS

        if should_log:
            logger.info(
                f"请求开始: {method} {path}",
                extra={"extra_data": {
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("user-agent", "-")[:100]
                }}
            )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算耗时
            duration_ms = (time.perf_counter() - start_time) * 1000

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            # 收集请求指标
            try:
                from core.monitoring import metrics_collector
                metrics_collector.record_request(method, path, response.status_code, duration_ms)
            except Exception:
                pass  # 指标收集失败不影响请求处理

            # 记录请求完成
            if should_log:
                log_method = logger.info if response.status_code < 400 else logger.warning
                log_method(
                    f"请求完成: {method} {path} -> {response.status_code} ({duration_ms:.2f}ms)",
                    extra={"extra_data": {
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2)
                    }}
                )

            return response

        except Exception as e:
            # 计算耗时
            duration_ms = (time.perf_counter() - start_time) * 1000

            # 记录异常
            logger.error(
                f"请求异常: {method} {path} -> {type(e).__name__}: {str(e)[:200]}",
                exc_info=True,
                extra={"extra_data": {
                    "duration_ms": round(duration_ms, 2),
                    "exception_type": type(e).__name__
                }}
            )
            raise

        finally:
            # 清除请求上下文
            clear_request_context()

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """获取客户端真实 IP"""
        # 优先从代理头获取
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接连接的客户端
        if request.client:
            return request.client.host

        return "unknown"


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    性能监控中间件

    功能：
    - 记录慢请求（超过阈值）
    - 可扩展为 Prometheus 指标收集
    """

    SLOW_REQUEST_THRESHOLD_MS = 1000  # 1秒

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # 记录慢请求
        if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                f"慢请求警告: {request.method} {request.url.path} 耗时 {duration_ms:.2f}ms",
                extra={"extra_data": {
                    "threshold_ms": self.SLOW_REQUEST_THRESHOLD_MS,
                    "duration_ms": round(duration_ms, 2)
                }}
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    全局限流中间件

    对所有请求进行基础限流，保护服务器免受过载
    敏感接口可使用 RateLimiter 依赖进行更严格的限流
    """

    # 默认配置
    DEFAULT_MAX_REQUESTS = 200  # 每个 IP 每分钟最大请求数
    DEFAULT_WINDOW_SECONDS = 60

    # 不限流的路径
    SKIP_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json"}

    def __init__(
        self,
        app,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过不需要限流的路径
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # 延迟导入避免循环依赖
        from core.rate_limiter import RateLimiter

        limiter = RateLimiter(
            max_requests=self.max_requests,
            window_seconds=self.window_seconds,
            key_prefix="global_limit"
        )

        is_allowed, rate_info = await limiter.is_allowed(request)

        if not is_allowed:
            # 返回 429 响应
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "100004",
                        "message": "请求过于频繁，请稍后重试",
                        "request_id": request_id_var.get(),
                        "details": {
                            "retry_after": rate_info.get("window_seconds", 60),
                            "limit": rate_info.get("limit")
                        }
                    }
                },
                headers={
                    "Retry-After": str(rate_info.get("window_seconds", 60)),
                    "X-RateLimit-Limit": str(rate_info.get("limit", 0)),
                    "X-RateLimit-Remaining": str(rate_info.get("remaining", 0)),
                    "X-RateLimit-Reset": str(rate_info.get("reset_at", 0))
                }
            )

        response = await call_next(request)

        # 添加限流信息到响应头
        response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset_at", 0))

        return response
