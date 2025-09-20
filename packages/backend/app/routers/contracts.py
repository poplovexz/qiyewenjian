"""
合同相关路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from uuid import uuid4
import re

from ..data.contracts import (
    contract_templates_data, find_contract_template,
    contract_parties_data, find_contract_party,
    payment_methods_data, find_payment_method,
    contracts_data, find_contract
)
from ..utils import _paginate, _now_iso

# 合同模板路由
template_router = APIRouter(prefix="/api/v1/contract-templates", tags=["合同模板"])

# 合同乙方主体路由
party_router = APIRouter(prefix="/api/v1/contract-parties", tags=["合同乙方主体"])

# 支付方式路由
payment_router = APIRouter(prefix="/api/v1/contract-payment-methods", tags=["支付方式"])

# 合同管理路由
contract_router = APIRouter(prefix="/api/v1/contracts", tags=["合同管理"])


# ==================== 合同模板接口 ====================

@template_router.get("/")
async def list_contract_templates(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    hetong_leixing: Optional[str] = None,
    moban_zhuangtai: Optional[str] = None,
    moban_fenlei: Optional[str] = None,
    shi_dangqian_banben: Optional[bool] = None
):
    """获取合同模板列表"""
    filtered = contract_templates_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("moban_mingcheng", "").lower()
            or keyword in item.get("moban_neirong", "").lower()
        ]

    if hetong_leixing:
        filtered = [item for item in filtered if item.get("hetong_leixing") == hetong_leixing]

    if moban_zhuangtai:
        filtered = [item for item in filtered if item.get("moban_zhuangtai") == moban_zhuangtai]

    if moban_fenlei:
        filtered = [item for item in filtered if item.get("moban_fenlei") == moban_fenlei]

    if shi_dangqian_banben is not None:
        filtered = [item for item in filtered if item.get("shi_dangqian_banben") == shi_dangqian_banben]

    return _paginate(filtered, page, size)


@template_router.get("/{template_id}")
async def get_contract_template_detail(template_id: str):
    """获取合同模板详情"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    return template


