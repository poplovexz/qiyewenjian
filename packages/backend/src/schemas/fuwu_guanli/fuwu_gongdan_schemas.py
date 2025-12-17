"""
服务工单管理 Schemas
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class ZhixingRenInfo(BaseModel):
    """执行人简要信息"""
    id: str = Field(..., description="用户ID")
    yonghu_ming: str = Field(..., description="用户名")
    xingming: str = Field(..., description="姓名")

    class Config:
        from_attributes = True


class FuwuGongdanXiangmuBase(BaseModel):
    """服务工单项目基础模型"""
    xiangmu_mingcheng: str = Field(..., min_length=1, max_length=200, description="项目名称")
    xiangmu_miaoshu: Optional[str] = Field(None, description="项目描述")
    xiangmu_zhuangtai: str = Field(default="pending", description="项目状态")
    paixu: int = Field(default=0, description="排序")
    jihua_gongshi: Optional[Decimal] = Field(None, description="计划工时")
    shiji_gongshi: Optional[Decimal] = Field(None, description="实际工时")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    beizhu: Optional[str] = Field(None, description="备注")
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")


class FuwuGongdanXiangmuCreate(FuwuGongdanXiangmuBase):
    """创建服务工单项目模型"""
    pass


class FuwuGongdanXiangmuUpdate(BaseModel):
    """更新服务工单项目模型"""
    xiangmu_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    xiangmu_miaoshu: Optional[str] = Field(None, description="项目描述")
    xiangmu_zhuangtai: Optional[str] = Field(None, description="项目状态")
    paixu: Optional[int] = Field(None, description="排序")
    jihua_gongshi: Optional[Decimal] = Field(None, description="计划工时")
    shiji_gongshi: Optional[Decimal] = Field(None, description="实际工时")
    kaishi_shijian: Optional[datetime] = Field(None, description="开始时间")
    jieshu_shijian: Optional[datetime] = Field(None, description="结束时间")
    beizhu: Optional[str] = Field(None, description="备注")
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")


class FuwuGongdanXiangmuResponse(FuwuGongdanXiangmuBase):
    """服务工单项目响应模型"""
    id: str = Field(..., description="项目ID")
    gongdan_id: str = Field(..., description="工单ID")
    zhixing_ren: Optional[ZhixingRenInfo] = Field(None, description="执行人信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class FuwuGongdanRizhiBase(BaseModel):
    """服务工单日志基础模型"""
    caozuo_leixing: str = Field(..., description="操作类型")
    caozuo_neirong: str = Field(..., min_length=1, description="操作内容")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")


class FuwuGongdanRizhiCreate(FuwuGongdanRizhiBase):
    """创建服务工单日志模型"""
    pass


class FuwuGongdanRizhiResponse(FuwuGongdanRizhiBase):
    """服务工单日志响应模型"""
    id: str = Field(..., description="日志ID")
    gongdan_id: str = Field(..., description="工单ID")
    caozuo_ren_id: str = Field(..., description="操作人ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class FuwuGongdanBase(BaseModel):
    """服务工单基础模型"""
    hetong_id: str = Field(..., description="关联合同ID")
    kehu_id: str = Field(..., description="客户ID")
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")
    gongdan_biaoti: str = Field(..., min_length=1, max_length=200, description="工单标题")
    gongdan_miaoshu: Optional[str] = Field(None, description="工单描述")
    fuwu_leixing: str = Field(..., description="服务类型")
    youxian_ji: str = Field(default="medium", description="优先级")
    gongdan_zhuangtai: str = Field(default="created", description="工单状态")
    jihua_kaishi_shijian: Optional[datetime] = Field(None, description="计划开始时间")
    jihua_jieshu_shijian: datetime = Field(..., description="计划结束时间")
    fenpei_beizhu: Optional[str] = Field(None, description="分配备注")


class FuwuGongdanCreate(FuwuGongdanBase):
    """创建服务工单模型"""
    xiangmu_list: Optional[List[FuwuGongdanXiangmuCreate]] = Field(default=[], description="工单项目列表")


class FuwuGongdanUpdate(BaseModel):
    """更新服务工单模型"""
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")
    gongdan_biaoti: Optional[str] = Field(None, min_length=1, max_length=200, description="工单标题")
    gongdan_miaoshu: Optional[str] = Field(None, description="工单描述")
    fuwu_leixing: Optional[str] = Field(None, description="服务类型")
    youxian_ji: Optional[str] = Field(None, description="优先级")
    gongdan_zhuangtai: Optional[str] = Field(None, description="工单状态")
    jihua_kaishi_shijian: Optional[datetime] = Field(None, description="计划开始时间")
    jihua_jieshu_shijian: Optional[datetime] = Field(None, description="计划结束时间")
    shiji_kaishi_shijian: Optional[datetime] = Field(None, description="实际开始时间")
    shiji_jieshu_shijian: Optional[datetime] = Field(None, description="实际结束时间")
    fenpei_beizhu: Optional[str] = Field(None, description="分配备注")
    wancheng_qingkuang: Optional[str] = Field(None, description="完成情况说明")
    jiaofei_wenjian: Optional[str] = Field(None, description="交付文件列表")
    kehu_pingjia: Optional[str] = Field(None, description="客户评价")
    kehu_pingjia_neirong: Optional[str] = Field(None, description="客户评价内容")


class FuwuGongdanResponse(FuwuGongdanBase):
    """服务工单响应模型"""
    id: str = Field(..., description="工单ID")
    gongdan_bianhao: str = Field(..., description="工单编号")
    shiji_kaishi_shijian: Optional[datetime] = Field(None, description="实际开始时间")
    shiji_jieshu_shijian: Optional[datetime] = Field(None, description="实际结束时间")
    fenpei_shijian: Optional[datetime] = Field(None, description="分配时间")
    fenpei_ren_id: Optional[str] = Field(None, description="分配人ID")
    wancheng_qingkuang: Optional[str] = Field(None, description="完成情况说明")
    jiaofei_wenjian: Optional[str] = Field(None, description="交付文件列表")
    kehu_queren_shijian: Optional[datetime] = Field(None, description="客户确认时间")
    kehu_pingjia: Optional[str] = Field(None, description="客户评价")
    kehu_pingjia_neirong: Optional[str] = Field(None, description="客户评价内容")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人ID")
    
    # 计算属性
    is_overdue: bool = Field(..., description="是否逾期")
    progress_percentage: int = Field(..., description="进度百分比")
    
    class Config:
        from_attributes = True


class FuwuGongdanDetailResponse(FuwuGongdanResponse):
    """服务工单详情响应模型"""
    xiangmu_list: List[FuwuGongdanXiangmuResponse] = Field(default=[], description="工单项目列表")
    rizhi_list: List[FuwuGongdanRizhiResponse] = Field(default=[], description="工单日志列表")


class FuwuGongdanListParams(BaseModel):
    """服务工单列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    gongdan_bianhao: Optional[str] = Field(None, description="工单编号")
    gongdan_biaoti: Optional[str] = Field(None, description="工单标题")
    fuwu_leixing: Optional[str] = Field(None, description="服务类型")
    gongdan_zhuangtai: Optional[str] = Field(None, description="工单状态")
    youxian_ji: Optional[str] = Field(None, description="优先级")
    zhixing_ren_id: Optional[str] = Field(None, description="执行人ID")
    kehu_id: Optional[str] = Field(None, description="客户ID")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    is_overdue: Optional[bool] = Field(None, description="是否逾期")


