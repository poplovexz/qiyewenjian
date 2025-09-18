"""
合同支付API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.yonghu_guanli import Yonghu
from src.services.zhifu_guanli.hetong_zhifu_service import HetongZhifuService
from src.schemas.zhifu_guanli import HetongZhifuCreate, HetongZhifuUpdate, HetongZhifuListParams

router = APIRouter()


@router.post("/", summary="创建合同支付")
async def create_hetong_zhifu(
    zhifu_data: HetongZhifuCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    创建合同支付
    
    - **hetong_id**: 合同ID（必填）
    - **zhifu_fangshi**: 支付方式（必填）
    - **zhifu_jine**: 支付金额（必填）
    """
    service = HetongZhifuService(db)
    result = service.create_hetong_zhifu(zhifu_data, current_user.id)
    
    return {
        "success": True,
        "message": "合同支付创建成功",
        "data": result
    }


@router.get("/", summary="获取合同支付列表")
async def get_hetong_zhifu_list(
    page: int = 1,
    size: int = 20,
    hetong_id: str = None,
    zhifu_fangshi: str = None,
    zhifu_zhuangtai: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取合同支付列表"""
    params = HetongZhifuListParams(
        page=page,
        size=size,
        hetong_id=hetong_id,
        zhifu_fangshi=zhifu_fangshi,
        zhifu_zhuangtai=zhifu_zhuangtai,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = HetongZhifuService(db)
    return service.get_hetong_zhifu_list(params)


@router.get("/{zhifu_id}", summary="获取合同支付详情")
async def get_hetong_zhifu_by_id(
    zhifu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据ID获取合同支付详情"""
    service = HetongZhifuService(db)
    result = service.get_hetong_zhifu_by_id(zhifu_id)
    
    return {
        "success": True,
        "data": result
    }


@router.put("/{zhifu_id}", summary="更新合同支付")
async def update_hetong_zhifu(
    zhifu_id: str,
    zhifu_data: HetongZhifuUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """更新合同支付"""
    service = HetongZhifuService(db)
    result = service.update_hetong_zhifu(zhifu_id, zhifu_data, current_user.id)
    
    return {
        "success": True,
        "message": "合同支付更新成功",
        "data": result
    }


@router.get("/contract/{hetong_id}", summary="根据合同ID获取支付记录")
async def get_zhifu_by_contract(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据合同ID获取支付记录"""
    service = HetongZhifuService(db)
    result = service.get_zhifu_by_hetong(hetong_id)
    
    return {
        "success": True,
        "data": result
    }


@router.post("/{zhifu_id}/alipay", summary="发起支付宝支付")
async def initiate_alipay(
    zhifu_id: str,
    return_url: str = None,
    notify_url: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """发起支付宝支付"""
    service = HetongZhifuService(db)
    result = service.initiate_alipay_payment(zhifu_id, return_url, notify_url)
    
    return {
        "success": True,
        "message": "支付宝支付发起成功",
        "data": result
    }


@router.post("/{zhifu_id}/wechat", summary="发起微信支付")
async def initiate_wechat_pay(
    zhifu_id: str,
    notify_url: str = None,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """发起微信支付"""
    service = HetongZhifuService(db)
    result = service.initiate_wechat_payment(zhifu_id, notify_url)
    
    return {
        "success": True,
        "message": "微信支付发起成功",
        "data": result
    }


@router.post("/{zhifu_id}/bank-transfer", summary="选择银行转账")
async def select_bank_transfer(
    zhifu_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """选择银行转账支付方式"""
    service = HetongZhifuService(db)
    result = service.select_bank_transfer(zhifu_id)
    
    return {
        "success": True,
        "message": "银行转账支付方式选择成功",
        "data": result
    }


@router.post("/notify/alipay", summary="支付宝支付回调")
async def alipay_notify(
    notify_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """支付宝支付回调（无需认证）"""
    service = HetongZhifuService(db)
    result = service.handle_alipay_notify(notify_data)
    
    if result:
        return "success"
    else:
        return "fail"


@router.post("/notify/wechat", summary="微信支付回调")
async def wechat_notify(
    notify_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """微信支付回调（无需认证）"""
    service = HetongZhifuService(db)
    result = service.handle_wechat_notify(notify_data)
    
    if result:
        return {"code": "SUCCESS", "message": "成功"}
    else:
        return {"code": "FAIL", "message": "失败"}


@router.get("/status/{hetong_id}", summary="获取合同支付状态")
async def get_payment_status(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取合同支付状态"""
    service = HetongZhifuService(db)
    result = service.get_payment_status_by_hetong(hetong_id)
    
    return {
        "success": True,
        "data": result
    }
