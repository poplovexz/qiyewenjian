"""
线索管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional

from ..utils import _paginate

router = APIRouter(prefix="/api/v1", tags=["线索管理"])


@router.get("/lead-sources/active")
async def get_active_lead_sources():
    """获取活跃的线索来源"""
    return [
        {"id": "1", "mingcheng": "网站咨询", "zhuangtai": "active"},
        {"id": "2", "mingcheng": "电话咨询", "zhuangtai": "active"},
        {"id": "3", "mingcheng": "推荐", "zhuangtai": "active"}
    ]


@router.get("/lead-statuses/active")
async def get_active_lead_statuses():
    """获取活跃的线索状态"""
    return [
        {"id": "1", "mingcheng": "新线索", "zhuangtai": "active"},
        {"id": "2", "mingcheng": "跟进中", "zhuangtai": "active"},
        {"id": "3", "mingcheng": "已成交", "zhuangtai": "active"},
        {"id": "4", "mingcheng": "已失效", "zhuangtai": "active"}
    ]


@router.get("/leads/")
async def get_leads_list(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    xiansuo_zhuangtai: Optional[str] = None,
    laiyuan_id: Optional[str] = None,
    zhiliang_pinggu: Optional[str] = None
):
    """获取线索列表"""
    # 模拟线索数据
    leads_data = [
        {
            "id": "1",
            "kehu_mingcheng": "测试客户1",
            "lianxi_ren": "张三",
            "lianxi_dianhua": "13800138000",
            "xiansuo_zhuangtai": "新线索",
            "laiyuan_mingcheng": "网站咨询",
            "zhiliang_pinggu": "高",
            "created_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": "2",
            "kehu_mingcheng": "测试客户2",
            "lianxi_ren": "李四",
            "lianxi_dianhua": "13800138001",
            "xiansuo_zhuangtai": "跟进中",
            "laiyuan_mingcheng": "电话咨询",
            "zhiliang_pinggu": "中",
            "created_at": "2024-01-14T09:00:00Z"
        }
    ]

    filtered = leads_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("kehu_mingcheng", "").lower()
            or keyword in item.get("lianxi_ren", "").lower()
            or keyword in item.get("lianxi_dianhua", "").lower()
        ]

    if xiansuo_zhuangtai:
        filtered = [item for item in filtered if item.get("xiansuo_zhuangtai") == xiansuo_zhuangtai]

    if laiyuan_id:
        # 简单映射
        laiyuan_map = {"1": "网站咨询", "2": "电话咨询", "3": "推荐"}
        laiyuan_name = laiyuan_map.get(laiyuan_id)
        if laiyuan_name:
            filtered = [item for item in filtered if item.get("laiyuan_mingcheng") == laiyuan_name]

    if zhiliang_pinggu:
        filtered = [item for item in filtered if item.get("zhiliang_pinggu") == zhiliang_pinggu]

    return _paginate(filtered, page, size)


@router.get("/lead-sources/")
async def get_lead_sources():
    """获取线索来源列表"""
    return {
        "items": [
            {"id": "1", "mingcheng": "网站咨询", "zhuangtai": "active"},
            {"id": "2", "mingcheng": "电话咨询", "zhuangtai": "active"},
            {"id": "3", "mingcheng": "推荐", "zhuangtai": "active"}
        ],
        "total": 3,
        "page": 1,
        "size": 20
    }


@router.get("/lead-quotes/xiansuo/{xiansuo_id}")
async def get_lead_quotes_by_xiansuo(xiansuo_id: str):
    """获取线索的报价列表"""
    return {
        "items": [
            {
                "id": "quote-1",
                "xiansuo_id": xiansuo_id,
                "baojia_bianhao": "BJ-2024-001",
                "baojia_zhuangtai": "draft",
                "zongjine": 5000.00,
                "created_at": "2024-01-15T10:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }
