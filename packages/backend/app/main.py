"""
主应用文件 - 重构后的模块化版本
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, users, permissions, roles, leads, audit
from .routers.contracts import template_router, party_router, payment_router, contract_router
from .routers.products import category_router, product_router, step_router
from .routers.customers import customer_router, service_record_router
from .routers import payments, audit_rules

# 创建FastAPI应用
app = FastAPI(
    title="代理记账营运内部系统 API",
    description="简化版后端服务，用于测试基础功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 基础路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "代理记账营运内部系统 API", "status": "running"}


@app.get("/api/v1/")
async def api_root():
    """API根路径"""
    return {"message": "API v1", "status": "running"}


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}


# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(roles.router)
app.include_router(leads.router)
app.include_router(audit.router)

# 合同相关路由
app.include_router(template_router)
app.include_router(party_router)
app.include_router(payment_router)
app.include_router(contract_router)

# 产品管理路由
app.include_router(category_router)
app.include_router(product_router)
app.include_router(step_router)

# 客户管理路由
app.include_router(customer_router)
app.include_router(service_record_router)

# 支付管理路由
app.include_router(payments.router)

# 审核规则路由
app.include_router(audit_rules.router)


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动简化版后端服务...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )
