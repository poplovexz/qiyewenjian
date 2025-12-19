"""
成本记录相关的 Pydantic 模式
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class ChengbenJiluCreate(BaseModel):
    """创建成本记录的请求模式"""
    hetong_id: Optional[str] = Field(None, description="合同ID")
    xiangmu_id: Optional[str] = Field(None, description="项目ID")
    bumen_id: Optional[str] = Field(None, description="部门ID")
    chengben_mingcheng: str = Field(..., min_length=1, max_length=200, description="成本名称")
    chengben_leixing: str = Field(..., description="成本类型")
    chengben_fenlei: str = Field(..., description="成本分类")
    chengben_miaoshu: Optional[str] = Field(None, description="成本描述")
    chengben_jine: Decimal = Field(..., gt=0, description="成本金额")
    yusuan_jine: Optional[Decimal] = Field(None, ge=0, description="预算金额")
    fasheng_shijian: datetime = Field(..., description="发生时间")
    gongyingshang_id: Optional[str] = Field(None, description="供应商ID")
    gongyingshang_mingcheng: Optional[str] = Field(None, description="供应商名称")
    fapiao_hao: Optional[str] = Field(None, description="发票号码")
    fapiao_jine: Optional[Decimal] = Field(None, ge=0, description="发票金额")
    kuaiji_kemu: Optional[str] = Field(None, description="会计科目")
    chengben_zhongxin: Optional[str] = Field(None, description="成本中心")
    fentan_fangshi: Optional[str] = Field(None, description="分摊方式")
    fentan_bili: Optional[Decimal] = Field(None, ge=0, le=1, description="分摊比例")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    beizhu: Optional[str] = Field(None, description="备注")

class ChengbenJiluUpdate(BaseModel):
    """更新成本记录的请求模式"""
    chengben_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="成本名称")
    chengben_leixing: Optional[str] = Field(None, description="成本类型")
    chengben_fenlei: Optional[str] = Field(None, description="成本分类")
    chengben_miaoshu: Optional[str] = Field(None, description="成本描述")
    chengben_jine: Optional[Decimal] = Field(None, gt=0, description="成本金额")
    yusuan_jine: Optional[Decimal] = Field(None, ge=0, description="预算金额")
    shiji_jine: Optional[Decimal] = Field(None, ge=0, description="实际金额")
    fasheng_shijian: Optional[datetime] = Field(None, description="发生时间")
    jizhangjian: Optional[datetime] = Field(None, description="记账时间")
    gongyingshang_id: Optional[str] = Field(None, description="供应商ID")
    gongyingshang_mingcheng: Optional[str] = Field(None, description="供应商名称")
    fapiao_hao: Optional[str] = Field(None, description="发票号码")
    fapiao_jine: Optional[Decimal] = Field(None, ge=0, description="发票金额")
    fapiao_zhuangtai: Optional[str] = Field(None, description="发票状态")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态")
    kuaiji_kemu: Optional[str] = Field(None, description="会计科目")
    chengben_zhongxin: Optional[str] = Field(None, description="成本中心")
    fentan_fangshi: Optional[str] = Field(None, description="分摊方式")
    fentan_bili: Optional[Decimal] = Field(None, ge=0, le=1, description="分摊比例")
    fujian_lujing: Optional[str] = Field(None, description="附件路径")
    zhuangtai: Optional[str] = Field(None, description="状态")
    beizhu: Optional[str] = Field(None, description="备注")

class ChengbenJiluResponse(BaseModel):
    """成本记录响应模式"""
    id: str
    hetong_id: Optional[str]
    xiangmu_id: Optional[str]
    bumen_id: Optional[str]
    chengben_bianhao: str
    chengben_mingcheng: str
    chengben_leixing: str
    chengben_fenlei: str
    chengben_miaoshu: Optional[str]
    chengben_jine: Decimal
    yusuan_jine: Optional[Decimal]
    shiji_jine: Optional[Decimal]
    fasheng_shijian: datetime
    jizhangjian: Optional[datetime]
    gongyingshang_id: Optional[str]
    gongyingshang_mingcheng: Optional[str]
    fapiao_hao: Optional[str]
    fapiao_jine: Optional[Decimal]
    fapiao_zhuangtai: str
    shenhe_zhuangtai: str
    shenhe_jilu_id: Optional[str]
    shenhe_ren: Optional[str]
    shenhe_shijian: Optional[datetime]
    shenhe_yijian: Optional[str]
    kuaiji_kemu: Optional[str]
    chengben_zhongxin: Optional[str]
    fentan_fangshi: Optional[str]
    fentan_bili: Optional[Decimal]
    fujian_lujing: Optional[str]
    zhuangtai: str
    beizhu: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class ChengbenJiluListParams(BaseModel):
    """成本记录列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    hetong_id: Optional[str] = Field(None, description="合同ID")
    xiangmu_id: Optional[str] = Field(None, description="项目ID")
    bumen_id: Optional[str] = Field(None, description="部门ID")
    chengben_leixing: Optional[str] = Field(None, description="成本类型")
    chengben_fenlei: Optional[str] = Field(None, description="成本分类")
    shenhe_zhuangtai: Optional[str] = Field(None, description="审核状态")
    fapiao_zhuangtai: Optional[str] = Field(None, description="发票状态")
    zhuangtai: Optional[str] = Field(None, description="状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")

