"""
支付管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from uuid import uuid4

from ..utils import _paginate, _now_iso

router = APIRouter(prefix="/api/v1", tags=["支付管理"])

# 合同支付模拟数据
contract_payments_data = [
    {
        "id": "payment-1",
        "hetong_id": "contract-1",
        "hetong_bianhao": "HT-2024-001",
        "zhifu_jine": 2000.00,
        "zhifu_riqi": "2024-01-31",
        "zhifu_zhuangtai": "completed",
        "zhifu_fangshi": "bank_transfer",
        "beizhu": "首期付款",
        "created_at": "2024-01-31T08:00:00Z",
        "updated_at": "2024-01-31T08:00:00Z",
        "created_by": "admin"
    }
]

# 银行汇款单据模拟数据
bank_transfers_data = [
    {
        "id": "transfer-1",
        "zhifu_id": "payment-1",
        "huikuan_jine": 2000.00,
        "huikuan_riqi": "2024-01-31",
        "huikuan_yinhang": "工商银行",
        "huikuan_zhanghu": "6222021234567890",
        "shenhe_zhuangtai": "approved",
        "beizhu": "合同首期付款",
        "created_at": "2024-01-31T08:00:00Z",
        "updated_at": "2024-01-31T08:00:00Z",
        "created_by": "admin"
    }
]


@router.get("/contract-payments")
async def list_contract_payments(
    page: int = 1,
    size: int = 20,
    hetong_id: Optional[str] = None,
    zhifu_zhuangtai: Optional[str] = None
):
    """获取合同支付列表"""
    filtered = contract_payments_data

    if hetong_id:
        filtered = [item for item in filtered if item.get("hetong_id") == hetong_id]

    if zhifu_zhuangtai:
        filtered = [item for item in filtered if item.get("zhifu_zhuangtai") == zhifu_zhuangtai]

    return _paginate(filtered, page, size)


@router.get("/contract-payments/{payment_id}")
async def get_contract_payment_detail(payment_id: str):
    """获取合同支付详情"""
    for payment in contract_payments_data:
        if payment["id"] == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="支付记录不存在")


@router.post("/contract-payments")
async def create_contract_payment(payload: Dict):
    """创建合同支付"""
    new_payment = {
        "id": str(uuid4()),
        "hetong_id": payload.get("hetong_id"),
        "hetong_bianhao": payload.get("hetong_bianhao"),
        "zhifu_jine": payload.get("zhifu_jine", 0.0),
        "zhifu_riqi": payload.get("zhifu_riqi"),
        "zhifu_zhuangtai": payload.get("zhifu_zhuangtai", "pending"),
        "zhifu_fangshi": payload.get("zhifu_fangshi", "bank_transfer"),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    contract_payments_data.append(new_payment)
    return new_payment


@router.get("/contract-payments/contract/{contract_id}")
async def get_payments_by_contract(contract_id: str):
    """根据合同ID获取支付记录"""
    payments = [p for p in contract_payments_data if p.get("hetong_id") == contract_id]
    return payments


@router.get("/bank-transfers")
async def list_bank_transfers(
    page: int = 1,
    size: int = 20,
    shenhe_zhuangtai: Optional[str] = None
):
    """获取银行汇款单据列表"""
    filtered = bank_transfers_data

    if shenhe_zhuangtai:
        filtered = [item for item in filtered if item.get("shenhe_zhuangtai") == shenhe_zhuangtai]

    return _paginate(filtered, page, size)


@router.get("/bank-transfers/{transfer_id}")
async def get_bank_transfer_detail(transfer_id: str):
    """获取银行汇款单据详情"""
    for transfer in bank_transfers_data:
        if transfer["id"] == transfer_id:
            return transfer
    raise HTTPException(status_code=404, detail="汇款单据不存在")


@router.post("/bank-transfers")
async def create_bank_transfer(payload: Dict):
    """创建银行汇款单据"""
    new_transfer = {
        "id": str(uuid4()),
        "zhifu_id": payload.get("zhifu_id"),
        "huikuan_jine": payload.get("huikuan_jine", 0.0),
        "huikuan_riqi": payload.get("huikuan_riqi"),
        "huikuan_yinhang": payload.get("huikuan_yinhang"),
        "huikuan_zhanghu": payload.get("huikuan_zhanghu"),
        "shenhe_zhuangtai": payload.get("shenhe_zhuangtai", "pending"),
        "beizhu": payload.get("beizhu"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "created_by": payload.get("created_by", "admin")
    }

    bank_transfers_data.append(new_transfer)
    return new_transfer


@router.post("/bank-transfers/{transfer_id}/audit")
async def audit_bank_transfer(transfer_id: str, payload: Dict):
    """审核银行汇款单据"""
    for transfer in bank_transfers_data:
        if transfer["id"] == transfer_id:
            transfer["shenhe_zhuangtai"] = payload.get("shenhe_zhuangtai", "approved")
            transfer["updated_at"] = _now_iso()
            return transfer
    raise HTTPException(status_code=404, detail="汇款单据不存在")


@router.get("/bank-transfers/payment/{payment_id}")
async def get_transfers_by_payment(payment_id: str):
    """根据合同支付ID获取汇款单据"""
    transfers = [t for t in bank_transfers_data if t.get("zhifu_id") == payment_id]
    return transfers
