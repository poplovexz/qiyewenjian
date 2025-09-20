"""
审核规则管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from uuid import uuid4

from ..utils import _paginate, _now_iso

router = APIRouter(prefix="/api/v1/audit-rules", tags=["审核规则"])

# 审核规则模拟数据
audit_rules_data = [
    {
        "id": "rule-1",
        "guize_mingcheng": "合同金额审核",
        "guize_leixing": "contract",
        "guize_miaoshu": "合同金额超过10000元需要审核",
        "chufa_tiaojian": "contract_amount > 10000",
        "shenhe_liucheng": "manager_approval",
        "zhuangtai": "active",
        "created_at": "2024-01-01T08:00:00Z",
        "updated_at": "2024-01-01T08:00:00Z",
        "created_by": "admin"
    },
    {
        "id": "rule-2",
        "guize_mingcheng": "客户状态变更审核",
        "guize_leixing": "customer",
        "guize_miaoshu": "客户状态变更为终止需要审核",
        "chufa_tiaojian": "status_change == 'terminated'",
        "shenhe_liucheng": "senior_approval",
        "zhuangtai": "active",
        "created_at": "2024-01-02T08:00:00Z",
        "updated_at": "2024-01-02T08:00:00Z",
        "created_by": "admin"
    }
]


@router.get("/")
async def list_audit_rules(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    guize_leixing: Optional[str] = None,
    zhuangtai: Optional[str] = None
):
    """获取审核规则列表"""
    filtered = audit_rules_data

    if search:
        keyword = search.lower()
        filtered = [
            item for item in filtered
            if keyword in item.get("guize_mingcheng", "").lower()
            or keyword in item.get("guize_miaoshu", "").lower()
        ]

    if guize_leixing:
        filtered = [item for item in filtered if item.get("guize_leixing") == guize_leixing]

    if zhuangtai:
        filtered = [item for item in filtered if item.get("zhuangtai") == zhuangtai]

    return _paginate(filtered, page, size)


@router.get("/{rule_id}")
async def get_audit_rule_detail(rule_id: str):
    """获取审核规则详情"""
    for rule in audit_rules_data:
        if rule["id"] == rule_id:
            return rule
    raise HTTPException(status_code=404, detail="审核规则不存在")


@router.post("/")
async def create_audit_rule(payload: Dict):
    """创建审核规则"""
    if not payload.get("guize_mingcheng") or not payload.get("guize_leixing"):
        raise HTTPException(status_code=400, detail="规则名称和类型不能为空")

    new_rule = {
        "id": str(uuid4()),
        "guize_mingcheng": payload.get("guize_mingcheng"),
        "guize_leixing": payload.get("guize_leixing"),
        "guize_miaoshu": payload.get("guize_miaoshu"),
        "chufa_tiaojian": payload.get("chufa_tiaojian"),
        "shenhe_liucheng": payload.get("shenhe_liucheng"),
        "zhuangtai": payload.get("zhuangtai", "active"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    audit_rules_data.append(new_rule)
    return new_rule


@router.put("/{rule_id}")
async def update_audit_rule(rule_id: str, payload: Dict):
    """更新审核规则"""
    for rule in audit_rules_data:
        if rule["id"] == rule_id:
            for field in ["guize_mingcheng", "guize_leixing", "guize_miaoshu", 
                         "chufa_tiaojian", "shenhe_liucheng", "zhuangtai"]:
                if field in payload and payload[field] is not None:
                    rule[field] = payload[field]
            
            rule["updated_at"] = _now_iso()
            return rule
    
    raise HTTPException(status_code=404, detail="审核规则不存在")


@router.delete("/{rule_id}")
async def delete_audit_rule(rule_id: str):
    """删除审核规则"""
    for i, rule in enumerate(audit_rules_data):
        if rule["id"] == rule_id:
            audit_rules_data.pop(i)
            return {"message": "审核规则删除成功"}
    
    raise HTTPException(status_code=404, detail="审核规则不存在")


@router.get("/type/{rule_type}")
async def get_active_rules_by_type(rule_type: str):
    """根据类型获取启用的审核规则"""
    rules = [
        rule for rule in audit_rules_data 
        if rule.get("guize_leixing") == rule_type and rule.get("zhuangtai") == "active"
    ]
    return rules
