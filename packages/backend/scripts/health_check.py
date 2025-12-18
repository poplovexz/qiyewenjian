"""
系统健康检查脚本
"""
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp
import psutil
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.database import get_db, engine
from src.core.config import settings
from src.services.xiansuo_guanli.xiansuo_service import XiansuoService
from src.services.hetong_guanli.hetong_service import HetongService
from src.services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine


class SystemHealthChecker:
    """系统健康检查器"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {}
        }

    async def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        print("🔍 检查数据库健康状态...")
        
        result = {
            "status": "unknown",
            "response_time": 0,
            "connection_count": 0,
            "table_count": 0,
            "errors": []
        }

        try:
            start_time = time.time()

            # 测试数据库连接 (PTC-W0063: 使用 next() 的默认值防止 StopIteration)
            db = next(get_db(), None)
            if db is None:
                result["errors"].append("无法获取数据库连接")
                return result
            
            # 检查响应时间
            db.execute(text("SELECT 1"))
            result["response_time"] = round((time.time() - start_time) * 1000, 2)
            
            # 检查连接数
            connection_result = db.execute(text("SHOW STATUS LIKE 'Threads_connected'"))
            connection_row = connection_result.fetchone()
            if connection_row:
                result["connection_count"] = int(connection_row[1])
            
            # 检查表数量
            table_result = db.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"
            ))
            table_row = table_result.fetchone()
            if table_row:
                result["table_count"] = int(table_row[0])
            
            db.close()
            
            # 判断状态
            if result["response_time"] < 100:
                result["status"] = "healthy"
            elif result["response_time"] < 500:
                result["status"] = "warning"
            else:
                result["status"] = "critical"
                
            print(f"✓ 数据库响应时间: {result['response_time']}ms")
            print(f"✓ 活跃连接数: {result['connection_count']}")
            print(f"✓ 表数量: {result['table_count']}")
            
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
            print(f"✗ 数据库检查失败: {e}")

        return result

    async def check_api_endpoints(self) -> Dict[str, Any]:
        """检查API端点健康状态"""
        print("🌐 检查API端点健康状态...")
        
        result = {
            "status": "unknown",
            "endpoints": [],
            "success_rate": 0,
            "errors": []
        }

        # 定义要检查的端点
        endpoints = [
            {"path": "/api/v1/", "method": "GET", "expected_status": 200},
            {"path": "/api/v1/auth/me", "method": "GET", "expected_status": [200, 401]},
            {"path": "/api/v1/customers", "method": "GET", "expected_status": [200, 401]},
            {"path": "/api/v1/contracts", "method": "GET", "expected_status": [200, 401]},
            {"path": "/api/v1/audit-workflows", "method": "GET", "expected_status": [200, 401]},
        ]

        base_url = f"http://localhost:{settings.PORT}"
        successful_checks = 0

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                endpoint_result = {
                    "path": endpoint["path"],
                    "method": endpoint["method"],
                    "status": "unknown",
                    "response_time": 0,
                    "status_code": 0
                }

                try:
                    start_time = time.time()
                    
                    async with session.request(
                        endpoint["method"],
                        f"{base_url}{endpoint['path']}",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        endpoint_result["response_time"] = round((time.time() - start_time) * 1000, 2)
                        endpoint_result["status_code"] = response.status
                        
                        expected_statuses = endpoint["expected_status"]
                        if isinstance(expected_statuses, int):
                            expected_statuses = [expected_statuses]
                        
                        if response.status in expected_statuses:
                            endpoint_result["status"] = "healthy"
                            successful_checks += 1
                        else:
                            endpoint_result["status"] = "warning"
                            
                except Exception as e:
                    endpoint_result["status"] = "critical"
                    endpoint_result["error"] = str(e)

                result["endpoints"].append(endpoint_result)
                print(f"  {endpoint['path']}: {endpoint_result['status']} ({endpoint_result['response_time']}ms)")

        result["success_rate"] = round((successful_checks / len(endpoints)) * 100, 2)
        
        if result["success_rate"] >= 90:
            result["status"] = "healthy"
        elif result["success_rate"] >= 70:
            result["status"] = "warning"
        else:
            result["status"] = "critical"

        print(f"✓ API成功率: {result['success_rate']}%")
        return result

    async def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况"""
        print("💻 检查系统资源...")
        
        result = {
            "status": "unknown",
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "errors": []
        }

        try:
            # CPU使用率
            result["cpu_percent"] = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            result["memory_percent"] = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            result["disk_percent"] = round((disk.used / disk.total) * 100, 2)
            
            # 判断状态
            max_usage = max(result["cpu_percent"], result["memory_percent"], result["disk_percent"])
            if max_usage < 70:
                result["status"] = "healthy"
            elif max_usage < 85:
                result["status"] = "warning"
            else:
                result["status"] = "critical"
            
            print(f"✓ CPU使用率: {result['cpu_percent']}%")
            print(f"✓ 内存使用率: {result['memory_percent']}%")
            print(f"✓ 磁盘使用率: {result['disk_percent']}%")
            
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
            print(f"✗ 系统资源检查失败: {e}")

        return result

    async def check_business_logic(self) -> Dict[str, Any]:
        """检查业务逻辑健康状态"""
        print("🏢 检查业务逻辑...")
        
        result = {
            "status": "unknown",
            "services": [],
            "errors": []
        }

        try:
            # PTC-W0063: 使用 next() 的默认值防止 StopIteration
            db = next(get_db(), None)
            if db is None:
                result["errors"].append("无法获取数据库连接")
                return result

            # 检查线索服务
            xiansuo_service = XiansuoService(db)
            xiansuo_count = db.execute(text("SELECT COUNT(*) FROM xiansuo WHERE is_deleted = 'N'")).scalar()
            result["services"].append({
                "name": "线索服务",
                "status": "healthy" if xiansuo_count is not None else "critical",
                "data_count": xiansuo_count or 0
            })
            
            # 检查合同服务
            hetong_service = HetongService(db)
            hetong_count = db.execute(text("SELECT COUNT(*) FROM hetong WHERE is_deleted = 'N'")).scalar()
            result["services"].append({
                "name": "合同服务",
                "status": "healthy" if hetong_count is not None else "critical",
                "data_count": hetong_count or 0
            })
            
            # 检查审核服务
            workflow_engine = ShenheWorkflowEngine(db)
            audit_count = db.execute(text("SELECT COUNT(*) FROM shenhe_liucheng WHERE is_deleted = 'N'")).scalar()
            result["services"].append({
                "name": "审核服务",
                "status": "healthy" if audit_count is not None else "critical",
                "data_count": audit_count or 0
            })
            
            db.close()
            
            # 判断整体状态
            failed_services = [s for s in result["services"] if s["status"] != "healthy"]
            if len(failed_services) == 0:
                result["status"] = "healthy"
            elif len(failed_services) <= 1:
                result["status"] = "warning"
            else:
                result["status"] = "critical"
            
            for service in result["services"]:
                print(f"  {service['name']}: {service['status']} ({service['data_count']} 条记录)")
                
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
            print(f"✗ 业务逻辑检查失败: {e}")

        return result

    async def check_data_integrity(self) -> Dict[str, Any]:
        """检查数据完整性"""
        print("🔒 检查数据完整性...")
        
        result = {
            "status": "unknown",
            "checks": [],
            "errors": []
        }

        try:
            # PTC-W0063: 使用 next() 的默认值防止 StopIteration
            db = next(get_db(), None)
            if db is None:
                result["errors"].append("无法获取数据库连接")
                return result

            # 检查孤立记录
            integrity_checks = [
                {
                    "name": "孤立合同记录",
                    "query": """
                    SELECT COUNT(*) FROM hetong h 
                    LEFT JOIN xiansuo_baojia b ON h.baojia_id = b.id 
                    WHERE h.baojia_id IS NOT NULL AND b.id IS NULL AND h.is_deleted = 'N'
                    """
                },
                {
                    "name": "孤立审核记录",
                    "query": """
                    SELECT COUNT(*) FROM shenhe_jilu j 
                    LEFT JOIN shenhe_liucheng l ON j.liucheng_id = l.id 
                    WHERE l.id IS NULL AND j.is_deleted = 'N'
                    """
                },
                {
                    "name": "孤立支付记录",
                    "query": """
                    SELECT COUNT(*) FROM hetong_zhifu z 
                    LEFT JOIN hetong h ON z.hetong_id = h.id 
                    WHERE h.id IS NULL AND z.is_deleted = 'N'
                    """
                }
            ]
            
            for check in integrity_checks:
                try:
                    count = db.execute(text(check["query"])).scalar()
                    check_result = {
                        "name": check["name"],
                        "status": "healthy" if count == 0 else "warning",
                        "issue_count": count
                    }
                    result["checks"].append(check_result)
                    print(f"  {check['name']}: {check_result['status']} ({count} 个问题)")
                except Exception as e:
                    result["checks"].append({
                        "name": check["name"],
                        "status": "critical",
                        "error": str(e)
                    })
            
            db.close()
            
            # 判断整体状态
            critical_checks = [c for c in result["checks"] if c["status"] == "critical"]
            warning_checks = [c for c in result["checks"] if c["status"] == "warning"]
            
            if len(critical_checks) > 0:
                result["status"] = "critical"
            elif len(warning_checks) > 0:
                result["status"] = "warning"
            else:
                result["status"] = "healthy"
                
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
            print(f"✗ 数据完整性检查失败: {e}")

        return result

    async def run_full_health_check(self) -> Dict[str, Any]:
        """运行完整健康检查"""
        print("🏥 开始系统健康检查...\n")
        
        # 运行所有检查
        self.results["checks"]["database"] = await self.check_database_health()
        print()
        
        self.results["checks"]["api"] = await self.check_api_endpoints()
        print()
        
        self.results["checks"]["system"] = await self.check_system_resources()
        print()
        
        self.results["checks"]["business"] = await self.check_business_logic()
        print()
        
        self.results["checks"]["integrity"] = await self.check_data_integrity()
        print()
        
        # 计算整体状态
        statuses = [check["status"] for check in self.results["checks"].values()]
        if "critical" in statuses:
            self.results["overall_status"] = "critical"
        elif "warning" in statuses:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "healthy"
        
        print(f"🏥 系统整体状态: {self.results['overall_status'].upper()}")
        
        # 保存报告
        with open("health_check_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        print("📊 健康检查报告已保存到 health_check_report.json")
        
        return self.results


async def main():
    """主函数"""
    checker = SystemHealthChecker()
    await checker.run_full_health_check()


if __name__ == "__main__":
    asyncio.run(main())
