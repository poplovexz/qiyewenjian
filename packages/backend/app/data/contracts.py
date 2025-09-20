"""
合同相关数据模块
"""
from typing import List, Dict, Optional


# 合同模板数据存储（空列表，不包含模拟数据）
contract_templates_data: List[Dict] = []


# 合同数据存储
contracts_data: List[Dict] = [
    {
        "id": "contract-1",
        "hetong_bianhao": "HT-2024-001",
        "hetong_mingcheng": "代理记账服务合同",
        "yifang_zhuti_id": "party-1",
        "yifang_mingcheng": "上海某科技有限公司",
        "hetong_leixing": "service",
        "hetong_zhuangtai": "signed",
        "qianyue_riqi": "2024-01-15",
        "shengxiao_riqi": "2024-01-15",
        "daqi_riqi": "2024-12-31",
        "hetong_jine": 6000.00,
        "yifu_jine": 2000.00,
        "weifu_jine": 4000.00,
        "zhifu_fangshi": "monthly",
        "beizhu": "年度代理记账服务合同",
        "created_at": "2024-01-15T08:00:00Z",
        "updated_at": "2024-01-15T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "contract-2",
        "hetong_bianhao": "HT-2024-002",
        "hetong_mingcheng": "税务咨询服务合同",
        "yifang_zhuti_id": "party-2",
        "yifang_mingcheng": "张三",
        "hetong_leixing": "consulting",
        "hetong_zhuangtai": "draft",
        "qianyue_riqi": None,
        "shengxiao_riqi": None,
        "daqi_riqi": "2024-06-30",
        "hetong_jine": 3000.00,
        "yifu_jine": 0.00,
        "weifu_jine": 3000.00,
        "zhifu_fangshi": "lump_sum",
        "beizhu": "税务筹划咨询合同",
        "created_at": "2024-02-01T08:00:00Z",
        "updated_at": "2024-02-01T08:00:00Z",
        "created_by": "admin"
    }
]


# 合同乙方主体模拟数据
contract_parties_data: List[Dict] = [
    {
        "id": "party-1",
        "zhuti_mingcheng": "上海某科技有限公司",
        "zhuti_leixing": "enterprise",
        "tongyi_shehui_xinyong_daima": "91310000MA1K123456",
        "yingyezhizhao_haoma": "310000202401010001",
        "faren_daibiao": "李四",
        "lianxi_dianhua": "021-88888888",
        "lianxi_youxiang": "contact@company.com",
        "zhuce_dizhi": "上海市浦东新区世纪大道",
        "yinhang_mingcheng": "中国银行上海分行",
        "yinhang_zhanghu": "1234567890123456",
        "yinhang_kaihuhang": "中国银行上海分行营业部",
        "beizhu": "核心客户",
        "created_at": "2024-01-05T08:00:00Z",
        "updated_at": "2024-01-05T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "party-2",
        "zhuti_mingcheng": "张三",
        "zhuti_leixing": "individual",
        "lianxi_dianhua": "13800138000",
        "lianxi_youxiang": "zhangsan@example.com",
        "zhuce_dizhi": "北京市朝阳区",
        "beizhu": "个人客户",
        "created_at": "2024-02-01T09:00:00Z",
        "updated_at": "2024-02-01T09:00:00Z",
        "created_by": "admin"
    }
]


# 支付方式模拟数据
payment_methods_data: List[Dict] = [
    {
        "id": "pay-1",
        "yifang_zhuti_id": "party-1",
        "zhifu_leixing": "bank_transfer",
        "zhifu_mingcheng": "对公账户",
        "zhanghu_mingcheng": "上海某科技有限公司",
        "zhanghu_haoma": "6222021234567890",
        "kaihuhang_mingcheng": "工商银行上海分行",
        "zhifu_zhuangtai": "active",
        "shi_moren": True,
        "beizhu": "主要收款账户",
        "created_at": "2024-01-05T08:30:00Z",
        "updated_at": "2024-01-05T08:30:00Z",
        "created_by": "admin"
    },
    {
        "id": "pay-2",
        "yifang_zhuti_id": "party-1",
        "zhifu_leixing": "alipay",
        "zhifu_mingcheng": "支付宝收款",
        "zhifubao_haoma": "company-alipay@example.com",
        "zhifu_zhuangtai": "active",
        "shi_moren": False,
        "created_at": "2024-01-06T08:30:00Z",
        "updated_at": "2024-01-06T08:30:00Z",
        "created_by": "admin"
    },
    {
        "id": "pay-3",
        "yifang_zhuti_id": "party-2",
        "zhifu_leixing": "wechat_pay",
        "zhifu_mingcheng": "微信收款码",
        "weixin_haoma": "wxid-zhangsan",
        "zhifu_zhuangtai": "active",
        "shi_moren": True,
        "created_at": "2024-02-02T09:30:00Z",
        "updated_at": "2024-02-02T09:30:00Z",
        "created_by": "admin"
    }
]


def find_contract_template(template_id: str) -> Optional[Dict]:
    """查找合同模板"""
    for item in contract_templates_data:
        if item["id"] == template_id:
            return item
    return None


def find_contract_party(party_id: str) -> Optional[Dict]:
    """查找合同乙方主体"""
    for item in contract_parties_data:
        if item["id"] == party_id:
            return item
    return None


def find_payment_method(method_id: str) -> Optional[Dict]:
    """查找支付方式"""
    for item in payment_methods_data:
        if item["id"] == method_id:
            return item
    return None


def find_contract(contract_id: str) -> Optional[Dict]:
    """查找合同"""
    for item in contracts_data:
        if item["id"] == contract_id:
            return item
    return None
