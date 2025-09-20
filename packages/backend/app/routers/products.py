"""
产品管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from uuid import uuid4

from ..data.products import (
    product_categories_data, find_product_category,
    products_data, find_product
)
from ..utils import _paginate, _now_iso

# 产品分类路由
category_router = APIRouter(prefix="/api/v1/product-management/categories", tags=["产品分类"])

# 产品项目路由
product_router = APIRouter(prefix="/api/v1/product-management/products", tags=["产品项目"])


# ==================== 产品分类接口 ====================

@category_router.get("/")
async def list_product_categories(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    zhuangtai: Optional[str] = None
):
    """获取产品分类列表"""
    filtered = product_categories_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("fenlei_mingcheng", "").lower()
            or keyword in item.get("fenlei_bianma", "").lower()
            or keyword in item.get("miaoshu", "").lower()
        ]

    if zhuangtai:
        filtered = [item for item in filtered if item.get("zhuangtai") == zhuangtai]

    # 按排序字段排序
    filtered.sort(key=lambda x: x.get("paixu", 999))

    return _paginate(filtered, page, size)


@category_router.get("/options")
async def get_category_options(zhuangtai: Optional[str] = "active"):
    """获取产品分类选项（用于下拉框）"""
    filtered = product_categories_data
    
    if zhuangtai:
        filtered = [item for item in filtered if item.get("zhuangtai") == zhuangtai]
    
    # 按排序字段排序
    filtered.sort(key=lambda x: x.get("paixu", 999))
    
    return [
        {
            "id": item["id"],
            "fenlei_mingcheng": item["fenlei_mingcheng"],
            "fenlei_bianma": item["fenlei_bianma"]
        }
        for item in filtered
    ]


@category_router.get("/{category_id}")
async def get_category_detail(category_id: str):
    """获取产品分类详情"""
    category = find_product_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="产品分类不存在")
    return category


@category_router.post("/")
async def create_category(payload: Dict):
    """创建产品分类"""
    if not payload.get("fenlei_mingcheng") or not payload.get("fenlei_bianma"):
        raise HTTPException(status_code=400, detail="分类名称和编码不能为空")

    new_category = {
        "id": str(uuid4()),
        "fenlei_mingcheng": payload.get("fenlei_mingcheng"),
        "fenlei_bianma": payload.get("fenlei_bianma"),
        "miaoshu": payload.get("miaoshu", ""),
        "zhuangtai": payload.get("zhuangtai", "active"),
        "paixu": payload.get("paixu", 999),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    product_categories_data.append(new_category)
    return new_category


@category_router.put("/{category_id}")
async def update_category(category_id: str, payload: Dict):
    """更新产品分类"""
    category = find_product_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="产品分类不存在")

    for field in ["fenlei_mingcheng", "fenlei_bianma", "miaoshu", "zhuangtai", "paixu"]:
        if field in payload and payload[field] is not None:
            category[field] = payload[field]

    category["updated_at"] = _now_iso()
    return category


@category_router.delete("/{category_id}")
async def delete_category(category_id: str):
    """删除产品分类"""
    category = find_product_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="产品分类不存在")
    
    # 检查是否有产品使用此分类
    products_using_category = [p for p in products_data if p.get("fenlei_id") == category_id]
    if products_using_category:
        raise HTTPException(status_code=400, detail="该分类下还有产品，无法删除")
    
    product_categories_data.remove(category)
    return {"message": "产品分类删除成功"}


# ==================== 产品项目接口 ====================

@product_router.get("/")
async def list_products(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    fenlei_id: Optional[str] = None,
    zhuangtai: Optional[str] = None,
    shi_tuijian: Optional[bool] = None
):
    """获取产品项目列表"""
    filtered = products_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("xiangmu_mingcheng", "").lower()
            or keyword in item.get("xiangmu_bianma", "").lower()
            or keyword in item.get("xiangmu_beizhu", "").lower()
        ]

    if fenlei_id:
        filtered = [item for item in filtered if item.get("fenlei_id") == fenlei_id]

    if zhuangtai:
        filtered = [item for item in filtered if item.get("zhuangtai") == zhuangtai]



    # 按排序字段排序
    filtered.sort(key=lambda x: x.get("paixu", 999))

    return _paginate(filtered, page, size)


@product_router.get("/{product_id}")
async def get_product_detail(product_id: str):
    """获取产品项目详情"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    return product


