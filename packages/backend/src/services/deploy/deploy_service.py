"""部署管理服务"""
import os
import subprocess
import threading
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pathlib import Path

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
        # 获取项目根目录
        # 当前文件: /var/www/packages/backend/src/services/deploy/deploy_service.py
        # 向上6级到达: /var/www
        self.project_root = Path(__file__).parent.parent.parent.parent.parent.parent.resolve()
    
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

    def get_git_branches(self) -> Dict[str, Any]:
        """
        获取Git分支列表

        Returns:
            Dict: 包含当前分支和所有分支列表
        """
        try:
            # 获取当前分支
            current_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd="/var/www"
            )
            current_branch = current_result.stdout.strip()

            # 获取所有本地分支
            branches_result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd="/var/www"
            )

            local_branches = [
                branch.strip()
                for branch in branches_result.stdout.split('\n')
                if branch.strip()
            ]

            # 获取所有远程分支
            remote_result = subprocess.run(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd="/var/www"
            )

            remote_branches = [
                branch.strip().replace('origin/', '')
                for branch in remote_result.stdout.split('\n')
                if branch.strip() and 'HEAD' not in branch
            ]

            # 合并并去重
            all_branches = list(set(local_branches + remote_branches))
            all_branches.sort()

            return {
                "current_branch": current_branch,
                "branches": all_branches
            }
        except Exception as e:
            return {
                "current_branch": "main",
                "branches": ["main"]
            }

    def pre_deploy_check(self, deep_check: bool = False) -> Dict[str, Any]:
        """
        部署前检查

        Args:
            deep_check: 是否执行深度检查（包括实际构建和依赖安装）

        Returns:
            Dict: 检查结果
        """
        checks = []
        errors = 0
        warnings = 0

        # 1. 检查 requirements-production.txt
        check_result = {
            "name": "依赖文件检查",
            "status": "checking",
            "message": ""
        }

        req_file = self.project_root / "packages" / "backend" / "requirements-production.txt"
        if req_file.exists():
            check_result["status"] = "success"
            check_result["message"] = "requirements-production.txt 存在"
        else:
            check_result["status"] = "error"
            check_result["message"] = f"requirements-production.txt 不存在 (路径: {req_file})"
            errors += 1

        checks.append(check_result)

        # 2. 检查数据库迁移文件
        check_result = {
            "name": "数据库迁移文件检查",
            "status": "checking",
            "message": ""
        }

        migration_dir = self.project_root / "packages" / "backend" / "migrations"
        if migration_dir.exists():
            migration_files = [f for f in migration_dir.iterdir() if f.suffix == '.sql']
            check_result["status"] = "success"
            check_result["message"] = f"找到 {len(migration_files)} 个迁移文件"
        else:
            check_result["status"] = "warning"
            check_result["message"] = f"迁移目录不存在 (路径: {migration_dir})"
            warnings += 1

        checks.append(check_result)

        # 3. 检查前端文件（快速检查，不实际构建）
        check_result = {
            "name": "前端文件检查",
            "status": "checking",
            "message": ""
        }

        frontend_dir = self.project_root / "packages" / "frontend"
        if not frontend_dir.exists():
            check_result["status"] = "error"
            check_result["message"] = f"前端目录不存在 (路径: {frontend_dir})"
            errors += 1
        else:
            # 检查关键文件
            package_json = frontend_dir / "package.json"
            vite_config = frontend_dir / "vite.config.ts"

            if not package_json.exists():
                check_result["status"] = "error"
                check_result["message"] = "package.json 不存在"
                errors += 1
            elif not vite_config.exists():
                check_result["status"] = "warning"
                check_result["message"] = "vite.config.ts 不存在"
                warnings += 1
            else:
                check_result["status"] = "success"
                check_result["message"] = "前端文件结构正常"

        checks.append(check_result)

        # 4. 依赖文件内容检查（快速检查，不实际安装）
        check_result = {
            "name": "依赖文件内容检查",
            "status": "checking",
            "message": ""
        }

        if not req_file.exists():
            check_result["status"] = "error"
            check_result["message"] = "依赖文件不存在"
            errors += 1
        else:
            try:
                # 读取依赖文件并检查格式
                with open(req_file, 'r') as f:
                    lines = f.readlines()

                # 过滤掉注释和空行
                deps = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

                if len(deps) == 0:
                    check_result["status"] = "warning"
                    check_result["message"] = "依赖文件为空"
                    warnings += 1
                else:
                    # 检查是否有明显的格式错误
                    invalid_lines = []
                    for dep in deps:
                        # 简单检查：应该包含包名，可能包含版本号
                        if not any(c.isalnum() for c in dep):
                            invalid_lines.append(dep)

                    if invalid_lines:
                        check_result["status"] = "warning"
                        check_result["message"] = f"发现 {len(invalid_lines)} 行可能有格式问题"
                        warnings += 1
                    else:
                        check_result["status"] = "success"
                        check_result["message"] = f"依赖文件格式正常 ({len(deps)} 个依赖)"
            except Exception as e:
                check_result["status"] = "warning"
                check_result["message"] = f"无法读取依赖文件: {str(e)}"
                warnings += 1

        checks.append(check_result)

        # 5. 检查后端代码
        check_result = {
            "name": "后端代码检查",
            "status": "checking",
            "message": ""
        }

        backend_dir = self.project_root / "packages" / "backend"
        if not backend_dir.exists():
            check_result["status"] = "error"
            check_result["message"] = f"后端目录不存在 (路径: {backend_dir})"
            errors += 1
        else:
            try:
                # 测试导入主应用
                result = subprocess.run(
                    ["python3", "-c", "from src.main import app; print('OK')"],
                    cwd=str(backend_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    check_result["status"] = "success"
                    check_result["message"] = "后端代码可以正常导入"
                else:
                    check_result["status"] = "error"
                    check_result["message"] = f"后端代码导入失败: {result.stderr[:200]}"
                    errors += 1
            except Exception as e:
                check_result["status"] = "warning"
                check_result["message"] = f"无法检查后端代码: {str(e)}"
                warnings += 1

        checks.append(check_result)

        # 深度检查（可选）
        if deep_check:
            # 6. 前端实际构建测试
            check_result = {
                "name": "前端构建测试（深度）",
                "status": "checking",
                "message": ""
            }

            frontend_dir = self.project_root / "packages" / "frontend"
            if not frontend_dir.exists():
                check_result["status"] = "error"
                check_result["message"] = "前端目录不存在，跳过构建测试"
                errors += 1
            else:
                try:
                    result = subprocess.run(
                        ["npm", "run", "build:prod"],
                        cwd=str(frontend_dir),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        check_result["status"] = "success"
                        check_result["message"] = "前端构建成功"
                    else:
                        check_result["status"] = "error"
                        check_result["message"] = f"前端构建失败: {result.stderr[:200]}"
                        errors += 1
                except subprocess.TimeoutExpired:
                    check_result["status"] = "error"
                    check_result["message"] = "前端构建超时"
                    errors += 1
                except Exception as e:
                    check_result["status"] = "error"
                    check_result["message"] = f"前端构建异常: {str(e)}"
                    errors += 1

            checks.append(check_result)

            # 7. 依赖实际安装测试
            check_result = {
                "name": "依赖安装测试（深度）",
                "status": "checking",
                "message": ""
            }

            req_file = self.project_root / "packages" / "backend" / "requirements-production.txt"
            if not req_file.exists():
                check_result["status"] = "error"
                check_result["message"] = "依赖文件不存在，跳过安装测试"
                errors += 1
            else:
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        venv_path = os.path.join(temp_dir, "test_venv")

                        subprocess.run(
                            ["python3", "-m", "venv", venv_path],
                            check=True,
                            capture_output=True,
                            timeout=30
                        )

                        pip_path = os.path.join(venv_path, "bin", "pip")
                        result = subprocess.run(
                            [pip_path, "install", "-r", str(req_file), "-q"],
                            capture_output=True,
                            text=True,
                            timeout=180
                        )

                        if result.returncode == 0:
                            check_result["status"] = "success"
                            check_result["message"] = "所有依赖可以正常安装"
                        else:
                            check_result["status"] = "error"
                            check_result["message"] = f"依赖安装失败: {result.stderr[:200]}"
                            errors += 1
                except subprocess.TimeoutExpired:
                    check_result["status"] = "error"
                    check_result["message"] = "依赖安装超时"
                    errors += 1
                except Exception as e:
                    check_result["status"] = "warning"
                    check_result["message"] = f"无法测试依赖安装: {str(e)}"
                    warnings += 1

            checks.append(check_result)

        # 返回结果
        overall_status = "success"
        if errors > 0:
            overall_status = "error"
        elif warnings > 0:
            overall_status = "warning"

        check_mode = "深度检查" if deep_check else "快速检查"
        return {
            "overall_status": overall_status,
            "errors": errors,
            "warnings": warnings,
            "checks": checks,
            "can_deploy": errors == 0,
            "message": f"{check_mode}完成: {errors} 个错误, {warnings} 个警告",
            "deep_check": deep_check
        }