class FuwuGongdanListResponse(BaseModel):
    """服务工单列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[FuwuGongdanResponse] = Field(..., description="工单列表")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class FuwuGongdanStatistics(BaseModel):
    """服务工单统计模型"""
    total_count: int = Field(..., description="总工单数")
    created_count: int = Field(..., description="已创建数量")
    assigned_count: int = Field(..., description="已分配数量")
    in_progress_count: int = Field(..., description="进行中数量")
    pending_review_count: int = Field(..., description="待审核数量")
    completed_count: int = Field(..., description="已完成数量")
    cancelled_count: int = Field(..., description="已取消数量")
    overdue_count: int = Field(..., description="逾期数量")
    avg_completion_days: float = Field(..., description="平均完成天数")
    completion_rate: float = Field(..., description="完成率")


# ==================== 任务项相关 Schema ====================

class KehuInfo(BaseModel):
    """客户简要信息"""
    id: str = Field(..., description="客户ID")
    kehu_mingcheng: str = Field(..., description="客户名称")

    class Config:
        from_attributes = True


class GongdanInfo(BaseModel):
    """工单简要信息"""
    id: str = Field(..., description="工单ID")
    gongdan_bianhao: str = Field(..., description="工单编号")
    gongdan_biaoti: str = Field(..., description="工单标题")
    fuwu_leixing: str = Field(..., description="服务类型")
    gongdan_zhuangtai: str = Field(..., description="工单状态")

    class Config:
        from_attributes = True


class TaskItemWithGongdanResponse(FuwuGongdanXiangmuResponse):
    """任务项响应模型（包含工单信息）"""
    gongdan: GongdanInfo = Field(..., description="工单信息")
    kehu: Optional[KehuInfo] = Field(None, description="客户信息")

    class Config:
        from_attributes = True


class TaskItemListParams(BaseModel):
    """任务项列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    xiangmu_zhuangtai: Optional[str] = Field(None, description="任务项状态筛选")
    gongdan_zhuangtai: Optional[str] = Field(None, description="工单状态筛选")
    fuwu_leixing: Optional[str] = Field(None, description="服务类型筛选")


class TaskItemListResponse(BaseModel):
    """任务项列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[TaskItemWithGongdanResponse] = Field(..., description="任务项列表")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class TaskItemStatistics(BaseModel):
    """任务项统计模型"""
    total_count: int = Field(..., description="总任务数")
    pending_count: int = Field(..., description="待处理数量")
    in_progress_count: int = Field(..., description="进行中数量")
    completed_count: int = Field(..., description="已完成数量")
    skipped_count: int = Field(..., description="已跳过数量")
    total_jihua_gongshi: float = Field(..., description="总计划工时")
    total_shiji_gongshi: float = Field(..., description="总实际工时")
    avg_completion_rate: float = Field(..., description="平均完成率")


class TaskItemStartRequest(BaseModel):
    """开始任务项请求模型"""
    pass  # 无需额外参数，从token获取当前用户


class TaskItemCompleteRequest(BaseModel):
    """完成任务项请求模型"""
    shiji_gongshi: Decimal = Field(..., ge=0, description="实际工时")
    beizhu: Optional[str] = Field(None, description="备注")


class TaskItemPauseRequest(BaseModel):
    """暂停任务项请求模型"""
    beizhu: Optional[str] = Field(None, description="备注")
