"""
API v1 路由聚合
"""
from fastapi import APIRouter

# 创建 API 路由器
api_router = APIRouter()

# 导入各个模块的路由
from .endpoints import auth, yonghu
from .endpoints.kehu_guanli import kehu, fuwu_jilu
from .endpoints.yonghu_guanli import jiaose as role_api, quanxian
from .endpoints.chanpin_guanli import chanpin_fenlei, chanpin_xiangmu, chanpin_buzou

# 注册路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(yonghu.router, prefix="/users", tags=["用户管理"])

# 用户管理模块路由
api_router.include_router(role_api.router, prefix="/user-management/roles", tags=["角色管理"])
api_router.include_router(quanxian.router, prefix="/user-management/permissions", tags=["权限管理"])

# 客户管理模块路由
api_router.include_router(kehu.router, prefix="/customers", tags=["客户管理"])
api_router.include_router(fuwu_jilu.router, prefix="/service-records", tags=["服务记录管理"])

# 产品管理模块路由
api_router.include_router(chanpin_fenlei.router, prefix="/product-management/categories", tags=["产品分类管理"])
api_router.include_router(chanpin_xiangmu.router, prefix="/product-management/products", tags=["产品项目管理"])
api_router.include_router(chanpin_buzou.router, prefix="/product-management", tags=["产品步骤管理"])

# 这里将来会包含其他模块的路由
# from .endpoints import contracts
# api_router.include_router(contracts.router, prefix="/contracts", tags=["合同管理"])


@api_router.get("/")
async def api_info() -> dict[str, str]:
    """API 信息"""
    return {"message": "代理记账营运内部系统 API v1", "version": "0.1.0"}
