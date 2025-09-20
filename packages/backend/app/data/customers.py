"""
客户管理数据模块
"""
from typing import List, Dict, Optional


# 客户模拟数据
customers_data: List[Dict] = [
    {
        "id": "customer-1",
        "gongsi_mingcheng": "上海科技有限公司",
        "tongyi_shehui_xinyong_daima": "91310000MA1K123456",
        "yingyezhizhao_haoma": "310000202401010001",
        "faren_xingming": "张三",
        "faren_shenfenzheng": "310101199001011234",
        "zhuce_dizhi": "上海市浦东新区世纪大道1000号",
        "jingying_dizhi": "上海市浦东新区世纪大道1000号",
        "lianxi_ren": "李四",
        "lianxi_dianhua": "021-88888888",
        "shouji_haoma": "13800138000",
        "youxiang_dizhi": "contact@company.com",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi": "2024-01-01",
        "fuwu_jieshu": "2024-12-31",
        "beizhu": "重要客户",
        "created_at": "2024-01-01T08:00:00Z",
        "updated_at": "2024-01-01T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "customer-2",
        "gongsi_mingcheng": "北京贸易有限公司",
        "tongyi_shehui_xinyong_daima": "91110000MA1K654321",
        "yingyezhizhao_haoma": "110000202401010002",
        "faren_xingming": "王五",
        "faren_shenfenzheng": "110101199002022345",
        "zhuce_dizhi": "北京市朝阳区建国路100号",
        "jingying_dizhi": "北京市朝阳区建国路100号",
        "lianxi_ren": "赵六",
        "lianxi_dianhua": "010-66666666",
        "shouji_haoma": "13800138001",
        "youxiang_dizhi": "info@trading.com",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi": "2024-02-01",
        "fuwu_jieshu": "2025-01-31",
        "beizhu": "新客户",
        "created_at": "2024-02-01T08:00:00Z",
        "updated_at": "2024-02-01T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "customer-3",
        "gongsi_mingcheng": "深圳制造有限公司",
        "tongyi_shehui_xinyong_daima": "91440300MA1K789012",
        "yingyezhizhao_haoma": "440300202401010003",
        "faren_xingming": "陈七",
        "faren_shenfenzheng": "440301199003033456",
        "zhuce_dizhi": "深圳市南山区科技园南路200号",
        "jingying_dizhi": "深圳市南山区科技园南路200号",
        "lianxi_ren": "刘八",
        "lianxi_dianhua": "0755-88888888",
        "shouji_haoma": "13800138002",
        "youxiang_dizhi": "service@manufacturing.com",
        "kehu_zhuangtai": "renewing",
        "fuwu_kaishi": "2023-06-01",
        "fuwu_jieshu": "2024-05-31",
        "beizhu": "续约中",
        "created_at": "2023-06-01T08:00:00Z",
        "updated_at": "2024-05-01T08:00:00Z",
        "created_by": "admin"
    }
]


# 服务记录模拟数据
service_records_data: List[Dict] = [
    {
        "id": "service-1",
        "kehu_id": "customer-1",
        "kehu_mingcheng": "上海科技有限公司",
        "fuwu_leixing": "代理记账",
        "fuwu_neirong": "2024年1月代理记账服务",
        "fuwu_riqi": "2024-01-31",
        "fuwu_zhuangtai": "completed",
        "fuwu_renyuan": "张会计",
        "fuwu_shichang": 8.0,
        "beizhu": "按时完成",
        "created_at": "2024-01-31T17:00:00Z",
        "updated_at": "2024-01-31T17:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "service-2",
        "kehu_id": "customer-2",
        "kehu_mingcheng": "北京贸易有限公司",
        "fuwu_leixing": "税务申报",
        "fuwu_neirong": "2024年2月税务申报",
        "fuwu_riqi": "2024-02-15",
        "fuwu_zhuangtai": "in_progress",
        "fuwu_renyuan": "李税务",
        "fuwu_shichang": 4.0,
        "beizhu": "进行中",
        "created_at": "2024-02-15T09:00:00Z",
        "updated_at": "2024-02-15T09:00:00Z",
        "created_by": "admin"
    }
]


def find_customer(customer_id: str) -> Optional[Dict]:
    """查找客户"""
    for item in customers_data:
        if item["id"] == customer_id:
            return item
    return None


def find_service_record(record_id: str) -> Optional[Dict]:
    """查找服务记录"""
    for item in service_records_data:
        if item["id"] == record_id:
            return item
    return None
