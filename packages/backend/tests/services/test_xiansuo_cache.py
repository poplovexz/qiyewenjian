"""线索来源缓存相关测试"""
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.core.redis_client import redis_client
from src.models.xiansuo_guanli import XiansuoLaiyuan
from src.services.xiansuo_guanli import XiansuoLaiyuanService


@pytest.mark.asyncio
async def test_get_active_laiyuan_list_cache_miss(db_session, monkeypatch):
    """缓存未命中时应从数据库加载并写入缓存"""
    laiyuan = XiansuoLaiyuan(
        laiyuan_mingcheng="渠道A",
        laiyuan_bianma="channel_a",
        laiyuan_leixing="online",
        zhuangtai="active",
    )
    db_session.add(laiyuan)
    db_session.commit()

    monkeypatch.setattr(redis_client, "_connected", True)
    monkeypatch.setattr(redis_client, "redis", object())
    get_mock = AsyncMock(return_value=None)
    set_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(redis_client, "get", get_mock)
    monkeypatch.setattr(redis_client, "set", set_mock)

    service = XiansuoLaiyuanService(db_session)
    result = await service.get_active_laiyuan_list()

    assert len(result) == 1
    assert result[0].laiyuan_bianma == "channel_a"
    get_mock.assert_awaited_once()
    set_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_active_laiyuan_list_cache_hit(db_session, monkeypatch):
    """缓存命中时应直接返回缓存数据并跳过数据库访问"""
    monkeypatch.setattr(redis_client, "_connected", True)
    monkeypatch.setattr(redis_client, "redis", object())
    cached_payload = [
        {
            "id": "cached-id",
            "laiyuan_mingcheng": "缓存渠道",
            "laiyuan_bianma": "cached",
            "laiyuan_leixing": "offline",
            "huoqu_chengben": 10.0,
            "xiansuo_shuliang": 5,
            "zhuanhua_shuliang": 2,
            "zhuanhua_lv": 40.0,
            "zhuangtai": "active",
            "paixu": 1,
            "miaoshu": "from cache",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
    ]

    get_mock = AsyncMock(return_value=cached_payload)
    set_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(redis_client, "get", get_mock)
    monkeypatch.setattr(redis_client, "set", set_mock)

    service = XiansuoLaiyuanService(db_session)
    result = await service.get_active_laiyuan_list()

    assert len(result) == 1
    assert result[0].laiyuan_bianma == "cached"
    get_mock.assert_awaited_once()
    set_mock.assert_not_awaited()
