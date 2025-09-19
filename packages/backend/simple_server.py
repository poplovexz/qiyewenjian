#!/usr/bin/env python3
"""
简化的FastAPI服务器，用于测试基础功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="代理记账营运内部系统",
    description="简化版本用于测试",
    version="1.0.0"
)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "status": "healthy",
        "service": "proxy-accounting-backend",
        "message": "服务运行正常"
    }

# 模拟登录接口
@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """模拟登录"""
    if credentials.get("yonghu_ming") == "admin" and credentials.get("mima") == "admin123":
        return {
            "access_token": "test-token-12345",
            "token_type": "bearer",
            "user": {
                "id": "admin-id",
                "yonghu_ming": "admin",
                "xing_ming": "管理员"
            }
        }
    return {"error": "Invalid credentials"}

# 模拟审核统计接口
@app.get("/api/v1/audit-records/statistics/my")
async def get_audit_statistics():
    """获取审核统计"""
    return {
        "total_pending": 5,
        "total_approved": 12,
        "total_rejected": 2,
        "total_transferred": 1,
        "this_month_processed": 8,
        "avg_processing_time": 2.5
    }

# 模拟待审核任务接口
@app.get("/api/v1/audit-workflows/pending/my")
async def get_pending_audits():
    """获取待审核任务"""
    return {
        "items": [
            {
                "id": "1",
                "title": "合同金额变更审核",
                "type": "contract_amount_change",
                "status": "pending",
                "created_at": "2024-01-15T10:00:00Z",
                "priority": "high"
            },
            {
                "id": "2", 
                "title": "报价折扣审核",
                "type": "quote_discount",
                "status": "pending",
                "created_at": "2024-01-15T09:30:00Z",
                "priority": "medium"
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }

if __name__ == "__main__":
    print("🚀 启动简化版后端服务...")
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