@template_router.post("/")
async def create_contract_template(payload: Dict):
    """创建合同模板"""
    if not payload.get("moban_mingcheng") or not payload.get("hetong_leixing"):
        raise HTTPException(status_code=400, detail="模板名称和合同类型不能为空")

    # 处理当前版本状态
    if payload.get("shi_dangqian_banben", False):
        for template in contract_templates_data:
            if template.get("hetong_leixing") == payload.get("hetong_leixing"):
                template["shi_dangqian_banben"] = False

    new_template = {
        "id": str(uuid4()),
        "moban_mingcheng": payload.get("moban_mingcheng"),
        "hetong_leixing": payload.get("hetong_leixing"),
        "moban_zhuangtai": payload.get("moban_zhuangtai", "draft"),
        "moban_fenlei": payload.get("moban_fenlei", "standard"),
        "moban_neirong": payload.get("moban_neirong", ""),
        "bianliang_peizhi": payload.get("bianliang_peizhi", "{}"),
        "shi_dangqian_banben": payload.get("shi_dangqian_banben", False),
        "banben_haoma": payload.get("banben_haoma", "1.0"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    contract_templates_data.append(new_template)
    return new_template


@template_router.put("/{template_id}")
async def update_contract_template(template_id: str, payload: Dict):
    """更新合同模板"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")

    # 处理当前版本状态
    if payload.get("shi_dangqian_banben", False):
        for t in contract_templates_data:
            if t.get("hetong_leixing") == template.get("hetong_leixing") and t["id"] != template_id:
                t["shi_dangqian_banben"] = False

    for field in ["moban_mingcheng", "hetong_leixing", "moban_zhuangtai", "moban_fenlei", 
                  "moban_neirong", "bianliang_peizhi", "shi_dangqian_banben", "banben_haoma"]:
        if field in payload and payload[field] is not None:
            template[field] = payload[field]

    template["updated_at"] = _now_iso()
    return template


@template_router.delete("/{template_id}")
async def delete_contract_template(template_id: str):
    """删除合同模板"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    contract_templates_data.remove(template)
    return {"message": "合同模板删除成功"}


@template_router.patch("/{template_id}/status")
async def toggle_template_status(template_id: str, payload: Dict):
    """切换模板状态"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    
    new_status = payload.get("moban_zhuangtai")
    if not new_status:
        raise HTTPException(status_code=400, detail="缺少状态参数")
    
    template["moban_zhuangtai"] = new_status
    template["updated_at"] = _now_iso()
    return template


@template_router.post("/{template_id}/preview")
async def preview_contract_template(template_id: str, payload: Dict):
    """预览合同模板（支持占位符替换）"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    
    content = template.get("moban_neirong", "")
    variables = payload.get("bianliang_zhis", {})
    
    # 简单的占位符替换
    for key, value in variables.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, str(value))
    
    return {
        "yulan_neirong": content,
        "moban_mingcheng": template.get("moban_mingcheng"),
        "hetong_leixing": template.get("hetong_leixing")
    }


@template_router.get("/{template_id}/variables")
async def get_template_variables(template_id: str):
    """获取模板变量配置"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    
    return {
        "bianliang_peizhi": template.get("bianliang_peizhi", "{}"),
        "moban_id": template_id
    }


@template_router.put("/{template_id}/variables")
async def update_template_variables(template_id: str, payload: Dict):
    """更新模板变量配置"""
    template = find_contract_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    
    template["bianliang_peizhi"] = payload.get("bianliang_peizhi", "{}")
    template["updated_at"] = _now_iso()
    return {"message": "变量配置更新成功"}


@template_router.get("/statistics/overview")
async def get_template_statistics():
    """获取合同模板统计信息"""
    total = len(contract_templates_data)
    type_stats = {}
    status_stats = {}
    
    for template in contract_templates_data:
        # 按类型统计
        t_type = template.get("hetong_leixing", "unknown")
        type_stats[t_type] = type_stats.get(t_type, 0) + 1
        
        # 按状态统计
        status = template.get("moban_zhuangtai", "unknown")
        status_stats[status] = status_stats.get(status, 0) + 1
    
    return {
        "total": total,
        "type_distribution": type_stats,
        "status_distribution": status_stats,
        "current_version_count": len([t for t in contract_templates_data if t.get("shi_dangqian_banben", False)])
    }


# ==================== 合同乙方主体接口 ====================

@party_router.get("/")
async def list_contract_parties(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    zhuti_leixing: Optional[str] = None
):
    """获取合同乙方主体列表"""
    filtered = contract_parties_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("zhuti_mingcheng", "").lower()
            or keyword in item.get("faren_daibiao", "").lower()
            or keyword in item.get("lianxi_dianhua", "").lower()
        ]

    if zhuti_leixing:
        filtered = [item for item in filtered if item.get("zhuti_leixing") == zhuti_leixing]

    return _paginate(filtered, page, size)


@party_router.get("/{party_id}")
async def get_contract_party_detail(party_id: str):
    """获取合同乙方主体详情"""
    party = find_contract_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="合同乙方主体不存在")
    return party


@party_router.post("/")
async def create_contract_party(payload: Dict):
    """创建合同乙方主体"""
    if not payload.get("zhuti_mingcheng") or not payload.get("zhuti_leixing"):
        raise HTTPException(status_code=400, detail="主体名称和类型不能为空")

    new_party = {
        "id": str(uuid4()),
        "zhuti_mingcheng": payload.get("zhuti_mingcheng"),
        "zhuti_leixing": payload.get("zhuti_leixing"),
        "tongyi_shehui_xinyong_daima": payload.get("tongyi_shehui_xinyong_daima"),
        "yingyezhizhao_haoma": payload.get("yingyezhizhao_haoma"),
        "faren_daibiao": payload.get("faren_daibiao"),
        "lianxi_dianhua": payload.get("lianxi_dianhua"),
        "lianxi_youxiang": payload.get("lianxi_youxiang"),
        "zhuce_dizhi": payload.get("zhuce_dizhi"),
        "yinhang_mingcheng": payload.get("yinhang_mingcheng"),
        "yinhang_zhanghu": payload.get("yinhang_zhanghu"),
        "yinhang_kaihuhang": payload.get("yinhang_kaihuhang"),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    contract_parties_data.append(new_party)
    return new_party


@party_router.put("/{party_id}")
async def update_contract_party(party_id: str, payload: Dict):
    """更新合同乙方主体"""
    party = find_contract_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="合同乙方主体不存在")

    for field in ["zhuti_mingcheng", "zhuti_leixing", "tongyi_shehui_xinyong_daima",
                  "yingyezhizhao_haoma", "faren_daibiao", "lianxi_dianhua", "lianxi_youxiang",
                  "zhuce_dizhi", "yinhang_mingcheng", "yinhang_zhanghu", "yinhang_kaihuhang", "beizhu"]:
        if field in payload and payload[field] is not None:
            party[field] = payload[field]

    party["updated_at"] = _now_iso()
    return party


@party_router.delete("/{party_id}")
async def delete_contract_party(party_id: str):
    """删除合同乙方主体"""
    party = find_contract_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="合同乙方主体不存在")
    contract_parties_data.remove(party)
    return {"message": "合同乙方主体删除成功"}


# ==================== 支付方式接口 ====================

@payment_router.get("/")
async def list_payment_methods(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    zhifu_leixing: Optional[str] = None
):
    """获取支付方式列表"""
    filtered = payment_methods_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("zhifu_mingcheng", "").lower()
            or keyword in item.get("zhanghu_mingcheng", "").lower()
            or keyword in item.get("zhanghu_haoma", "").lower()
        ]

    if zhifu_leixing:
        filtered = [item for item in filtered if item.get("zhifu_leixing") == zhifu_leixing]

    return _paginate(filtered, page, size)


@payment_router.get("/{method_id}")
async def get_payment_method_detail(method_id: str):
    """获取支付方式详情"""
    method = find_payment_method(method_id)
    if not method:
        raise HTTPException(status_code=404, detail="支付方式不存在")
    return method


@payment_router.post("/")
async def create_payment_method(payload: Dict):
    """创建支付方式"""
    if not payload.get("zhifu_mingcheng") or not payload.get("zhifu_leixing"):
        raise HTTPException(status_code=400, detail="支付名称和类型不能为空")

    new_method = {
        "id": str(uuid4()),
        "yifang_zhuti_id": payload.get("yifang_zhuti_id"),
        "zhifu_leixing": payload.get("zhifu_leixing"),
        "zhifu_mingcheng": payload.get("zhifu_mingcheng"),
        "zhanghu_mingcheng": payload.get("zhanghu_mingcheng"),
        "zhanghu_haoma": payload.get("zhanghu_haoma"),
        "kaihuhang_mingcheng": payload.get("kaihuhang_mingcheng"),
        "zhifubao_haoma": payload.get("zhifubao_haoma"),
        "weixin_haoma": payload.get("weixin_haoma"),
        "zhifu_zhuangtai": payload.get("zhifu_zhuangtai", "active"),
        "shi_moren": payload.get("shi_moren", False),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    payment_methods_data.append(new_method)
    return new_method


@payment_router.put("/{method_id}")
async def update_payment_method(method_id: str, payload: Dict):
    """更新支付方式"""
    method = find_payment_method(method_id)
    if not method:
        raise HTTPException(status_code=404, detail="支付方式不存在")

    for field in ["zhifu_mingcheng", "zhifu_leixing", "zhanghu_mingcheng", "zhanghu_haoma",
                  "kaihuhang_mingcheng", "zhifubao_haoma", "weixin_haoma", "zhifu_zhuangtai",
                  "shi_moren", "beizhu"]:
        if field in payload and payload[field] is not None:
            method[field] = payload[field]

    method["updated_at"] = _now_iso()
    return method


@payment_router.delete("/{method_id}")
async def delete_payment_method(method_id: str):
    """删除支付方式"""
    method = find_payment_method(method_id)
    if not method:
        raise HTTPException(status_code=404, detail="支付方式不存在")
    payment_methods_data.remove(method)
    return {"message": "支付方式删除成功"}


# ==================== 合同管理接口 ====================

@contract_router.get("/")
async def list_contracts(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    hetong_leixing: Optional[str] = None,
    hetong_zhuangtai: Optional[str] = None,
    yifang_zhuti_id: Optional[str] = None
):
    """获取合同列表"""
    filtered = contracts_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("hetong_bianhao", "").lower()
            or keyword in item.get("hetong_mingcheng", "").lower()
            or keyword in item.get("yifang_mingcheng", "").lower()
        ]

    if hetong_leixing:
        filtered = [item for item in filtered if item.get("hetong_leixing") == hetong_leixing]

    if hetong_zhuangtai:
        filtered = [item for item in filtered if item.get("hetong_zhuangtai") == hetong_zhuangtai]

    if yifang_zhuti_id:
        filtered = [item for item in filtered if item.get("yifang_zhuti_id") == yifang_zhuti_id]

    return _paginate(filtered, page, size)


@contract_router.get("/{contract_id}")
async def get_contract_detail(contract_id: str):
    """获取合同详情"""
    contract = find_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract


@contract_router.post("/")
async def create_contract(payload: Dict):
    """创建合同"""
    if not payload.get("hetong_mingcheng") or not payload.get("yifang_zhuti_id"):
        raise HTTPException(status_code=400, detail="合同名称和乙方主体不能为空")

    # 验证乙方主体是否存在
    party = find_contract_party(payload["yifang_zhuti_id"])
    if not party:
        raise HTTPException(status_code=400, detail="乙方主体不存在")

    # 生成合同编号
    contract_count = len(contracts_data) + 1
    hetong_bianhao = f"HT-2024-{contract_count:03d}"

    new_contract = {
        "id": str(uuid4()),
        "hetong_bianhao": hetong_bianhao,
        "hetong_mingcheng": payload.get("hetong_mingcheng"),
        "yifang_zhuti_id": payload.get("yifang_zhuti_id"),
        "yifang_mingcheng": party.get("zhuti_mingcheng"),
        "hetong_leixing": payload.get("hetong_leixing", "service"),
        "hetong_zhuangtai": payload.get("hetong_zhuangtai", "draft"),
        "qianyue_riqi": payload.get("qianyue_riqi"),
        "shengxiao_riqi": payload.get("shengxiao_riqi"),
        "daqi_riqi": payload.get("daqi_riqi"),
        "hetong_jine": payload.get("hetong_jine", 0.0),
        "yifu_jine": payload.get("yifu_jine", 0.0),
        "weifu_jine": payload.get("hetong_jine", 0.0) - payload.get("yifu_jine", 0.0),
        "zhifu_fangshi": payload.get("zhifu_fangshi", "lump_sum"),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    contracts_data.append(new_contract)
    return new_contract


@contract_router.put("/{contract_id}")
async def update_contract(contract_id: str, payload: Dict):
    """更新合同信息"""
    contract = find_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")

    # 如果更新了乙方主体，需要验证并更新名称
    if "yifang_zhuti_id" in payload:
        party = find_contract_party(payload["yifang_zhuti_id"])
        if not party:
            raise HTTPException(status_code=400, detail="乙方主体不存在")
        contract["yifang_mingcheng"] = party.get("zhuti_mingcheng")

    for field in ["hetong_mingcheng", "yifang_zhuti_id", "hetong_leixing", "hetong_zhuangtai",
                  "qianyue_riqi", "shengxiao_riqi", "daqi_riqi", "hetong_jine", "yifu_jine",
                  "zhifu_fangshi", "beizhu"]:
        if field in payload and payload[field] is not None:
            contract[field] = payload[field]

    # 重新计算未付金额
    if "hetong_jine" in payload or "yifu_jine" in payload:
        contract["weifu_jine"] = contract.get("hetong_jine", 0.0) - contract.get("yifu_jine", 0.0)

    contract["updated_at"] = _now_iso()
    return contract


@contract_router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """删除合同"""
    contract = find_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")

    contracts_data.remove(contract)
    return {"message": "合同删除成功"}


@contract_router.post("/from-quote/{baojia_id}")
async def create_contract_from_quote(baojia_id: str):
    """基于报价自动生成合同"""
    # 这里应该根据报价ID获取报价信息，然后生成合同
    # 由于没有报价数据，这里返回一个模拟的合同

    contract_count = len(contracts_data) + 1
    hetong_bianhao = f"HT-2024-{contract_count:03d}"

    new_contract = {
        "id": str(uuid4()),
        "hetong_bianhao": hetong_bianhao,
        "hetong_mingcheng": f"基于报价{baojia_id}生成的合同",
        "yifang_zhuti_id": "party-1",
        "yifang_mingcheng": "上海某科技有限公司",
        "hetong_leixing": "service",
        "hetong_zhuangtai": "draft",
        "qianyue_riqi": None,
        "shengxiao_riqi": None,
        "daqi_riqi": "2024-12-31",
        "hetong_jine": 5000.00,
        "yifu_jine": 0.00,
        "weifu_jine": 5000.00,
        "zhifu_fangshi": "monthly",
        "beizhu": f"基于报价{baojia_id}自动生成",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": "admin"
    }

    contracts_data.append(new_contract)
    return new_contract
