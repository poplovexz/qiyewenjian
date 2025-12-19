"""部署管理API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models import Yonghu
from services.deploy.deploy_service import DeployService
from schemas.deploy.deploy_schemas import (
    DeployTriggerRequest,
    DeployStatusResponse,
    DeployLogResponse,
    DeployHistoryListResponse,
    DeployHistoryResponse,
    RollbackRequest,
)

router = APIRouter()

@router.post("/trigger", response_model=DeployStatusResponse, summary="触发部署")
def trigger_deploy(
    request: DeployTriggerRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    触发部署
    
    需要管理员权限
    """
    # TODO: 添加权限检查，只有管理员可以触发部署
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="权限不足")
    
    service = DeployService(db)
    deploy = service.trigger_deploy(request, current_user.yonghu_ming)
    
    return DeployStatusResponse(
        deploy_id=deploy.id,
        status=deploy.status.value,
        environment=deploy.environment,
        branch=deploy.branch,
        started_at=deploy.started_at,
        completed_at=deploy.completed_at,
        duration=deploy.duration,
        deployed_by=deploy.deployed_by,
        commit_hash=deploy.commit_hash,
        error_message=deploy.error_message,
    )

@router.get("/status/{deploy_id}", response_model=DeployStatusResponse, summary="获取部署状态")
def get_deploy_status(
    deploy_id: int,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取部署状态"""
    service = DeployService(db)
    status = service.get_deploy_status(deploy_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="部署记录不存在")
    
    return status

@router.get("/logs/{deploy_id}", response_model=DeployLogResponse, summary="获取部署日志")
def get_deploy_logs(
    deploy_id: int,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取部署日志"""
    service = DeployService(db)
    logs = service.get_deploy_logs(deploy_id)
    status = service.get_deploy_status(deploy_id)
    
    is_complete = False
    if status:
        is_complete = status.status in ["success", "failed", "cancelled"]
    
    return DeployLogResponse(
        deploy_id=deploy_id,
        logs=logs,
        is_complete=is_complete
    )

@router.get("/history", response_model=DeployHistoryListResponse, summary="获取部署历史")
def get_deploy_history(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    environment: Optional[str] = Query(None, description="环境筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取部署历史列表"""
    service = DeployService(db)
    items, total = service.get_deploy_history(page, size, environment, status)
    
    return DeployHistoryListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )

@router.get("/history/{deploy_id}", response_model=DeployHistoryResponse, summary="获取部署详情")
def get_deploy_detail(
    deploy_id: int,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """获取部署详情"""
    from models.deploy.deploy_history import DeployHistory

    deploy = db.query(DeployHistory).filter(
        DeployHistory.id == deploy_id,
        DeployHistory.is_deleted == "N"
    ).first()
    
    if not deploy:
        raise HTTPException(status_code=404, detail="部署记录不存在")
    
    return DeployHistoryResponse(
        id=deploy.id,
        environment=deploy.environment,
        branch=deploy.branch,
        status=deploy.status.value,
        started_at=deploy.started_at,
        completed_at=deploy.completed_at,
        duration=deploy.duration,
        deployed_by=deploy.deployed_by,
        commit_hash=deploy.commit_hash,
        description=deploy.description,
        logs=deploy.logs,
        error_message=deploy.error_message,
        created_at=deploy.created_at,
        updated_at=deploy.updated_at,
    )

@router.post("/cancel/{deploy_id}", summary="取消部署")
def cancel_deploy(
    deploy_id: int,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    取消正在运行的部署
    
    需要管理员权限
    """
    # TODO: 添加权限检查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="权限不足")
    
    service = DeployService(db)
    success = service.cancel_deploy(deploy_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="无法取消部署，可能已经完成或不存在")
    
    return {"message": "部署已取消"}

@router.post("/rollback", response_model=DeployStatusResponse, summary="回滚到指定版本")
def rollback_deploy(
    request: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    回滚到指定版本
    
    需要管理员权限
    """
    # TODO: 添加权限检查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="权限不足")

    from models.deploy.deploy_history import DeployHistory

    # 获取要回滚到的部署记录
    target_deploy = db.query(DeployHistory).filter(
        DeployHistory.id == request.deploy_id,
        DeployHistory.is_deleted == "N"
    ).first()
    
    if not target_deploy:
        raise HTTPException(status_code=404, detail="目标部署记录不存在")
    
    if target_deploy.status.value != "success":
        raise HTTPException(status_code=400, detail="只能回滚到成功的部署版本")
    
    # 创建新的部署请求（回滚）
    rollback_request = DeployTriggerRequest(
        environment=target_deploy.environment,
        branch=target_deploy.branch,
        description=f"回滚到部署 #{request.deploy_id}" + (
            f": {request.description}" if request.description else ""
        )
    )
    
    service = DeployService(db)
    deploy = service.trigger_deploy(rollback_request, current_user.yonghuming)
    
    return DeployStatusResponse(
        deploy_id=deploy.id,
        status=deploy.status.value,
        environment=deploy.environment,
        branch=deploy.branch,
        started_at=deploy.started_at,
        completed_at=deploy.completed_at,
        duration=deploy.duration,
        deployed_by=deploy.deployed_by,
        commit_hash=deploy.commit_hash,
        error_message=deploy.error_message,
    )

@router.get("/branches", summary="获取Git分支列表")
def get_git_branches(
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    获取Git分支列表

    返回当前分支和所有可用分支
    """
    service = DeployService(db)
    return service.get_git_branches()

@router.get("/pre-check", summary="部署前检查")
def pre_deploy_check(
    deep_check: bool = Query(False, description="是否执行深度检查（包括实际构建和依赖安装测试）"),
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    """
    部署前检查

    检查项目：
    - 依赖文件是否存在
    - 数据库迁移文件
    - 前端文件结构（快速检查）
    - 依赖文件内容（快速检查）
    - 后端代码检查

    如果 deep_check=true，还会执行：
    - 前端实际构建测试（耗时1-2分钟）
    - 依赖实际安装测试（耗时1-2分钟）
    """
    service = DeployService(db)
    return service.pre_deploy_check(deep_check=deep_check)