class ChengbenJiluListResponse(BaseModel):
    """成本记录列表响应模式"""
    items: List[ChengbenJiluResponse]
    total: int
    page: int
    size: int
    pages: int

class ChengbenAuditRequest(BaseModel):
    """成本审核请求模式"""
    jilu_id: str = Field(..., description="记录ID")
    shenhe_yijian: Optional[str] = Field(None, description="审核意见")
    shenhe_jieguo: str = Field(..., description="审核结果：approved(通过)、rejected(拒绝)")

class ChengbenRecordRequest(BaseModel):
    """成本入账请求模式"""
    jilu_id: str = Field(..., description="记录ID")
    shiji_jine: Decimal = Field(..., gt=0, description="实际金额")
    jizhangjian: Optional[datetime] = Field(None, description="记账时间")
    kuaiji_kemu: Optional[str] = Field(None, description="会计科目")
    chengben_zhongxin: Optional[str] = Field(None, description="成本中心")

class ChengbenStatistics(BaseModel):
    """成本统计信息"""
    total_count: int = Field(..., description="总记录数")
    draft_count: int = Field(..., description="草稿数")
    submitted_count: int = Field(..., description="已提交数")
    approved_count: int = Field(..., description="已审批数")
    recorded_count: int = Field(..., description="已入账数")
    rejected_count: int = Field(..., description="已拒绝数")
    total_amount: Decimal = Field(..., description="总成本金额")
    budget_amount: Decimal = Field(..., description="预算金额")
    actual_amount: Decimal = Field(..., description="实际金额")
    variance_amount: Decimal = Field(..., description="差异金额")
    variance_rate: Decimal = Field(..., description="差异率")

class ChengbenAnalysis(BaseModel):
    """成本分析"""
    by_type: List[dict] = Field(..., description="按类型分析")
    by_category: List[dict] = Field(..., description="按分类分析")
    by_department: List[dict] = Field(..., description="按部门分析")
    by_project: List[dict] = Field(..., description="按项目分析")
    trend_analysis: List[dict] = Field(..., description="趋势分析")

class ChengbenBudgetComparison(BaseModel):
    """成本预算对比"""
    budget_total: Decimal = Field(..., description="预算总额")
    actual_total: Decimal = Field(..., description="实际总额")
    variance_total: Decimal = Field(..., description="差异总额")
    variance_rate: Decimal = Field(..., description="差异率")
    details: List[dict] = Field(..., description="明细对比")
