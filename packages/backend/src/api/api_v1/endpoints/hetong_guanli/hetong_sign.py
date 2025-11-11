"""
合同签署相关API端点
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from services.hetong_guanli.hetong_sign_service import HetongSignService
from schemas.hetong_guanli.hetong_schemas import (
    GenerateSignLinkResponse,
    ContractSignInfoResponse,
    CustomerSignRequest,
    CustomerPaymentRequest,
    PaymentCallbackRequest,
    BankPaymentInfoRequest,
    BankPaymentInfoResponse
)

router = APIRouter()


@router.post("/{hetong_id}/generate-sign-link", response_model=GenerateSignLinkResponse, summary="生成客户签署链接")
async def generate_sign_link(
    hetong_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    为合同生成客户签署链接
    
    - 需要登录认证
    - 生成的链接30天内有效
    - 客户可以通过链接无需登录即可签署合同
    """
    service = HetongSignService(db)

    # 获取前端基础URL
    # 从请求头中获取Origin，如果没有则使用默认的前端URL
    origin = request.headers.get('origin') or request.headers.get('referer')
    if origin:
        # 移除末尾的斜杠
        base_url = origin.rstrip('/')
    else:
        # 默认使用前端URL
        base_url = "http://localhost:5174"

    return service.generate_sign_link(hetong_id, base_url)


@router.get("/sign/{sign_token}", response_model=ContractSignInfoResponse, summary="获取合同签署信息")
async def get_contract_sign_info(
    sign_token: str,
    db: Session = Depends(get_db)
):
    """
    通过签署令牌获取合同信息（无需认证）
    
    - 客户端通过签署链接访问
    - 无需登录即可查看合同内容
    - 用于客户签署页面
    """
    service = HetongSignService(db)
    return service.get_contract_by_token(sign_token)


@router.post("/sign/{sign_token}/sign", response_model=ContractSignInfoResponse, summary="客户签署合同")
async def customer_sign_contract(
    sign_token: str,
    sign_request: CustomerSignRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    客户签署合同（无需认证）
    
    - 提交电子签名
    - 更新合同状态为已签署
    - 记录签署时间和IP地址
    """
    service = HetongSignService(db)
    
    # 获取客户端IP
    client_ip = request.client.host if request.client else "unknown"
    
    return service.customer_sign_contract(sign_token, sign_request, client_ip)


@router.post("/sign/{sign_token}/pay", summary="发起支付")
async def initiate_payment(
    sign_token: str,
    payment_request: CustomerPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    发起支付（无需认证）
    
    - 客户签署后可以发起支付
    - 返回支付URL或二维码
    - 支持微信支付、支付宝、银行转账
    """
    service = HetongSignService(db)
    return service.initiate_payment(sign_token, payment_request)


@router.post("/sign/{sign_token}/payment-callback", summary="支付回调")
async def payment_callback(
    sign_token: str,
    callback_data: PaymentCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    支付回调接口
    
    - 由支付网关调用
    - 更新合同支付状态
    """
    service = HetongSignService(db)
    success = service.handle_payment_callback(sign_token, callback_data)

    return {"success": success, "message": "支付状态已更新"}


@router.post("/sign/{sign_token}/bank-payment", response_model=BankPaymentInfoResponse, summary="客户提交银行汇款信息")
async def submit_bank_payment_info(
    sign_token: str,
    payment_info: BankPaymentInfoRequest,
    db: Session = Depends(get_db)
):
    """
    客户提交银行汇款信息（无需认证）

    - 客户签署后选择银行转账
    - 提交汇款信息
    - 系统创建汇款单据并通知业务员
    """
    service = HetongSignService(db)
    return service.submit_bank_payment_info(sign_token, payment_info)

