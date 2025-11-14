"""
支付配置管理API端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security.permissions import require_permission
from models.yonghu_guanli import Yonghu
from services.zhifu_guanli.zhifu_peizhi_service import ZhifuPeizhiService
from schemas.zhifu_guanli.zhifu_peizhi_schemas import (
    ZhifuPeizhiCreate,
    ZhifuPeizhiUpdate,
    ZhifuPeizhiResponse,
    ZhifuPeizhiListResponse
)

router = APIRouter()


@router.post("/", response_model=ZhifuPeizhiResponse, summary="创建支付配置")
async def create_zhifu_peizhi(
    peizhi_data: ZhifuPeizhiCreate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:create"))
):
    """
    创建新的支付配置
    
    - **peizhi_mingcheng**: 配置名称（必填）
    - **peizhi_leixing**: 配置类型（必填）：weixin(微信)、zhifubao(支付宝)
    - **zhuangtai**: 状态：qiyong(启用)、tingyong(停用)
    - **huanjing**: 环境：shachang(沙箱)、shengchan(生产)
    
    **微信支付配置：**
    - **weixin_appid**: 微信APPID
    - **weixin_shanghu_hao**: 微信商户号
    - **weixin_shanghu_siyao**: 微信商户私钥
    - **weixin_zhengshu_xuliehao**: 微信证书序列号
    - **weixin_api_v3_miyao**: 微信API v3密钥
    
    **支付宝配置：**
    - **zhifubao_appid**: 支付宝APPID
    - **zhifubao_shanghu_siyao**: 支付宝商户私钥
    - **zhifubao_zhifubao_gongyao**: 支付宝公钥
    
    **注意：所有敏感信息将自动加密存储**
    """
    service = ZhifuPeizhiService(db)
    return service.create_zhifu_peizhi(peizhi_data, current_user.id)


@router.get("/", response_model=ZhifuPeizhiListResponse, summary="获取支付配置列表")
async def get_zhifu_peizhi_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    peizhi_leixing: Optional[str] = Query(None, description="配置类型：weixin、zhifubao"),
    zhuangtai: Optional[str] = Query(None, description="状态：qiyong、tingyong"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:read"))
):
    """
    获取支付配置列表（敏感信息已脱敏）
    
    支持筛选和搜索：
    - 按配置类型筛选
    - 按状态筛选
    - 按配置名称或备注搜索
    """
    service = ZhifuPeizhiService(db)
    return service.get_zhifu_peizhi_list(
        page=page,
        page_size=page_size,
        peizhi_leixing=peizhi_leixing,
        zhuangtai=zhuangtai,
        search=search
    )


@router.get("/{peizhi_id}", response_model=ZhifuPeizhiResponse, summary="获取支付配置详情")
async def get_zhifu_peizhi(
    peizhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:read"))
):
    """
    根据ID获取支付配置详情（敏感信息已脱敏）
    """
    service = ZhifuPeizhiService(db)
    return service.get_zhifu_peizhi_by_id(peizhi_id)


@router.put("/{peizhi_id}", response_model=ZhifuPeizhiResponse, summary="更新支付配置")
async def update_zhifu_peizhi(
    peizhi_id: str,
    peizhi_data: ZhifuPeizhiUpdate,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:update"))
):
    """
    更新支付配置
    
    只需要提供需要更新的字段，未提供的字段将保持不变
    
    **注意：所有敏感信息将自动加密存储**
    """
    service = ZhifuPeizhiService(db)
    return service.update_zhifu_peizhi(peizhi_id, peizhi_data, current_user.id)


@router.delete("/{peizhi_id}", summary="删除支付配置")
async def delete_zhifu_peizhi(
    peizhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:delete"))
):
    """
    删除支付配置（软删除）
    """
    service = ZhifuPeizhiService(db)
    service.delete_zhifu_peizhi(peizhi_id, current_user.id)
    return {"message": "支付配置删除成功"}


@router.post("/{peizhi_id}/toggle-status", response_model=ZhifuPeizhiResponse, summary="切换配置状态")
async def toggle_zhifu_peizhi_status(
    peizhi_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(require_permission("payment_config:update"))
):
    """
    切换支付配置的启用/停用状态
    """
    service = ZhifuPeizhiService(db)
    peizhi = service.get_zhifu_peizhi_by_id(peizhi_id)
    
    # 切换状态
    new_status = 'tingyong' if peizhi.zhuangtai == 'qiyong' else 'qiyong'
    update_data = ZhifuPeizhiUpdate(zhuangtai=new_status)
    
    return service.update_zhifu_peizhi(peizhi_id, update_data, current_user.id)