@product_router.post("/")
async def create_product(payload: Dict):
    """创建产品项目"""
    if not payload.get("xiangmu_mingcheng") or not payload.get("xiangmu_bianma"):
        raise HTTPException(status_code=400, detail="项目名称和编码不能为空")

    # 验证分类是否存在
    fenlei_id = payload.get("fenlei_id")
    if fenlei_id:
        category = find_product_category(fenlei_id)
        if not category:
            raise HTTPException(status_code=400, detail="产品分类不存在")
        fenlei_mingcheng = category.get("fenlei_mingcheng")
    else:
        fenlei_mingcheng = ""

    new_product = {
        "id": str(uuid4()),
        "xiangmu_mingcheng": payload.get("xiangmu_mingcheng"),
        "xiangmu_bianma": payload.get("xiangmu_bianma"),
        "fenlei_id": fenlei_id,
        "fenlei_mingcheng": fenlei_mingcheng,
        "xiangmu_beizhu": payload.get("xiangmu_beizhu", ""),
        "yewu_baojia": payload.get("yewu_baojia", 0.0),
        "baojia_danwei": payload.get("baojia_danwei", "yuan"),
        "banshi_tianshu": payload.get("banshi_tianshu", 1),
        "zhuangtai": payload.get("zhuangtai", "active"),
        "paixu": payload.get("paixu", 999),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    products_data.append(new_product)
    return new_product


@product_router.put("/{product_id}")
async def update_product(product_id: str, payload: Dict):
    """更新产品项目"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    # 如果更新了分类，需要验证分类是否存在并更新分类名称
    if "fenlei_id" in payload:
        fenlei_id = payload["fenlei_id"]
        if fenlei_id:
            category = find_product_category(fenlei_id)
            if not category:
                raise HTTPException(status_code=400, detail="产品分类不存在")
            product["fenlei_mingcheng"] = category.get("fenlei_mingcheng")
        else:
            product["fenlei_mingcheng"] = ""

    for field in ["xiangmu_mingcheng", "xiangmu_bianma", "fenlei_id", "xiangmu_beizhu",
                  "yewu_baojia", "baojia_danwei", "banshi_tianshu", "zhuangtai", "paixu"]:
        if field in payload and payload[field] is not None:
            product[field] = payload[field]

    product["updated_at"] = _now_iso()
    return product


@product_router.delete("/{product_id}")
async def delete_product(product_id: str):
    """删除产品项目"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")
    
    products_data.remove(product)
    return {"message": "产品项目删除成功"}


@product_router.get("/statistics/overview")
async def get_product_statistics():
    """获取产品统计信息"""
    total_products = len(products_data)
    total_categories = len(product_categories_data)
    
    # 按分类统计产品数量
    category_stats = {}
    for product in products_data:
        fenlei_id = product.get("fenlei_id", "未分类")
        category_stats[fenlei_id] = category_stats.get(fenlei_id, 0) + 1
    
    # 按状态统计
    status_stats = {}
    for product in products_data:
        status = product.get("zhuangtai", "unknown")
        status_stats[status] = status_stats.get(status, 0) + 1
    
    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "active_products": len([p for p in products_data if p.get("zhuangtai") == "active"]),
        "category_distribution": category_stats,
        "status_distribution": status_stats
    }


# 产品步骤路由
step_router = APIRouter(prefix="/api/v1/product-management/steps", tags=["产品步骤"])

# 产品步骤模拟数据
product_steps_data = [
    {
        "id": "step-1",
        "buzou_mingcheng": "收集客户资料",
        "xiangmu_id": "prod-1",
        "yugu_shichang": 2.0,
        "shichang_danwei": "tian",
        "buzou_feiyong": 0.0,
        "buzou_miaoshu": "收集客户营业执照、身份证等基础资料",
        "paixu": 1,
        "shi_bixu": "Y",
        "zhuangtai": "active",
        "created_at": "2024-01-10T08:00:00Z",
        "updated_at": "2024-01-10T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "step-2",
        "buzou_mingcheng": "建立账套",
        "xiangmu_id": "prod-1",
        "yugu_shichang": 1.0,
        "shichang_danwei": "tian",
        "buzou_feiyong": 0.0,
        "buzou_miaoshu": "在财务软件中建立客户账套",
        "paixu": 2,
        "shi_bixu": "Y",
        "zhuangtai": "active",
        "created_at": "2024-01-10T08:00:00Z",
        "updated_at": "2024-01-10T08:00:00Z",
        "created_by": "admin"
    }
]


def find_product_step(step_id: str):
    """查找产品步骤"""
    for step in product_steps_data:
        if step["id"] == step_id:
            return step
    return None


