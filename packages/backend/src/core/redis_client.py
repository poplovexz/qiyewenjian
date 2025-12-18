"""Redis 客户端管理"""
import hashlib
import json
import logging
from typing import Any, List, Optional

import redis.asyncio as redis

from core.config import settings


logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端类"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            self.redis = redis.from_url(
                settings.get_redis_url(),
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            await self.redis.ping()
            self._connected = True
            logger.info(
                "Redis connection established (%s:%s)",
                settings.REDIS_HOST,
                settings.REDIS_PORT,
            )
        except Exception as e:
            logger.warning("Redis connection failed: %s", e)
            logger.warning("Cache disabled, system will operate without Redis")
            logger.info(
                "Redis configuration host=%s port=%s", settings.REDIS_HOST, settings.REDIS_PORT
            )
            self._connected = False
            self.redis = None

    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("Redis connection closed")
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self.redis is not None
    
    async def get(self, key: str) -> Any:
        """获取缓存数据"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip GET for key '%s'", key)
            return None

        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning("Redis GET failed for key '%s': %s", key, e)
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存数据"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip SET for key '%s'", key)
            return False

        try:
            # 序列化数据 - 处理Pydantic模型
            if hasattr(value, 'model_dump'):
                # 单个Pydantic模型
                data = json.dumps(value.model_dump(), ensure_ascii=False, default=str)
            elif isinstance(value, list) and value and hasattr(value[0], 'model_dump'):
                # Pydantic模型列表
                data = json.dumps([item.model_dump() for item in value], ensure_ascii=False, default=str)
            else:
                # 普通数据
                data = json.dumps(value, ensure_ascii=False, default=str)

            if ttl:
                result = await self.redis.setex(key, ttl, data)
            else:
                result = await self.redis.set(key, data)

            return bool(result)
        except Exception as e:
            logger.warning("Redis SET failed for key '%s': %s", key, e)
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip DELETE for key '%s'", key)
            return False

        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning("Redis DELETE failed for key '%s': %s", key, e)
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有键"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip pattern delete for '%s'", pattern)
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                result = await self.redis.delete(*keys)
                return int(result)
            return 0
        except Exception as e:
            logger.warning("Redis delete pattern '%s' failed: %s", pattern, e)
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected:
            return False

        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.warning("Redis EXISTS failed for key '%s': %s", key, e)
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip EXPIRE for key '%s'", key)
            return False

        try:
            result = await self.redis.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.warning("Redis EXPIRE failed for key '%s': %s", key, e)
            return False
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        if not self.is_connected:
            return -1

        try:
            result = await self.redis.ttl(key)
            return int(result)
        except Exception as e:
            logger.warning("Redis TTL failed for key '%s': %s", key, e)
            return -1
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的所有键"""
        if not self.is_connected:
            return []

        try:
            keys = await self.redis.keys(pattern)
            return list(keys)
        except Exception as e:
            logger.warning("Redis KEYS failed for pattern '%s': %s", pattern, e)
            return []
    
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not self.is_connected:
            logger.warning("Redis unavailable, skip FLUSHDB")
            return False

        try:
            result = await self.redis.flushdb()
            return bool(result)
        except Exception as e:
            logger.warning("Redis FLUSHDB failed: %s", e)
            return False
    
    async def info(self) -> dict:
        """获取Redis服务器信息"""
        if not self.is_connected:
            return {}

        try:
            info = await self.redis.info()
            return dict(info)
        except Exception as e:
            logger.warning("Redis INFO failed: %s", e)
            return {}
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        if args or kwargs:
            # 将参数转换为字符串并生成哈希
            # 安全修复：MD5 用于缓存键生成，不用于安全目的
            params_str = str(args) + str(sorted(kwargs.items()))
            params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:8]
            return f"{prefix}:{params_hash}"
        else:
            return prefix


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: int = settings.CACHE_DEFAULT_TTL,
        *args,
        **kwargs
    ) -> Any:
        """获取缓存或设置缓存"""
        # 尝试从缓存获取
        cached_data = await self.redis.get(key)
        if cached_data is not None:
            logger.info("CacheManager hit for key '%s'", key)
            return cached_data
        
        # 缓存未命中，执行获取函数
        logger.debug("CacheManager miss for key '%s'", key)
        try:
            if args or kwargs:
                data = await fetch_func(*args, **kwargs)
            else:
                data = await fetch_func()
            
            # 存储到缓存
            await self.redis.set(key, data, ttl)
            logger.info("CacheManager stored key '%s' (ttl=%s)", key, ttl)
            
            return data
        except Exception as e:
            logger.warning("CacheManager fetch failed for key '%s': %s", key, e)
            raise

    async def invalidate_pattern(self, pattern: str) -> int:
        """使匹配模式的缓存失效"""
        count = await self.redis.delete_pattern(pattern)
        if count > 0:
            logger.info("CacheManager invalidated pattern '%s' (%s keys)", pattern, count)
        return count
    
    async def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        if not self.redis.is_connected:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis.info()
            keys_count = len(await self.redis.keys("*"))
            
            return {
                "status": "connected",
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": keys_count,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> str:
        """计算缓存命中率"""
        total = hits + misses
        if total == 0:
            return "0%"
        
        hit_rate = (hits / total) * 100
        return f"{hit_rate:.2f}%"


# 全局Redis客户端实例
redis_client = RedisClient()
cache_manager = CacheManager(redis_client)


# 缓存键常量
class CacheKeys:
    """缓存键常量"""
    
    # 线索管理相关
    XIANSUO_LAIYUAN_ACTIVE = "xiansuo:laiyuan:active"
    XIANSUO_ZHUANGTAI_ACTIVE = "xiansuo:zhuangtai:active"
    XIANSUO_LIST = "xiansuo:list"
    XIANSUO_DETAIL = "xiansuo:detail"
    XIANSUO_STATISTICS = "xiansuo:statistics"
    
    # 用户权限相关
    USER_PERMISSIONS = "user:permissions"
    ROLE_PERMISSIONS = "role:permissions"
    USER_ROLES = "user:roles"
    
    # 系统相关
    ONLINE_USERS = "system:online_users"
    SYSTEM_CONFIG = "system:config"
