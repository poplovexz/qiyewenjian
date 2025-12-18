"""
监控指标与健康检查模块

功能：
- 增强版健康检查（数据库、Redis、系统资源）
- Prometheus 格式指标导出
- 应用性能监控指标收集
"""
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from core.logging import get_logger

logger = get_logger(__name__)


# ==================== 指标收集器 ====================

@dataclass
class MetricsCollector:
    """应用指标收集器"""
    
    # 请求计数器
    request_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # 请求耗时统计 (毫秒)
    request_duration: Dict[str, list] = field(default_factory=lambda: defaultdict(list))
    
    # 错误计数
    error_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # 活跃连接数
    active_connections: int = 0
    
    # 启动时间
    start_time: float = field(default_factory=time.time)
    
    # 最大保留的耗时样本数
    MAX_DURATION_SAMPLES = 1000
    
    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """记录请求指标"""
        key = f"{method}:{path}"
        self.request_count[key] += 1
        
        # 记录耗时
        durations = self.request_duration[key]
        durations.append(duration_ms)
        
        # 限制样本数量
        if len(durations) > self.MAX_DURATION_SAMPLES:
            self.request_duration[key] = durations[-self.MAX_DURATION_SAMPLES:]
        
        # 记录错误
        if status_code >= 400:
            error_key = f"{status_code}:{path}"
            self.error_count[error_key] += 1
    
    def get_request_stats(self, key: str) -> Dict[str, float]:
        """获取请求统计信息"""
        durations = self.request_duration.get(key, [])
        if not durations:
            return {"count": 0, "avg_ms": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0}
        
        sorted_d = sorted(durations)
        count = len(sorted_d)
        
        return {
            "count": self.request_count.get(key, 0),
            "avg_ms": round(sum(sorted_d) / count, 2),
            "p50_ms": round(sorted_d[int(count * 0.5)], 2),
            "p95_ms": round(sorted_d[int(count * 0.95)], 2) if count > 20 else 0,
            "p99_ms": round(sorted_d[int(count * 0.99)], 2) if count > 100 else 0,
        }
    
    def get_uptime_seconds(self) -> float:
        """获取运行时长（秒）"""
        return time.time() - self.start_time
    
    def to_prometheus_format(self) -> str:
        """导出 Prometheus 格式指标"""
        lines = []
        
        # 应用运行时长
        lines.append("# HELP app_uptime_seconds Application uptime in seconds")
        lines.append("# TYPE app_uptime_seconds gauge")
        lines.append(f"app_uptime_seconds {self.get_uptime_seconds():.2f}")
        
        # 活跃连接数
        lines.append("# HELP app_active_connections Current active connections")
        lines.append("# TYPE app_active_connections gauge")
        lines.append(f"app_active_connections {self.active_connections}")
        
        # 请求计数
        lines.append("# HELP http_requests_total Total HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for key, count in self.request_count.items():
            method, path = key.split(":", 1)
            lines.append(f'http_requests_total{{method="{method}",path="{path}"}} {count}')
        
        # 错误计数
        lines.append("# HELP http_errors_total Total HTTP errors")
        lines.append("# TYPE http_errors_total counter")
        for key, count in self.error_count.items():
            status, path = key.split(":", 1)
            lines.append(f'http_errors_total{{status="{status}",path="{path}"}} {count}')
        
        # 请求耗时
        lines.append("# HELP http_request_duration_ms HTTP request duration in milliseconds")
        lines.append("# TYPE http_request_duration_ms summary")
        for key in self.request_count.keys():
            stats = self.get_request_stats(key)
            method, path = key.split(":", 1)
            lines.append(f'http_request_duration_ms{{method="{method}",path="{path}",quantile="0.5"}} {stats["p50_ms"]}')
            lines.append(f'http_request_duration_ms{{method="{method}",path="{path}",quantile="0.95"}} {stats["p95_ms"]}')
            lines.append(f'http_request_duration_ms{{method="{method}",path="{path}",quantile="0.99"}} {stats["p99_ms"]}')
        
        return "\n".join(lines)


# 全局指标收集器
metrics_collector = MetricsCollector()


# ==================== 健康检查服务 ====================

class HealthChecker:
    """增强版健康检查服务"""

    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            from core.database import SessionLocal
            from sqlalchemy import text

            start = time.time()
            db = SessionLocal()
            try:
                result = db.execute(text("SELECT 1"))
                result.fetchone()
                latency_ms = (time.time() - start) * 1000

                # 获取连接池状态
                pool = db.get_bind().pool
                pool_status = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow()
                }

                return {
                    "status": "healthy" if latency_ms < 100 else "degraded",
                    "latency_ms": round(latency_ms, 2),
                    "pool": pool_status
                }
            finally:
                db.close()

        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """检查 Redis 连接"""
        try:
            from core.redis_client import redis_client

            if not redis_client.is_connected:
                return {"status": "unhealthy", "error": "未连接"}

            start = time.time()
            await redis_client.redis.ping()
            latency_ms = (time.time() - start) * 1000

            # 获取 Redis 信息
            info = await redis_client.info()

            return {
                "status": "healthy" if latency_ms < 50 else "degraded",
                "latency_ms": round(latency_ms, 2),
                "version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }

        except Exception as e:
            logger.error(f"Redis 健康检查失败: {e}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_system() -> Dict[str, Any]:
        """检查系统资源"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 判断状态
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "unhealthy"

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
            }

        except ImportError:
            return {"status": "unknown", "error": "psutil not installed"}
        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return {"status": "unknown", "error": str(e)}

    @classmethod
    async def full_check(cls) -> Dict[str, Any]:
        """执行完整健康检查"""
        start = time.time()

        # 并行执行所有检查
        db_task = asyncio.create_task(cls.check_database())
        redis_task = asyncio.create_task(cls.check_redis())
        system_task = asyncio.create_task(cls.check_system())

        db_result, redis_result, system_result = await asyncio.gather(
            db_task, redis_task, system_task
        )

        # 判断整体状态
        statuses = [
            db_result.get("status"),
            redis_result.get("status"),
            system_result.get("status")
        ]

        if "unhealthy" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return {
            "status": overall,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(metrics_collector.get_uptime_seconds(), 2),
            "checks": {
                "database": db_result,
                "redis": redis_result,
                "system": system_result
            },
            "check_duration_ms": round((time.time() - start) * 1000, 2)
        }

    @classmethod
    async def liveness_check(cls) -> Dict[str, Any]:
        """存活检查（Kubernetes liveness probe）"""
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat()
        }

    @classmethod
    async def readiness_check(cls) -> Dict[str, Any]:
        """就绪检查（Kubernetes readiness probe）"""
        db_result = await cls.check_database()

        is_ready = db_result.get("status") != "unhealthy"

        return {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "database": db_result.get("status")
        }

