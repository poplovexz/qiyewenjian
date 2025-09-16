"""
API v1 路由聚合
"""
from fastapi import APIRouter

# 创建 API 路由器
api_router = APIRouter()

# 导入各个模块的路由
from .endpoints import auth, yonghu, jiaose

# 注册路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(yonghu.router, prefix="/users", tags=["用户管理"])
api_router.include_router(jiaose.router, prefix="/roles", tags=["角色管理"])

# 这里将来会包含其他模块的路由
# from .endpoints import customers, contracts
# api_router.include_router(customers.router, prefix="/customers", tags=["客户管理"])
# api_router.include_router(contracts.router, prefix="/contracts", tags=["合同管理"])


@api_router.get("/")
async def api_info() -> dict[str, str]:
    """API 信息"""
    return {"message": "代理记账营运内部系统 API v1", "version": "0.1.0"}
