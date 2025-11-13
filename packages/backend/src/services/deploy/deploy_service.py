"""部署管理服务"""
import os
import subprocess
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import SessionLocal
from models.deploy.deploy_history import DeployHistory, DeployStatus
from schemas.deploy.deploy_schemas import (
    DeployTriggerRequest,
    DeployStatusResponse,
    DeployHistoryItem,
)


class DeployService:
    """部署管理服务"""
    
    # 存储正在运行的部署进程
    _running_deploys: Dict[int, subprocess.Popen] = {}
    # 存储部署日志
    _deploy_logs: Dict[int, List[str]] = {}
    
    def __init__(self, db: Session):
        self.db = db
    
    def trigger_deploy(
        self,
        request: DeployTriggerRequest,
        deployed_by: str
    ) -> DeployHistory:
        """
        触发部署
        
        Args:
            request: 部署请求
            deployed_by: 部署人用户名
        
        Returns:
            DeployHistory: 部署历史记录
        """
        # 获取当前Git提交哈希
        commit_hash = self._get_current_commit_hash()
        
        # 创建部署记录
        deploy = DeployHistory(
            environment=request.environment,
            branch=request.branch,
            commit_hash=commit_hash,
            status=DeployStatus.PENDING,
            deployed_by=deployed_by,
            description=request.description,
            started_at=datetime.now(),
        )
        
        self.db.add(deploy)
        self.db.commit()
        self.db.refresh(deploy)
        
        # 初始化日志存储
        self._deploy_logs[deploy.id] = []
        
        # 在后台线程中执行部署
        thread = threading.Thread(
            target=self._execute_deploy,
            args=(deploy.id, request)
        )
        thread.daemon = True
        thread.start()
        
        return deploy
    
    def _execute_deploy(self, deploy_id: int, request: DeployTriggerRequest):
        """
        执行部署（在后台线程中运行）

        Args:
            deploy_id: 部署ID
            request: 部署请求
        """
        # 在后台线程中创建新的数据库会话
        db = SessionLocal()

        try:
            deploy = db.query(DeployHistory).filter(
                DeployHistory.id == deploy_id
            ).first()

            if not deploy:
                return

            try:
                # 更新状态为运行中
                deploy.status = DeployStatus.RUNNING
                db.commit()

                # 确定部署脚本路径
                script_path = self._get_deploy_script_path(request.environment)

                if not os.path.exists(script_path):
                    raise FileNotFoundError(f"部署脚本不存在: {script_path}")

                # 执行部署脚本
                self._add_log(deploy_id, f"开始部署到 {request.environment} 环境...")
                self._add_log(deploy_id, f"使用脚本: {script_path}")
                self._add_log(deploy_id, f"分支: {request.branch}")
                self._add_log(deploy_id, "=" * 60)

                process = subprocess.Popen(
                    [script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd="/var/www"
                )

                self._running_deploys[deploy_id] = process

                # 实时读取输出
                for line in process.stdout:
                    line = line.rstrip()
                    self._add_log(deploy_id, line)

                process.wait()

                # 检查返回码
                if process.returncode == 0:
                    deploy.status = DeployStatus.SUCCESS
                    self._add_log(deploy_id, "=" * 60)
                    self._add_log(deploy_id, "✓ 部署成功！")
                else:
                    deploy.status = DeployStatus.FAILED
                    deploy.error_message = f"部署脚本返回错误码: {process.returncode}"
                    self._add_log(deploy_id, "=" * 60)
                    self._add_log(deploy_id, f"✗ 部署失败！错误码: {process.returncode}")

            except Exception as e:
                deploy.status = DeployStatus.FAILED
                deploy.error_message = str(e)
                self._add_log(deploy_id, "=" * 60)
                self._add_log(deploy_id, f"✗ 部署失败！错误: {str(e)}")

            finally:
                # 更新完成时间和耗时
                deploy.completed_at = datetime.now()
                if deploy.started_at:
                    duration = (deploy.completed_at - deploy.started_at).total_seconds()
                    deploy.duration = int(duration)

                # 保存日志
                deploy.logs = "\n".join(self._deploy_logs.get(deploy_id, []))

                db.commit()

                # 清理
                if deploy_id in self._running_deploys:
                    del self._running_deploys[deploy_id]

        finally:
            # 关闭数据库会话
            db.close()
    
    def get_deploy_status(self, deploy_id: int) -> Optional[DeployStatusResponse]:
        """
        获取部署状态
        
        Args:
            deploy_id: 部署ID
        
        Returns:
            DeployStatusResponse: 部署状态
        """
        deploy = self.db.query(DeployHistory).filter(
            DeployHistory.id == deploy_id,
            DeployHistory.is_deleted == "N"
        ).first()
        
        if not deploy:
            return None
        
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
    
    def get_deploy_logs(self, deploy_id: int) -> List[str]:
        """
        获取部署日志
        
        Args:
            deploy_id: 部署ID
        
        Returns:
            List[str]: 日志行列表
        """
        # 先尝试从内存中获取（正在运行的部署）
        if deploy_id in self._deploy_logs:
            return self._deploy_logs[deploy_id].copy()
        
        # 从数据库获取（已完成的部署）
        deploy = self.db.query(DeployHistory).filter(
            DeployHistory.id == deploy_id
        ).first()
        
        if deploy and deploy.logs:
            return deploy.logs.split("\n")
        
        return []
    
    def get_deploy_history(
        self,
        page: int = 1,
        size: int = 20,
        environment: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[DeployHistoryItem], int]:
        """
        获取部署历史列表
        
        Args:
            page: 页码
            size: 每页大小
            environment: 环境筛选
            status: 状态筛选
        
        Returns:
            tuple: (部署历史列表, 总数)
        """
        query = self.db.query(DeployHistory).filter(
            DeployHistory.is_deleted == "N"
        )
        
        if environment:
            query = query.filter(DeployHistory.environment == environment)
        
        if status:
            query = query.filter(DeployHistory.status == status)
        
        total = query.count()
        
        deploys = query.order_by(desc(DeployHistory.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()
        
        items = [
            DeployHistoryItem(
                id=d.id,
                environment=d.environment,
                branch=d.branch,
                status=d.status.value,
                started_at=d.started_at,
                completed_at=d.completed_at,
                duration=d.duration,
                deployed_by=d.deployed_by,
                commit_hash=d.commit_hash,
                description=d.description,
            )
            for d in deploys
        ]
        
        return items, total
    
    def cancel_deploy(self, deploy_id: int) -> bool:
        """
        取消部署
        
        Args:
            deploy_id: 部署ID
        
        Returns:
            bool: 是否成功取消
        """
        if deploy_id in self._running_deploys:
            process = self._running_deploys[deploy_id]
            process.terminate()
            
            deploy = self.db.query(DeployHistory).filter(
                DeployHistory.id == deploy_id
            ).first()
            
            if deploy:
                deploy.status = DeployStatus.CANCELLED
                deploy.completed_at = datetime.now()
                if deploy.started_at:
                    duration = (deploy.completed_at - deploy.started_at).total_seconds()
                    deploy.duration = int(duration)
                self.db.commit()
            
            return True
        
        return False
    
    def _get_deploy_script_path(self, environment: str) -> str:
        """获取部署脚本路径"""
        if environment == "production":
            return "/var/www/quick-deploy.sh"
        elif environment == "staging":
            return "/var/www/deploy-to-staging.sh"
        else:
            return "/var/www/deploy-to-development.sh"
    
    def _get_current_commit_hash(self) -> Optional[str]:
        """获取当前Git提交哈希"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd="/var/www"
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _add_log(self, deploy_id: int, message: str):
        """添加日志"""
        if deploy_id not in self._deploy_logs:
            self._deploy_logs[deploy_id] = []
        self._deploy_logs[deploy_id].append(message)

