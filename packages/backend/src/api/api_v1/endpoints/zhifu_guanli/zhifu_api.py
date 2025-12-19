"""
第三方支付API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.zhifu_guanli.zhifu_api_service import ZhifuApiService
from schemas.zhifu_guanli.zhifu_dingdan_schemas import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    QueryPaymentResponse
)

router = APIRouter()

@router.post("/create", response_model=CreatePaymentResponse, summary="创建第三方支付")
async def create_payment(
    payment_request: CreatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_order:create"))
):
    """
    创建第三方支付订单
    
    **支持的支付平台：**
    - weixin: 微信支付
    - zhifubao: 支付宝
    
    **微信支付方式：**
    - jsapi: 公众号支付（需要提供openid）
    - app: APP支付
    - h5: H5支付
    - native: 扫码支付
    
    **支付宝支付方式：**
    - page: 网页支付（需要提供return_url）
    - wap: 手机网页支付（需要提供return_url）
    - app: APP支付
    
    **注意事项：**
    1. 创建支付前，需要先创建支付订单
    2. 确保已配置对应的支付平台配置
    3. 微信JSAPI支付需要提供用户openid
    4. 支付宝网页支付需要提供return_url
    """
    service = ZhifuApiService(db)
    result = service.create_payment(
        dingdan_id=payment_request.dingdan_id,
        zhifu_pingtai=payment_request.zhifu_pingtai,
        zhifu_fangshi=payment_request.zhifu_fangshi,
        openid=payment_request.openid,
        return_url=payment_request.return_url,
        quit_url=payment_request.quit_url
    )
    return result

@router.get("/query/{dingdan_id}", response_model=QueryPaymentResponse, summary="查询支付订单状态")
async def query_payment(
    dingdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_order:read"))
):
    """
    查询第三方支付订单状态
    
    会向第三方平台查询订单的最新状态，并更新本地订单状态
    """
    service = ZhifuApiService(db)
    
    # 查询支付状态
    query_result = service.query_payment(dingdan_id)
    
    # 获取订单信息
    from models.zhifu_guanli import ZhifuDingdan
    dingdan = db.query(ZhifuDingdan).filter(
        ZhifuDingdan.id == dingdan_id,
        ZhifuDingdan.is_deleted == "N"
    ).first()
    
    if not dingdan:
        raise HTTPException(status_code=404, detail="支付订单不存在")
    
    return QueryPaymentResponse(
        dingdan_id=dingdan.id,
        dingdan_bianhao=dingdan.dingdan_bianhao,
        zhifu_zhuangtai=dingdan.zhifu_zhuangtai,
        zhifu_pingtai=dingdan.zhifu_pingtai,
        disanfang_dingdan_hao=dingdan.disanfang_dingdan_hao,
        disanfang_liushui_hao=dingdan.disanfang_liushui_hao,
        query_result=query_result
    )

@router.post("/close/{dingdan_id}", summary="关闭支付订单")
async def close_payment(
    dingdan_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_order:update"))
):
    """
    关闭第三方支付订单
    
    **注意事项：**
    1. 只能关闭未支付的订单
    2. 已支付的订单无法关闭，需要使用退款功能
    3. 关闭后订单状态变为cancelled
    """
    service = ZhifuApiService(db)
    result = service.close_payment(dingdan_id)
    return result
