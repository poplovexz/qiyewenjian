"""
客户管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from uuid import uuid4

from ..data.customers import customers_data, find_customer, service_records_data, find_service_record
from ..utils import _paginate, _now_iso

# 客户管理路由
customer_router = APIRouter(prefix="/api/v1/customers", tags=["客户管理"])

# 服务记录路由
service_record_router = APIRouter(prefix="/api/v1/service-records", tags=["服务记录"])


# ==================== 客户管理接口 ====================

@customer_router.get("/")
async def list_customers(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    kehu_zhuangtai: Optional[str] = None,
    fuwu_kaishi_start: Optional[str] = None,
    fuwu_kaishi_end: Optional[str] = None
):
    """获取客户列表"""
    filtered = customers_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("gongsi_mingcheng", "").lower()
            or keyword in item.get("tongyi_shehui_xinyong_daima", "").lower()
            or keyword in item.get("faren_xingming", "").lower()
            or keyword in item.get("lianxi_ren", "").lower()
        ]

    if kehu_zhuangtai:
        filtered = [item for item in filtered if item.get("kehu_zhuangtai") == kehu_zhuangtai]

    if fuwu_kaishi_start:
        filtered = [item for item in filtered if item.get("fuwu_kaishi", "") >= fuwu_kaishi_start]

    if fuwu_kaishi_end:
        filtered = [item for item in filtered if item.get("fuwu_kaishi", "") <= fuwu_kaishi_end]

    return _paginate(filtered, page, size)


@customer_router.get("/{customer_id}")
async def get_customer_detail(customer_id: str):
    """获取客户详情"""
    customer = find_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@customer_router.post("/")
async def create_customer(payload: Dict):
    """创建客户"""
    if not payload.get("gongsi_mingcheng"):
        raise HTTPException(status_code=400, detail="公司名称不能为空")

    new_customer = {
        "id": str(uuid4()),
        "gongsi_mingcheng": payload.get("gongsi_mingcheng"),
        "tongyi_shehui_xinyong_daima": payload.get("tongyi_shehui_xinyong_daima"),
        "yingyezhizhao_haoma": payload.get("yingyezhizhao_haoma"),
        "faren_xingming": payload.get("faren_xingming"),
        "faren_shenfenzheng": payload.get("faren_shenfenzheng"),
        "zhuce_dizhi": payload.get("zhuce_dizhi"),
        "jingying_dizhi": payload.get("jingying_dizhi"),
        "lianxi_ren": payload.get("lianxi_ren"),
        "lianxi_dianhua": payload.get("lianxi_dianhua"),
        "shouji_haoma": payload.get("shouji_haoma"),
        "youxiang_dizhi": payload.get("youxiang_dizhi"),
        "kehu_zhuangtai": payload.get("kehu_zhuangtai", "active"),
        "fuwu_kaishi": payload.get("fuwu_kaishi"),
        "fuwu_jieshu": payload.get("fuwu_jieshu"),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    customers_data.append(new_customer)
    return new_customer


@customer_router.put("/{customer_id}")
async def update_customer(customer_id: str, payload: Dict):
    """更新客户信息"""
    customer = find_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    for field in ["gongsi_mingcheng", "tongyi_shehui_xinyong_daima", "yingyezhizhao_haoma",
                  "faren_xingming", "faren_shenfenzheng", "zhuce_dizhi", "jingying_dizhi",
                  "lianxi_ren", "lianxi_dianhua", "shouji_haoma", "youxiang_dizhi",
                  "kehu_zhuangtai", "fuwu_kaishi", "fuwu_jieshu", "beizhu"]:
        if field in payload and payload[field] is not None:
            customer[field] = payload[field]

    customer["updated_at"] = _now_iso()
    return customer


@customer_router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    """删除客户"""
    customer = find_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    customers_data.remove(customer)
    return {"message": "客户删除成功"}


@customer_router.patch("/{customer_id}/status")
async def update_customer_status(customer_id: str, new_status: str):
    """更新客户状态"""
    customer = find_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    customer["kehu_zhuangtai"] = new_status
    customer["updated_at"] = _now_iso()
    return customer


@customer_router.get("/statistics/overview")
async def get_customer_statistics():
    """获取客户统计信息"""
    total_customers = len(customers_data)
    
    # 按状态统计
    status_stats = {}
    for customer in customers_data:
        status = customer.get("kehu_zhuangtai", "unknown")
        status_stats[status] = status_stats.get(status, 0) + 1
    
    return {
        "total_customers": total_customers,
        "active_customers": status_stats.get("active", 0),
        "renewing_customers": status_stats.get("renewing", 0),
        "terminated_customers": status_stats.get("terminated", 0),
        "monthly_new_customers": 2,  # 模拟数据
        "status_distribution": status_stats
    }


@customer_router.post("/batch/status")
async def batch_update_customer_status(customer_ids: List[str], new_status: str):
    """批量更新客户状态"""
    updated_count = 0
    for customer_id in customer_ids:
        customer = find_customer(customer_id)
        if customer:
            customer["kehu_zhuangtai"] = new_status
            customer["updated_at"] = _now_iso()
            updated_count += 1
    
    return {
        "updated_count": updated_count,
        "total_requested": len(customer_ids),
        "new_status": new_status
    }


@customer_router.post("/batch/delete")
async def batch_delete_customers(customer_ids: List[str]):
    """批量删除客户"""
    deleted_count = 0
    for customer_id in customer_ids:
        customer = find_customer(customer_id)
        if customer:
            customers_data.remove(customer)
            deleted_count += 1
    
    return {
        "deleted_count": deleted_count,
        "total_requested": len(customer_ids)
    }


@customer_router.post("/search/advanced")
async def advanced_search_customers(search_params: Dict):
    """高级搜索客户"""
    filtered = customers_data

    # 应用各种搜索条件
    if search_params.get("gongsi_mingcheng"):
        keyword = search_params["gongsi_mingcheng"].lower()
        filtered = [item for item in filtered if keyword in item.get("gongsi_mingcheng", "").lower()]

    if search_params.get("tongyi_shehui_xinyong_daima"):
        filtered = [item for item in filtered 
                   if search_params["tongyi_shehui_xinyong_daima"] in item.get("tongyi_shehui_xinyong_daima", "")]

    if search_params.get("faren_xingming"):
        keyword = search_params["faren_xingming"].lower()
        filtered = [item for item in filtered if keyword in item.get("faren_xingming", "").lower()]

    if search_params.get("kehu_zhuangtai"):
        filtered = [item for item in filtered if item.get("kehu_zhuangtai") == search_params["kehu_zhuangtai"]]

    # 日期范围过滤
    if search_params.get("fuwu_kaishi_start"):
        filtered = [item for item in filtered if item.get("fuwu_kaishi", "") >= search_params["fuwu_kaishi_start"]]

    if search_params.get("fuwu_kaishi_end"):
        filtered = [item for item in filtered if item.get("fuwu_kaishi", "") <= search_params["fuwu_kaishi_end"]]

    if search_params.get("created_start"):
        filtered = [item for item in filtered if item.get("created_at", "") >= search_params["created_start"]]

    if search_params.get("created_end"):
        filtered = [item for item in filtered if item.get("created_at", "") <= search_params["created_end"]]

    page = search_params.get("page", 1)
    size = search_params.get("size", 20)
    
    return _paginate(filtered, page, size)


# ==================== 服务记录接口 ====================

@service_record_router.get("/")
async def list_service_records(
    page: int = 1,
    size: int = 20,
    kehu_id: Optional[str] = None,
    fuwu_leixing: Optional[str] = None,
    fuwu_zhuangtai: Optional[str] = None
):
    """获取服务记录列表"""
    filtered = service_records_data

    if kehu_id:
        filtered = [item for item in filtered if item.get("kehu_id") == kehu_id]

    if fuwu_leixing:
        filtered = [item for item in filtered if item.get("fuwu_leixing") == fuwu_leixing]

    if fuwu_zhuangtai:
        filtered = [item for item in filtered if item.get("fuwu_zhuangtai") == fuwu_zhuangtai]

    return _paginate(filtered, page, size)


@service_record_router.get("/{record_id}")
async def get_service_record_detail(record_id: str):
    """获取服务记录详情"""
    record = find_service_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="服务记录不存在")
    return record


@service_record_router.post("/")
async def create_service_record(payload: Dict):
    """创建服务记录"""
    if not payload.get("kehu_id") or not payload.get("fuwu_leixing"):
        raise HTTPException(status_code=400, detail="客户ID和服务类型不能为空")

    # 验证客户是否存在
    customer = find_customer(payload["kehu_id"])
    if not customer:
        raise HTTPException(status_code=400, detail="客户不存在")

    new_record = {
        "id": str(uuid4()),
        "kehu_id": payload.get("kehu_id"),
        "kehu_mingcheng": customer.get("gongsi_mingcheng"),
        "fuwu_leixing": payload.get("fuwu_leixing"),
        "fuwu_neirong": payload.get("fuwu_neirong"),
        "fuwu_riqi": payload.get("fuwu_riqi"),
        "fuwu_zhuangtai": payload.get("fuwu_zhuangtai", "planned"),
        "fuwu_renyuan": payload.get("fuwu_renyuan"),
        "fuwu_shichang": payload.get("fuwu_shichang", 0.0),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    service_records_data.append(new_record)
    return new_record


@service_record_router.put("/{record_id}")
async def update_service_record(record_id: str, payload: Dict):
    """更新服务记录"""
    record = find_service_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="服务记录不存在")

    for field in ["fuwu_leixing", "fuwu_neirong", "fuwu_riqi", "fuwu_zhuangtai",
                  "fuwu_renyuan", "fuwu_shichang", "beizhu"]:
        if field in payload and payload[field] is not None:
            record[field] = payload[field]

    record["updated_at"] = _now_iso()
    return record


@service_record_router.delete("/{record_id}")
async def delete_service_record(record_id: str):
    """删除服务记录"""
    record = find_service_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="服务记录不存在")
    
    service_records_data.remove(record)
    return {"message": "服务记录删除成功"}
