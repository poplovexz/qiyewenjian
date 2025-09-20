"""
产品管理数据模块
"""
from typing import List, Dict, Optional


# 产品分类模拟数据
product_categories_data: List[Dict] = [
    {
        "id": "cat-1",
        "fenlei_mingcheng": "代理记账服务",
        "fenlei_bianma": "accounting_service",
        "miaoshu": "提供专业的代理记账服务",
        "zhuangtai": "active",
        "paixu": 1,
        "created_at": "2024-01-01T08:00:00Z",
        "updated_at": "2024-01-01T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "cat-2",
        "fenlei_mingcheng": "税务咨询",
        "fenlei_bianma": "tax_consulting",
        "miaoshu": "税务政策咨询和筹划服务",
        "zhuangtai": "active",
        "paixu": 2,
        "created_at": "2024-01-02T08:00:00Z",
        "updated_at": "2024-01-02T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "cat-3",
        "fenlei_mingcheng": "工商注册",
        "fenlei_bianma": "business_registration",
        "miaoshu": "公司注册、变更等工商服务",
        "zhuangtai": "active",
        "paixu": 3,
        "created_at": "2024-01-03T08:00:00Z",
        "updated_at": "2024-01-03T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "cat-4",
        "fenlei_mingcheng": "财务审计",
        "fenlei_bianma": "financial_audit",
        "miaoshu": "财务报表审计服务",
        "zhuangtai": "active",
        "paixu": 4,
        "created_at": "2024-01-04T08:00:00Z",
        "updated_at": "2024-01-04T08:00:00Z",
        "created_by": "admin"
    }
]


# 产品项目模拟数据
products_data: List[Dict] = [
    {
        "id": "prod-1",
        "xiangmu_mingcheng": "小规模纳税人代理记账",
        "xiangmu_bianma": "ACC_SMALL_001",
        "fenlei_id": "cat-1",
        "fenlei_mingcheng": "代理记账服务",
        "xiangmu_beizhu": "适用于小规模纳税人的代理记账服务",
        "yewu_baojia": 200.00,
        "baojia_danwei": "yuan",
        "banshi_tianshu": 30,
        "zhuangtai": "active",
        "paixu": 1,
        "created_at": "2024-01-05T08:00:00Z",
        "updated_at": "2024-01-05T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "prod-2",
        "xiangmu_mingcheng": "一般纳税人代理记账",
        "xiangmu_bianma": "ACC_GENERAL_001",
        "fenlei_id": "cat-1",
        "fenlei_mingcheng": "代理记账服务",
        "xiangmu_beizhu": "适用于一般纳税人的代理记账服务",
        "yewu_baojia": 500.00,
        "baojia_danwei": "yuan",
        "banshi_tianshu": 30,
        "zhuangtai": "active",
        "paixu": 2,
        "created_at": "2024-01-06T08:00:00Z",
        "updated_at": "2024-01-06T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "prod-3",
        "xiangmu_mingcheng": "税务筹划咨询",
        "xiangmu_bianma": "TAX_PLAN_001",
        "fenlei_id": "cat-2",
        "fenlei_mingcheng": "税务咨询",
        "xiangmu_beizhu": "专业的税务筹划和优化方案",
        "yewu_baojia": 1000.00,
        "baojia_danwei": "yuan",
        "banshi_tianshu": 7,
        "zhuangtai": "active",
        "paixu": 3,
        "created_at": "2024-01-07T08:00:00Z",
        "updated_at": "2024-01-07T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "prod-4",
        "xiangmu_mingcheng": "有限公司注册",
        "xiangmu_bianma": "REG_COMPANY_001",
        "fenlei_id": "cat-3",
        "fenlei_mingcheng": "工商注册",
        "xiangmu_beizhu": "有限责任公司注册服务",
        "yewu_baojia": 800.00,
        "baojia_danwei": "yuan",
        "banshi_tianshu": 15,
        "zhuangtai": "active",
        "paixu": 4,
        "created_at": "2024-01-08T08:00:00Z",
        "updated_at": "2024-01-08T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "prod-5",
        "xiangmu_mingcheng": "年度财务审计",
        "xiangmu_bianma": "AUDIT_ANNUAL_001",
        "fenlei_id": "cat-4",
        "fenlei_mingcheng": "财务审计",
        "xiangmu_beizhu": "企业年度财务报表审计",
        "yewu_baojia": 5000.00,
        "baojia_danwei": "yuan",
        "banshi_tianshu": 60,
        "zhuangtai": "active",
        "paixu": 5,
        "created_at": "2024-01-09T08:00:00Z",
        "updated_at": "2024-01-09T08:00:00Z",
        "created_by": "admin"
    }
]


def find_product_category(category_id: str) -> Optional[Dict]:
    """查找产品分类"""
    for item in product_categories_data:
        if item["id"] == category_id:
            return item
    return None


def find_product(product_id: str) -> Optional[Dict]:
    """查找产品"""
    for item in products_data:
        if item["id"] == product_id:
            return item
    return None
