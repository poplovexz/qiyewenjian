"""缓存装饰器"""
import functools
import logging
from typing import Any, Callable, Optional

from core.redis_client import CacheKeys, redis_client
from core.config import settings

logger = logging.getLogger(__name__)

def cache_result(
    key_prefix: str,
    ttl: int = settings.CACHE_DEFAULT_TTL,
    use_args: bool = True,
    key_func: Optional[Callable] = None
):
    """
    缓存结果装饰器
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
        use_args: 是否使用函数参数生成缓存键
        key_func: 自定义缓存键生成函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            elif use_args:
                cache_key = redis_client.generate_cache_key(key_prefix, *args, **kwargs)
            else:
                cache_key = key_prefix
            
            # 尝试从缓存获取
            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                logger.info("Cache hit for key '%s'", cache_key)
                return cached_result

            # 缓存未命中，执行原函数
            logger.debug("Cache miss for key '%s', executing %s", cache_key, func.__name__)
            result = await func(*args, **kwargs)

            # 存储到缓存
            success = await redis_client.set(cache_key, result, ttl)
            if success:
                logger.info(
                    "Cache populated for key '%s' (ttl=%s)", cache_key, ttl
                )
            else:
                logger.warning("Failed to persist cache for key '%s'", cache_key)

            return result
        return wrapper
    return decorator

def cache_invalidate(*patterns: str):
    """
    缓存失效装饰器
    在函数执行成功后清除指定模式的缓存
    
    Args:
        patterns: 要清除的缓存键模式
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 清除相关缓存
            for pattern in patterns:
                count = await redis_client.delete_pattern(pattern)
                if count > 0:
                    logger.info("Cache invalidated for pattern '%s' (%s keys)", pattern, count)

            return result
        return wrapper
    return decorator

def cache_key_generator(template: str):
    """
    缓存键生成器
    
    Args:
        template: 缓存键模板，支持参数替换
    """
    def key_func(*args, **kwargs):
        # 简单的模板替换
        key = template
        for i, arg in enumerate(args):
            key = key.replace(f"{{{i}}}", str(arg))
        
        for k, v in kwargs.items():
            key = key.replace(f"{{{k}}}", str(v))
        
        return key
    
    return key_func

# 预定义的缓存装饰器

def cache_xiansuo_laiyuan(ttl: int = settings.CACHE_LONG_TTL):
    """线索来源缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_key = CacheKeys.XIANSUO_LAIYUAN_ACTIVE

            # 尝试从缓存获取
            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                logger.info("Cache hit for key '%s'", cache_key)
                # 重新构造Pydantic模型
                from schemas.xiansuo_guanli.xiansuo_laiyuan_schemas import XiansuoLaiyuanResponse
                if isinstance(cached_result, list):
                    return [XiansuoLaiyuanResponse.model_validate(item) for item in cached_result]
                else:
                    return XiansuoLaiyuanResponse.model_validate(cached_result)

            # 缓存未命中，执行原函数
            logger.debug("Cache miss for key '%s', executing %s", cache_key, func.__name__)
            result = await func(*args, **kwargs)

            # 存储到缓存
            success = await redis_client.set(cache_key, result, ttl)
            if success:
                logger.info(
                    "Cache populated for key '%s' (ttl=%s)", cache_key, ttl
                )
            else:
                logger.warning("Failed to persist cache for key '%s'", cache_key)

            return result
        return wrapper
    return decorator

def cache_xiansuo_zhuangtai(ttl: int = settings.CACHE_LONG_TTL):
    """线索状态缓存装饰器"""
    return cache_result(CacheKeys.XIANSUO_ZHUANGTAI_ACTIVE, ttl, use_args=False)

def cache_xiansuo_list(ttl: int = settings.CACHE_DEFAULT_TTL):
    """线索列表缓存装饰器"""
    return cache_result(CacheKeys.XIANSUO_LIST, ttl, use_args=True)

def cache_xiansuo_detail(ttl: int = settings.CACHE_DEFAULT_TTL):
    """线索详情缓存装饰器"""
    return cache_result(
        CacheKeys.XIANSUO_DETAIL,
        ttl,
        key_func=cache_key_generator("xiansuo:detail:{0}")
    )

def cache_user_permissions(ttl: int = settings.CACHE_LONG_TTL):
    """用户权限缓存装饰器"""
    return cache_result(
        CacheKeys.USER_PERMISSIONS,
        ttl,
        key_func=cache_key_generator("user:permissions:{0}")
    )

def invalidate_xiansuo_cache():
    """清除线索相关缓存"""
    return cache_invalidate(
        "xiansuo:list:*",
        "xiansuo:statistics:*",
        "xiansuo:detail:*"
    )

def invalidate_xiansuo_laiyuan_cache():
    """清除线索来源缓存"""
    return cache_invalidate(
        "xiansuo:laiyuan:*"
    )

def invalidate_xiansuo_zhuangtai_cache():
    """清除线索状态缓存"""
    return cache_invalidate(
        "xiansuo:zhuangtai:*"
    )

# 缓存预热函数
async def warm_up_cache():
    """缓存预热"""
    logger.info("Starting cache warm up")

    try:
        # 简单的缓存预热，只测试Redis连接
        test_key = "cache_warmup_test"
        test_value = {"status": "warmup", "timestamp": "test"}

        # 测试Redis写入和读取
        success = await redis_client.set(test_key, test_value, 60)
        if success:
            cached_value = await redis_client.get(test_key)
            if cached_value == test_value:
                logger.info("Redis cache warm up succeeded")
                await redis_client.delete(test_key)
            else:
                logger.warning("Redis cache warm up read verification failed")
        else:
            logger.warning("Redis cache warm up write failed")

        logger.info("Cache warm up completed")

    except Exception as e:
        logger.warning("Cache warm up failed: %s", e)

# 缓存清理函数
async def clear_all_cache():
    """清除所有缓存"""
    logger.info("Clearing all cache keys")
    
    try:
        result = await redis_client.flushdb()
        if result:
            logger.info("Cache database cleared successfully")
        else:
            logger.warning("Cache database flush returned failure state")
        return result
    except Exception as e:
        logger.warning("Cache flush raised exception: %s", e)
        return False

# 缓存健康检查
async def cache_health_check() -> dict:
    """缓存健康检查"""
    try:
        if not redis_client.is_connected:
            return {
                "status": "unhealthy",
                "message": "Redis未连接"
            }
        
        # 测试基本操作
        test_key = "health_check_test"
        test_value = {"timestamp": "test"}
        
        # 测试写入
        write_success = await redis_client.set(test_key, test_value, 10)
        if not write_success:
            return {
                "status": "unhealthy",
                "message": "Redis写入测试失败"
            }
        
        # 测试读取
        read_value = await redis_client.get(test_key)
        if read_value != test_value:
            return {
                "status": "unhealthy",
                "message": "Redis读取测试失败"
            }
        
        # 清理测试数据
        await redis_client.delete(test_key)
        
        # 获取统计信息
        from core.redis_client import cache_manager
        stats = await cache_manager.get_cache_stats()
        
        return {
            "status": "healthy",
            "message": "Redis运行正常",
            "stats": stats
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"健康检查异常: {e}"
        }
