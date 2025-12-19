"""
工作交接单数据模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class GongzuoJiaojieBase(BaseModel):
    """工作交接单基础模式"""
    jieshou_ren_id: str = Field(..., description="接收人ID")
    jiaojie_yuanyin: str = Field(..., description="交接原因")
    jiaojie_shijian: datetime = Field(..., description="交接时间")
    jiaojie_neirong: Optional[str] = Field(None, description="交接内容")
    wenjian_qingdan: Optional[str] = Field(None, description="文件清单")
    shebei_qingdan: Optional[str] = Field(None, description="设备清单")
    zhanghu_qingdan: Optional[str] = Field(None, description="账号清单")
    daiban_shixiang: Optional[str] = Field(None, description="待办事项")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")

class GongzuoJiaojieCreate(GongzuoJiaojieBase):
    """创建工作交接单模式"""
    pass

class GongzuoJiaojieUpdate(BaseModel):
    """更新工作交接单模式"""
    jieshou_ren_id: Optional[str] = Field(None, description="接收人ID")
    jiaojie_yuanyin: Optional[str] = Field(None, description="交接原因")
    jiaojie_shijian: Optional[datetime] = Field(None, description="交接时间")
    jiaojie_neirong: Optional[str] = Field(None, description="交接内容")
    wenjian_qingdan: Optional[str] = Field(None, description="文件清单")
    shebei_qingdan: Optional[str] = Field(None, description="设备清单")
    zhanghu_qingdan: Optional[str] = Field(None, description="账号清单")
    daiban_shixiang: Optional[str] = Field(None, description="待办事项")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    jiaojie_zhuangtai: Optional[str] = Field(None, description="交接状态")
    queren_ren_id: Optional[str] = Field(None, description="确认人ID")
    beizhu: Optional[str] = Field(None, description="备注")

class GongzuoJiaojieResponse(GongzuoJiaojieBase):
    """工作交接单响应模式"""
    id: str
    jiaojie_bianhao: str
    jiaojie_ren_id: str
    jiaojie_zhuangtai: str
    queren_ren_id: Optional[str]
    queren_shijian: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    jiaojie_ren_xingming: Optional[str] = Field(None, description="交接人姓名")
    jieshou_ren_xingming: Optional[str] = Field(None, description="接收人姓名")
    queren_ren_xingming: Optional[str] = Field(None, description="确认人姓名")
    
    class Config:
        from_attributes = True

class GongzuoJiaojieListParams(BaseModel):
    """工作交接单列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    jiaojie_zhuangtai: Optional[str] = Field(None, description="交接状态筛选")
    jiaojie_yuanyin: Optional[str] = Field(None, description="交接原因筛选")
    jiaojie_ren_id: Optional[str] = Field(None, description="交接人ID筛选")
    jieshou_ren_id: Optional[str] = Field(None, description="接收人ID筛选")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    search: Optional[str] = Field(None, description="搜索关键词")
