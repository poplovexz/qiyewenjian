"""
审计相关路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["审计"])


@router.get("/audit-records/statistics/my")
async def get_my_audit_statistics():
    """获取我的审计记录统计"""
    return {
        "total_records": 25,
        "pending_count": 3,
        "approved_count": 18,
        "rejected_count": 4,
        "this_month_count": 8
    }


@router.get("/audit-workflows/pending/my")
async def get_my_pending_workflows():
    """获取我的待审批工作流"""
    return {
        "items": [
            {
                "id": "workflow-1",
                "gongzuoliu_mingcheng": "合同审批流程",
                "shenqing_ren": "张三",
                "shenqing_shijian": "2024-01-15T10:00:00Z",
                "dangqian_jiedian": "部门经理审批",
                "youxianji": "高"
            },
            {
                "id": "workflow-2",
                "gongzuoliu_mingcheng": "费用报销流程",
                "shenqing_ren": "李四",
                "shenqing_shijian": "2024-01-14T14:30:00Z",
                "dangqian_jiedian": "财务审核",
                "youxianji": "中"
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }
