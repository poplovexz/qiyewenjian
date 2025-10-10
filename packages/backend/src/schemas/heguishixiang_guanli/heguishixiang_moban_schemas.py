"""
合规事项模板相关的Pydantic模式
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HeguishixiangMobanBase(BaseModel):
    """合规事项模板基础模式"""
    shixiang_mingcheng: str = Field(..., description="事项名称")
    shixiang_bianma: str = Field(..., description="事项编码")
    shixiang_leixing: str = Field(..., description="事项类型")
    shenbao_zhouqi: str = Field(..., description="申报周期")
    jiezhi_shijian_guize: str = Field(..., description="截止时间规则")
    tiqian_tixing_tianshu: Optional[str] = Field("15,7,3,1", description="提前提醒天数")
    shiyong_qiye_leixing: Optional[str] = Field(None, description="适用企业类型")
    shiyong_hangye: Optional[str] = Field(None, description="适用行业")
    shixiang_miaoshu: Optional[str] = Field(None, description="事项描述")
    banli_liucheng: Optional[str] = Field(None, description="办理流程说明")
    suoxu_cailiao: Optional[str] = Field(None, description="所需材料清单")
    fagui_yiju: Optional[str] = Field(None, description="法规依据")
    fengxian_dengji: Optional[str] = Field("medium", description="风险等级")
    moban_zhuangtai: Optional[str] = Field("active", description="模板状态")
    paixu: Optional[int] = Field(0, description="排序号")
    fenlei_biaoqian: Optional[str] = Field(None, description="分类标签")
    kuozhan_shuju: Optional[str] = Field(None, description="扩展数据")


class HeguishixiangMobanCreate(HeguishixiangMobanBase):
    """创建合规事项模板请求模式"""
    pass


class HeguishixiangMobanUpdate(BaseModel):
    """更新合规事项模板请求模式"""
    shixiang_mingcheng: Optional[str] = Field(None, description="事项名称")
    shixiang_bianma: Optional[str] = Field(None, description="事项编码")
    shixiang_leixing: Optional[str] = Field(None, description="事项类型")
    shenbao_zhouqi: Optional[str] = Field(None, description="申报周期")
    jiezhi_shijian_guize: Optional[str] = Field(None, description="截止时间规则")
    tiqian_tixing_tianshu: Optional[str] = Field(None, description="提前提醒天数")
    shiyong_qiye_leixing: Optional[str] = Field(None, description="适用企业类型")
    shiyong_hangye: Optional[str] = Field(None, description="适用行业")
    shixiang_miaoshu: Optional[str] = Field(None, description="事项描述")
    banli_liucheng: Optional[str] = Field(None, description="办理流程说明")
    suoxu_cailiao: Optional[str] = Field(None, description="所需材料清单")
    fagui_yiju: Optional[str] = Field(None, description="法规依据")
    fengxian_dengji: Optional[str] = Field(None, description="风险等级")
    moban_zhuangtai: Optional[str] = Field(None, description="模板状态")
    paixu: Optional[int] = Field(None, description="排序号")
    fenlei_biaoqian: Optional[str] = Field(None, description="分类标签")
    kuozhan_shuju: Optional[str] = Field(None, description="扩展数据")


class HeguishixiangMobanResponse(HeguishixiangMobanBase):
    """合规事项模板响应模式"""
    id: str = Field(..., description="模板ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建人")
    updated_by: Optional[str] = Field(None, description="更新人")

    class Config:
        from_attributes = True


class HeguishixiangMobanListParams(BaseModel):
    """合规事项模板列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")
    shixiang_leixing: Optional[str] = Field(None, description="事项类型")
    shenbao_zhouqi: Optional[str] = Field(None, description="申报周期")
    moban_zhuangtai: Optional[str] = Field(None, description="模板状态")
    fengxian_dengji: Optional[str] = Field(None, description="风险等级")


class HeguishixiangMobanListResponse(BaseModel):
    """合规事项模板列表响应模式"""
    items: List[HeguishixiangMobanResponse] = Field(..., description="模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class HeguishixiangMobanOptionsResponse(BaseModel):
    """合规事项模板选项响应模式"""
    shixiang_leixing_options: List[Dict[str, str]] = Field(..., description="事项类型选项")
    shenbao_zhouqi_options: List[Dict[str, str]] = Field(..., description="申报周期选项")
    fengxian_dengji_options: List[Dict[str, str]] = Field(..., description="风险等级选项")
    moban_zhuangtai_options: List[Dict[str, str]] = Field(..., description="模板状态选项")


class HeguishixiangMobanBatchCreateRequest(BaseModel):
    """批量创建合规事项模板请求模式"""
    templates: List[HeguishixiangMobanCreate] = Field(..., description="模板列表")


class HeguishixiangMobanBatchUpdateRequest(BaseModel):
    """批量更新合规事项模板请求模式"""
    template_ids: List[str] = Field(..., description="模板ID列表")
    update_data: HeguishixiangMobanUpdate = Field(..., description="更新数据")
