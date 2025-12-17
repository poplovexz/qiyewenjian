"""
合同签署相关API端点
"""
from fastapi import APIRouter, Depends, Request, HTTPException
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
    BankPaymentInfoResponse,
    PaymentInitiateResponse,
    PaymentCallbackResponse,
    AvailablePaymentMethodsResponse
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


@router.post("/sign/{sign_token}/pay", response_model=PaymentInitiateResponse, summary="发起支付")
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


@router.post("/sign/{sign_token}/payment-callback", response_model=PaymentCallbackResponse, summary="支付回调")
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


@router.get("/sign/{sign_token}/available-payment-methods", response_model=AvailablePaymentMethodsResponse, summary="获取可用的支付方式")
async def get_available_payment_methods(
    sign_token: str,
    db: Session = Depends(get_db)
):
    """
    获取可用的支付方式（无需认证）

    - 优先返回合同乙方主体关联的支付方式
    - 如果没有关联，则返回系统中所有启用的支付方式
    - 包括微信支付、支付宝、银行转账等
    - 用于客户签署页面显示可用的支付选项
    """
    from models.zhifu_guanli import ZhifuPeizhi
    from models.hetong_guanli import Hetong, HetongZhifuFangshi

    # 验证签署令牌
    hetong = db.query(Hetong).filter(
        Hetong.sign_token == sign_token,
        Hetong.is_deleted == "N"
    ).first()

    if not hetong:
        raise HTTPException(status_code=404, detail="签署链接无效")

    # 构建可用支付方式列表
    available_methods = []
    has_wechat = False
    has_alipay = False

    # 如果合同有乙方主体，优先查找该主体关联的支付方式
    if hetong.yifang_zhuti_id:
        zhifu_fangshi_list = db.query(HetongZhifuFangshi).join(
            ZhifuPeizhi, HetongZhifuFangshi.zhifu_peizhi_id == ZhifuPeizhi.id
        ).filter(
            HetongZhifuFangshi.yifang_zhuti_id == hetong.yifang_zhuti_id,
            HetongZhifuFangshi.zhifu_zhuangtai == "active",
            HetongZhifuFangshi.is_deleted == "N",
            ZhifuPeizhi.zhuangtai == "qiyong",
            ZhifuPeizhi.is_deleted == "N"
        ).all()

        # 检查是否有微信支付和支付宝
        for fangshi in zhifu_fangshi_list:
            if fangshi.zhifu_peizhi.peizhi_leixing == "weixin":
                has_wechat = True
            elif fangshi.zhifu_peizhi.peizhi_leixing == "zhifubao":
                has_alipay = True

    # 如果没有找到乙方主体关联的支付方式，则查询所有启用的支付配置
    if not has_wechat and not has_alipay:
        payment_configs = db.query(ZhifuPeizhi).filter(
            ZhifuPeizhi.zhuangtai == "qiyong",
            ZhifuPeizhi.is_deleted == "N"
        ).all()

        # 检查是否有微信支付配置
        has_wechat = any(p.peizhi_leixing == "weixin" for p in payment_configs)
        # 检查是否有支付宝配置
        has_alipay = any(p.peizhi_leixing == "zhifubao" for p in payment_configs)

    # 添加微信支付
    if has_wechat:
        available_methods.append({
            "method": "wechat",
            "label": "微信支付",
            "icon": "wechat",
            "description": "使用微信扫码支付"
        })

    # 添加支付宝
    if has_alipay:
        available_methods.append({
            "method": "alipay",
            "label": "支付宝",
            "icon": "alipay",
            "description": "使用支付宝扫码支付"
        })

    # 银行转账始终可用
    available_methods.append({
        "method": "bank",
        "label": "银行转账",
        "icon": "bank",
        "description": "通过银行转账支付"
    })

    return {
        "available_methods": available_methods,
        "has_online_payment": has_wechat or has_alipay
    }


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


@router.get("/sign/{sign_token}/payment-status", summary="查询支付状态")
async def get_payment_status(
    sign_token: str,
    db: Session = Depends(get_db)
):
    """
    查询支付状态（无需认证）

    - 用于前端轮询查询支付是否完成
    - 返回支付状态和相关信息
    """
    service = HetongSignService(db)
    return service.get_payment_status(sign_token)


@router.post("/sign/{sign_token}/test-payment-success", summary="测试：模拟支付成功")
async def test_payment_success(
    sign_token: str,
    db: Session = Depends(get_db)
):
    """
    测试接口：模拟支付成功（仅用于开发测试）

    - 直接更新合同支付状态为已支付
    - 生产环境应该删除此接口
    """
    from models.hetong_guanli import Hetong
    from datetime import datetime

    hetong = db.query(Hetong).filter(
        Hetong.sign_token == sign_token,
        Hetong.is_deleted == "N"
    ).first()

    if not hetong:
        raise HTTPException(status_code=404, detail="签署链接无效")

    # 更新支付状态
    hetong.payment_status = "paid"
    hetong.paid_at = datetime.now()
    hetong.payment_transaction_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    hetong.updated_at = datetime.now()

    db.commit()

    return {
        "success": True,
        "message": "支付状态已更新为成功（测试）"
    }
