"""
合同签署公共API端点（无需登录）
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from services.hetong_guanli.hetong_qianshu_service import HetongQianshuService

router = APIRouter()

class ContractSignRequest(BaseModel):
    """合同签署请求模型"""
    qianshu_ren_mingcheng: str = Field(..., description="签署人姓名")
    qianshu_ren_dianhua: str = Field(..., description="签署人电话")
    qianshu_ren_youxiang: str = Field(..., description="签署人邮箱")
    qianming_tupian: str = Field(..., description="签名图片Base64")
    qianming_leixing: str = Field("draw", description="签名类型：draw(手绘)、text(文字)")

@router.get("/token/{token}", summary="根据签署令牌获取合同信息")
async def get_contract_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    根据签署令牌获取合同信息
    
    此接口无需登录，客户可以通过签署链接直接访问
    """
    try:
        service = HetongQianshuService(db)
        result = service.get_contract_by_token(token)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sign/{token}", summary="电子签署合同")
async def sign_contract(
    token: str,
    sign_request: ContractSignRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    电子签署合同
    
    此接口无需登录，客户可以直接进行电子签名
    """
    try:
        service = HetongQianshuService(db)
        
        # 获取客户端IP
        client_ip = request.client.host
        if hasattr(request, 'headers') and 'x-forwarded-for' in request.headers:
            client_ip = request.headers['x-forwarded-for'].split(',')[0].strip()
        
        # 获取用户代理信息
        user_agent = request.headers.get('user-agent', '')
        
        # 执行签署
        result = service.sign_contract(
            token=token,
            signer_name=sign_request.qianshu_ren_mingcheng,
            signer_phone=sign_request.qianshu_ren_dianhua,
            signer_email=sign_request.qianshu_ren_youxiang,
            signature_image=sign_request.qianming_tupian,
            signature_type=sign_request.qianming_leixing,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        return {
            "success": True,
            "message": "合同签署成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{contract_id}", summary="获取合同签署状态")
async def get_signing_status(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    获取合同签署状态
    
    此接口无需登录，可以公开查询签署状态
    """
    try:
        service = HetongQianshuService(db)
        status = service.get_signing_status(contract_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-link/{contract_id}", summary="创建签署链接")
async def create_signing_link(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    为合同创建签署链接
    
    注意：此接口需要在内部系统中调用，不对外公开
    """
    try:
        service = HetongQianshuService(db)
        result = service.create_signing_link(contract_id)
        
        return {
            "success": True,
            "message": "签署链接创建成功",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/verify/{token}", summary="验证签署令牌")
async def verify_signing_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    验证签署令牌是否有效
    """
    try:
        service = HetongQianshuService(db)
        is_valid = service.verify_token(token)
        
        return {
            "success": True,
            "data": {
                "is_valid": is_valid
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
