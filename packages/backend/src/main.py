"""
代理记账营运内部系统 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api.api_v1.api import api_router
from src.core.redis_client import redis_client
from src.core.cache_decorator import warm_up_cache, cache_health_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("🚀 启动代理记账营运内部系统...")

    # 连接Redis
    try:
        await redis_client.connect()
        # 缓存预热
        if redis_client.is_connected:
            await warm_up_cache()
    except Exception as e:
        print(f"⚠️ Redis连接失败，跳过缓存功能: {e}")

    # 加载事件处理器
    try:
        from src.services.xiansuo_guanli.baojia_event_handlers import register_baojia_event_handlers
        print("✅ 事件处理器加载完成")
        register_baojia_event_handlers()
    except Exception as e:
        print(f"⚠️ 事件处理器加载失败: {e}")

    print("✅ 系统启动完成")

    yield

    # 关闭时
    print("🔄 正在关闭系统...")
    await redis_client.disconnect()
    print("✅ 系统已关闭")

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="0.1.0",
    description="代理记账营运内部系统后端 API",
    lifespan=lifespan
)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
       
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict[str, str]:
    """根路径健康检查"""
    return {"message": "代理记账营运内部系统 API 服务正常运行"}


@app.get("/health")
async def health_check() -> dict:
    """健康检查端点"""
    from datetime import datetime

    cache_status = await cache_health_check()

    # 判断整体健康状态
    overall_status = "healthy"
    issues = []

    # 检查Redis状态
    redis_status = cache_status.get("status", "unknown")
    if redis_status != "healthy":
        issues.append("Redis连接异常 - 系统在无缓存模式下运行")
        if redis_status == "unhealthy":
            issues.append("建议检查Redis服务是否启动和配置是否正确")

    # 如果有问题但系统仍可运行，标记为degraded
    if issues:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": "proxy-accounting-backend",
        "timestamp": datetime.now().isoformat(),
        "issues": issues if issues else None,
        "cache": {
            **cache_status,
            "fallback_mode": redis_status != "healthy",
            "performance_impact": "可能影响响应速度" if redis_status != "healthy" else None
        }
    }
