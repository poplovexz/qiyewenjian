"""
合同支付公共API端点（无需登录）
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from services.hetong_guanli.hetong_zhifu_public_service import HetongZhifuPublicService

router = APIRouter()


class ContractPaymentRequest(BaseModel):
    """合同支付请求模型"""
    hetong_id: str = Field(..., description="合同ID")
    zhifu_fangshi: str = Field(..., description="支付方式")
    zhifu_jine: float = Field(..., description="支付金额")


class AlipayPaymentRequest(BaseModel):
    """支付宝支付请求模型"""
    return_url: Optional[str] = Field(None, description="支付成功返回URL")
    notify_url: Optional[str] = Field(None, description="支付通知URL")


class WechatPaymentRequest(BaseModel):
    """微信支付请求模型"""
    notify_url: Optional[str] = Field(None, description="支付通知URL")


@router.get("/{contract_id}/info", summary="获取合同支付信息")
async def get_contract_payment_info(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    获取合同支付信息
    
    此接口无需登录，客户可以直接查看支付信息
    """
    try:
        service = HetongZhifuPublicService(db)
        result = service.get_contract_payment_info(contract_id)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create", summary="创建支付记录")
async def create_payment(
    payment_request: ContractPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    创建支付记录
    
    此接口无需登录，客户可以直接创建支付
    """
    try:
        service = HetongZhifuPublicService(db)
        result = service.create_payment(
            contract_id=payment_request.hetong_id,
            payment_method=payment_request.zhifu_fangshi,
            amount=payment_request.zhifu_jine
        )
        
        return {
            "success": True,
            "message": "支付记录创建成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/alipay", summary="发起支付宝支付")
async def initiate_alipay_payment(
    payment_id: str,
    alipay_request: AlipayPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    发起支付宝支付
    
    此接口无需登录，客户可以直接发起支付宝支付
    """
    try:
        service = HetongZhifuPublicService(db)
        result = service.initiate_alipay_payment(
            payment_id=payment_id,
            return_url=alipay_request.return_url,
            notify_url=alipay_request.notify_url
        )
        
        return {
            "success": True,
            "message": "支付宝支付发起成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/wechat", summary="发起微信支付")
async def initiate_wechat_payment(
    payment_id: str,
    wechat_request: WechatPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    发起微信支付
    
    此接口无需登录，客户可以直接发起微信支付
    """
    try:
        service = HetongZhifuPublicService(db)
        result = service.initiate_wechat_payment(
            payment_id=payment_id,
            notify_url=wechat_request.notify_url
        )
        
        return {
            "success": True,
            "message": "微信支付发起成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/bank-transfer", summary="选择银行转账")
async def select_bank_transfer(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    选择银行转账支付方式
    
    此接口无需登录，客户可以直接选择银行转账
    """
    try:
        service = HetongZhifuPublicService(db)
        result = service.select_bank_transfer(payment_id)
        
        return {
            "success": True,
            "message": "银行转账支付方式选择成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{contract_id}/download", summary="下载合同")
async def download_contract(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    下载合同PDF文件
    
    此接口无需登录，客户可以直接下载已签署的合同
    """
    try:
        service = HetongZhifuPublicService(db)
        file_data = service.download_contract(contract_id)
        
        from fastapi.responses import Response
        
        return Response(
            content=file_data["content"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_data['filename']}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}/status", summary="查询支付状态")
async def get_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    查询支付状态
    
    此接口无需登录，客户可以直接查询支付状态
    """
    try:
        service = HetongZhifuPublicService(db)
        status = service.get_payment_status(payment_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/alipay/notify", summary="支付宝支付通知")
async def alipay_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    支付宝支付通知回调
    
    此接口由支付宝系统调用，用于通知支付结果
    """
    try:
        service = HetongZhifuPublicService(db)
        
        # 获取通知数据
        form_data = await request.form()
        notify_data = dict(form_data)
        
        result = service.handle_alipay_notify(notify_data)
        
        return "success" if result else "fail"
        
    except Exception as e:
        print(f"支付宝通知处理失败: {e}")
        return "fail"


@router.post("/wechat/notify", summary="微信支付通知")
async def wechat_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    微信支付通知回调
    
    此接口由微信支付系统调用，用于通知支付结果
    """
    try:
        service = HetongZhifuPublicService(db)
        
        # 获取通知数据
        body = await request.body()
        
        result = service.handle_wechat_notify(body)
        
        return {
            "code": "SUCCESS" if result else "FAIL",
            "message": "成功" if result else "失败"
        }
        
    except Exception as e:
        print(f"微信支付通知处理失败: {e}")
        return {
            "code": "FAIL",
            "message": "处理失败"
        }
