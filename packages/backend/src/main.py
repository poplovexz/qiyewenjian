"""
代理记账营运内部系统 - 主应用入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from core.config import settings
from api.api_v1.api import api_router
from core.redis_client import redis_client
from core.cache_decorator import warm_up_cache
from core.logging import setup_logging, get_logger
from core.middleware import RequestLoggingMiddleware, RateLimitMiddleware
from core.exceptions import BaseCustomException
from core.exception_handlers import (
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from core.sentry import init_sentry

# 初始化 Sentry 错误监控（需要在其他模块之前初始化）
init_sentry()

# 初始化日志系统
setup_logging(
    level=settings.LOG_LEVEL,
    json_format=settings.LOG_JSON_FORMAT or not settings.DEBUG,  # 生产环境默认 JSON 格式
    log_file=settings.LOG_FILE
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 启动代理记账营运内部系统...")

    # 连接Redis（可选）
    try:
        await redis_client.connect()
        logger.info("✅ Redis连接成功")
        # 缓存预热
        if redis_client.is_connected:
            await warm_up_cache()
            logger.info("✅ 缓存预热完成")
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败，系统将在无缓存模式下运行: {e}")
        # 确保Redis客户端状态正确
        redis_client.is_connected = False

    # 加载事件处理器
    try:
        from services.xiansuo_guanli.baojia_event_handlers import register_baojia_event_handlers
        register_baojia_event_handlers()
        logger.info("✅ 事件处理器加载完成")
    except Exception as e:
        logger.warning(f"⚠️ 事件处理器加载失败: {e}")

    logger.info("✅ 系统启动完成")

    yield

    # 关闭时
    logger.info("🔄 正在关闭系统...")
    try:
        if redis_client.is_connected:
            await redis_client.disconnect()
            logger.info("✅ Redis连接已关闭")
    except Exception as e:
        logger.warning(f"⚠️ Redis关闭时出现错误: {e}")
    logger.info("✅ 系统已关闭")

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="0.1.0",
    description="代理记账营运内部系统后端 API",
    lifespan=lifespan
)

# 设置 CORS
default_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://172.22.61.135:5174",
    "http://10.255.255.254:5174"
]

configured_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

# 去重并保留顺序，确保默认值始终生效
allow_origins = []
for origin in configured_origins + default_cors_origins:
    if origin and origin not in allow_origins:
        allow_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|172\.22\.61\.135|10\.255\.255\.254)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 添加请求日志中间件（在 CORS 之后添加，确保 CORS 优先处理）
app.add_middleware(RequestLoggingMiddleware)

# 添加全局限流中间件（可通过配置启用/禁用）
if getattr(settings, 'RATE_LIMIT_ENABLED', True):
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 200),
        window_seconds=getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)
    )

# 注册统一异常处理器
app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 配置静态文件服务
UPLOAD_DIR = "/var/www/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
async def root() -> dict[str, str]:
    """根路径健康检查"""
    return {"message": "代理记账营运内部系统 API 服务正常运行"}


@app.get("/health")
async def health_check() -> dict:
    """增强版健康检查端点"""
    from core.monitoring import HealthChecker
    return await HealthChecker.full_check()


@app.get("/health/live")
async def liveness_probe() -> dict:
    """Kubernetes 存活探针"""
    from core.monitoring import HealthChecker
    return await HealthChecker.liveness_check()


@app.get("/health/ready")
async def readiness_probe() -> dict:
    """Kubernetes 就绪探针"""
    from core.monitoring import HealthChecker
    return await HealthChecker.readiness_check()


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus 格式指标导出"""
    from fastapi.responses import PlainTextResponse
    from core.monitoring import metrics_collector

    return PlainTextResponse(
        content=metrics_collector.to_prometheus_format(),
        media_type="text/plain; charset=utf-8"
    )


if __name__ == "__main__":
    import uvicorn
    # 安全修复：从环境变量读取 host，默认 127.0.0.1
    # 生产环境通过反向代理访问，不需要绑定 0.0.0.0
    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    uvicorn.run(
        "main:app",
        host=host,
        port=8000,
        reload=True,
        reload_dirs=["."]
    )
