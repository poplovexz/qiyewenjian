"""Redis 连接验证脚本"""
import asyncio
import logging

from core.cache_decorator import warm_up_cache
from core.redis_client import redis_client


async def verify() -> int:
    """验证 Redis 连接并执行一次缓存预热"""
    await redis_client.connect()
    if not redis_client.is_connected:
        logging.warning("Redis 未连接，跳过缓存预热")
        return 1

    await warm_up_cache()
    await redis_client.disconnect()
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    exit_code = asyncio.run(verify())
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