@step_router.get("/{step_id}")
async def get_step_detail(step_id: str):
    """获取产品步骤详情"""
    step = find_product_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="产品步骤不存在")
    return step


@step_router.post("/")
async def create_step(payload: Dict):
    """创建产品步骤"""
    if not payload.get("buzou_mingcheng") or not payload.get("xiangmu_id"):
        raise HTTPException(status_code=400, detail="步骤名称和项目ID不能为空")

    # 验证项目是否存在
    product = find_product(payload["xiangmu_id"])
    if not product:
        raise HTTPException(status_code=400, detail="产品项目不存在")

    new_step = {
        "id": str(uuid4()),
        "buzou_mingcheng": payload.get("buzou_mingcheng"),
        "xiangmu_id": payload.get("xiangmu_id"),
        "yugu_shichang": payload.get("yugu_shichang", 1.0),
        "shichang_danwei": payload.get("shichang_danwei", "tian"),
        "buzou_feiyong": payload.get("buzou_feiyong", 0.0),
        "buzou_miaoshu": payload.get("buzou_miaoshu", ""),
        "paixu": payload.get("paixu", 999),
        "shi_bixu": payload.get("shi_bixu", "Y"),
        "zhuangtai": payload.get("zhuangtai", "active"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    product_steps_data.append(new_step)
    return new_step


@step_router.put("/{step_id}")
async def update_step(step_id: str, payload: Dict):
    """更新产品步骤"""
    step = find_product_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="产品步骤不存在")

    for field in ["buzou_mingcheng", "yugu_shichang", "shichang_danwei", "buzou_feiyong",
                  "buzou_miaoshu", "paixu", "shi_bixu", "zhuangtai"]:
        if field in payload and payload[field] is not None:
            step[field] = payload[field]

    step["updated_at"] = _now_iso()
    return step


@step_router.delete("/{step_id}")
async def delete_step(step_id: str):
    """删除产品步骤"""
    step = find_product_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="产品步骤不存在")

    product_steps_data.remove(step)
    return {"message": "产品步骤删除成功"}


# 在产品路由中添加步骤相关接口
@product_router.get("/{product_id}/steps")
async def get_product_steps(product_id: str):
    """获取产品项目的步骤列表"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    steps = [step for step in product_steps_data if step.get("xiangmu_id") == product_id]
    steps.sort(key=lambda x: x.get("paixu", 999))
    return steps


@product_router.get("/{product_id}/detail")
async def get_product_detail_with_steps(product_id: str):
    """获取产品项目完整详情（包含步骤列表）"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    steps = [step for step in product_steps_data if step.get("xiangmu_id") == product_id]
    steps.sort(key=lambda x: x.get("paixu", 999))

    # 计算步骤统计
    total_time = sum(step.get("yugu_shichang", 0) for step in steps)
    total_cost = sum(step.get("buzou_feiyong", 0) for step in steps)

    return {
        **product,
        "buzou_list": steps,
        "buzou_count": len(steps),
        "total_time": total_time,
        "total_cost": total_cost
    }


@product_router.put("/{product_id}/steps")
async def batch_update_product_steps(product_id: str, payload: Dict):
    """批量更新产品步骤"""
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品项目不存在")

    buzou_list = payload.get("buzou_list", [])

    # 删除原有步骤
    global product_steps_data
    product_steps_data = [step for step in product_steps_data if step.get("xiangmu_id") != product_id]

    # 添加新步骤
    updated_steps = []
    for i, step_data in enumerate(buzou_list):
        new_step = {
            "id": step_data.get("id", str(uuid4())),
            "buzou_mingcheng": step_data.get("buzou_mingcheng"),
            "xiangmu_id": product_id,
            "yugu_shichang": step_data.get("yugu_shichang", 1.0),
            "shichang_danwei": step_data.get("shichang_danwei", "tian"),
            "buzou_feiyong": step_data.get("buzou_feiyong", 0.0),
            "buzou_miaoshu": step_data.get("buzou_miaoshu", ""),
            "paixu": i + 1,
            "shi_bixu": step_data.get("shi_bixu", "Y"),
            "zhuangtai": step_data.get("zhuangtai", "active"),
            "created_at": step_data.get("created_at", _now_iso()),
            "updated_at": _now_iso(),
            "created_by": step_data.get("created_by", "admin")
        }
        product_steps_data.append(new_step)
        updated_steps.append(new_step)

    return updated_steps
