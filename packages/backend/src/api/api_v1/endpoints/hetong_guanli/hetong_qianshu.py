"""
合同签署API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.yonghu_guanli import Yonghu
from services.hetong_guanli.hetong_qianshu_service import HetongQianshuService
from schemas.hetong_guanli import HetongQianshuCreate, HetongQianshuUpdate

router = APIRouter()


@router.post("/create-link/{hetong_id}", summary="创建合同签署链接")
async def create_qianshu_link(
    hetong_id: str,
    request: Request,
    youxiao_tianshu: int = 7,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    创建合同签署链接

    - **hetong_id**: 合同ID（必填）
    - **youxiao_tianshu**: 有效天数，默认7天
    """
    service = HetongQianshuService(db)
    result = service.create_qianshu_lianjie(hetong_id, youxiao_tianshu)

    # 生成完整的签署链接
    result["full_link"] = f"{request.base_url.scheme}://{request.base_url.netloc}{result['qianshu_lianjie']}"

    return {
        "success": True,
        "message": "签署链接创建成功",
        "data": result
    }


@router.get("/verify/{qianshu_token}", summary="验证签署令牌")
async def verify_qianshu_token(
    qianshu_token: str,
    db: Session = Depends(get_db)
):
    """
    验证签署令牌并获取合同信息（无需认证）
    
    - **qianshu_token**: 签署令牌
    """
    service = HetongQianshuService(db)
    qianshu_info = service.get_qianshu_by_token(qianshu_token)
    
    if not qianshu_info:
        raise HTTPException(status_code=404, detail="签署链接无效或已过期")
    
    return {
        "success": True,
        "data": qianshu_info
    }


@router.post("/sign/{qianshu_token}", summary="提交合同签署")
async def submit_qianshu(
    qianshu_token: str,
    qianshu_data: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """
    提交合同签署（无需认证）
    
    - **qianshu_token**: 签署令牌
    - **qianshu_data**: 签署数据
    """
    # 获取客户端IP和设备信息
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # 添加IP和设备信息到签署数据
    qianshu_data["qianshu_ip"] = client_ip
    qianshu_data["qianshu_shebei"] = user_agent
    
    service = HetongQianshuService(db)
    success = service.process_qianshu(qianshu_token, qianshu_data)
    
    if success:
        return {
            "success": True,
            "message": "合同签署成功"
        }
    else:
        raise HTTPException(status_code=400, detail="合同签署失败")


@router.get("/contract/{hetong_id}", summary="获取合同签署信息")
async def get_qianshu_by_contract(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """根据合同ID获取签署信息"""
    service = HetongQianshuService(db)
    qianshu_info = service.get_qianshu_by_hetong(hetong_id)
    
    return {
        "success": True,
        "data": qianshu_info
    }


@router.post("/cancel/{hetong_id}", summary="取消合同签署")
async def cancel_qianshu(
    hetong_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """取消合同签署"""
    service = HetongQianshuService(db)
    success = service.cancel_qianshu(hetong_id, reason)
    
    if success:
        return {
            "success": True,
            "message": "合同签署取消成功"
        }
    else:
        raise HTTPException(status_code=400, detail="取消合同签署失败")


@router.get("/status/{hetong_id}", summary="获取合同签署状态")
async def get_qianshu_status(
    hetong_id: str,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取合同签署状态"""
    try:
        service = HetongQianshuService(db)
        qianshu_info = service.get_qianshu_by_hetong(hetong_id)

        if qianshu_info:
            return {
                "success": True,
                "data": {
                    "qianshu_zhuangtai": qianshu_info["qianshu_zhuangtai"],
                    "qianshu_shijian": qianshu_info["qianshu_shijian"],
                    "qianshu_ren_mingcheng": qianshu_info["qianshu_ren_mingcheng"],
                    "youxiao_jieshu": qianshu_info["youxiao_jieshu"]
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "qianshu_zhuangtai": "weichuangjian"
                }
            }
    except Exception as e:
        # 如果表不存在或其他错误，返回未创建状态
        print(f"获取签署状态失败: {str(e)}")
        return {
            "success": True,
            "data": {
                "qianshu_zhuangtai": "weichuangjian"
            }
        }
