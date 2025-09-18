"""
审核流程数据模式
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ShenheLiuchengBase(BaseModel):
    """审核流程基础模型"""
    shenhe_leixing: str = Field(..., description="审核类型")
    guanlian_id: str = Field(..., description="关联ID")
    chufa_guize_id: str = Field(..., description="触发规则ID")
    shenqing_ren_id: str = Field(..., description="申请人ID")
    shenqing_yuanyin: Optional[str] = Field(None, description="申请原因")
    zonggong_buzhou: int = Field(..., ge=1, description="总共步骤")
    beizhu: Optional[str] = Field(None, description="备注")


class ShenheLiuchengCreate(ShenheLiuchengBase):
    """创建审核流程模型"""
    pass


class ShenheLiuchengUpdate(BaseModel):
    """更新审核流程模型"""
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态")
    dangqian_buzhou: Optional[int] = Field(None, description="当前步骤")
    beizhu: Optional[str] = Field(None, description="备注")


class ShenheLiuchengResponse(BaseModel):
    """审核流程响应模型"""
    id: str
    liucheng_bianhao: str
    shenhe_leixing: str
    guanlian_id: str
    shenhe_zhuangtai: str
    chufa_guize_id: str
    dangqian_buzhou: int
    zonggong_buzhou: int
    shenqing_ren_id: str
    shenqing_yuanyin: Optional[str]
    shenqing_shijian: Optional[datetime]
    wancheng_shijian: Optional[datetime]
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class ShenheLiuchengListParams(BaseModel):
    """审核流程列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    shenhe_leixing: Optional[str] = Field(None, description="审核类型筛选")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态筛选")
    shenqing_ren_id: Optional[str] = Field(None, description="申请人筛选")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向")


class ShenheActionRequest(BaseModel):
    """审核操作请求模型"""
    shenhe_jieguo: str = Field(..., description="审核结果：tongguo、jujue、zhuanfa")
    shenhe_yijian: Optional[str] = Field(None, description="审核意见")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    fujian_miaoshu: Optional[str] = Field(None, description="附件描述")
