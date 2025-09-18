"""
线索报价相关的Pydantic schemas
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class XiansuoBaojiaXiangmuBase(BaseModel):
    """报价项目基础模型"""
    chanpin_xiangmu_id: str = Field(..., description="产品项目ID")
    xiangmu_mingcheng: str = Field(..., description="项目名称")
    shuliang: Decimal = Field(default=Decimal("1.00"), description="数量")
    danjia: Decimal = Field(default=Decimal("0.00"), description="单价")
    danwei: str = Field(default="yuan", description="单位")
    paixu: int = Field(default=0, description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")


class XiansuoBaojiaXiangmuCreate(XiansuoBaojiaXiangmuBase):
    """创建报价项目"""
    pass


class XiansuoBaojiaXiangmuUpdate(BaseModel):
    """更新报价项目"""
    xiangmu_mingcheng: Optional[str] = Field(None, description="项目名称")
    shuliang: Optional[Decimal] = Field(None, description="数量")
    danjia: Optional[Decimal] = Field(None, description="单价")
    danwei: Optional[str] = Field(None, description="单位")
    paixu: Optional[int] = Field(None, description="排序号")
    beizhu: Optional[str] = Field(None, description="备注")


class XiansuoBaojiaXiangmuResponse(XiansuoBaojiaXiangmuBase):
    """报价项目响应模型"""
    id: str
    baojia_id: str
    xiaoji: Decimal = Field(..., description="小计")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class XiansuoBaojiaBase(BaseModel):
    """报价基础模型"""
    baojia_mingcheng: str = Field(..., description="报价名称")
    youxiao_qi: datetime = Field(..., description="有效期")
    beizhu: Optional[str] = Field(None, description="备注")


class XiansuoBaojiaCreate(XiansuoBaojiaBase):
    """创建报价"""
    xiansuo_id: str = Field(..., description="线索ID")
    xiangmu_list: List[XiansuoBaojiaXiangmuCreate] = Field(default=[], description="报价项目列表")


class XiansuoBaojiaUpdate(BaseModel):
    """更新报价"""
    baojia_mingcheng: Optional[str] = Field(None, description="报价名称")
    youxiao_qi: Optional[datetime] = Field(None, description="有效期")
    baojia_zhuangtai: Optional[str] = Field(None, description="报价状态")
    beizhu: Optional[str] = Field(None, description="备注")
    xiangmu_list: Optional[List[XiansuoBaojiaXiangmuCreate]] = Field(None, description="报价项目列表")

    @validator('baojia_zhuangtai')
    def validate_baojia_zhuangtai(cls, v):
        if v and v not in ['draft', 'sent', 'accepted', 'rejected', 'expired']:
            raise ValueError('报价状态必须是: draft, sent, accepted, rejected, expired 之一')
        return v


class XiansuoBaojiaResponse(XiansuoBaojiaBase):
    """报价响应模型"""
    id: str
    xiansuo_id: str
    baojia_bianma: str
    zongji_jine: Decimal = Field(..., description="总计金额")
    baojia_zhuangtai: str = Field(..., description="报价状态")
    is_expired: bool = Field(..., description="是否已过期")
    xiangmu_list: List[XiansuoBaojiaXiangmuResponse] = Field(default=[], description="报价项目列表")
    # 报价确认相关字段
    queren_ren_id: Optional[str] = Field(None, description="确认人ID")
    queren_shijian: Optional[datetime] = Field(None, description="确认时间")
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class XiansuoBaojiaListItem(BaseModel):
    """报价列表项"""
    id: str
    baojia_bianma: str
    baojia_mingcheng: str
    zongji_jine: Decimal
    baojia_zhuangtai: str
    youxiao_qi: datetime
    is_expired: bool
    xiangmu_count: int = Field(..., description="项目数量")
    # 报价确认相关字段
    queren_ren_id: Optional[str] = Field(None, description="确认人ID")
    queren_shijian: Optional[datetime] = Field(None, description="确认时间")
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class XiansuoBaojiaListParams(BaseModel):
    """报价列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    xiansuo_id: Optional[str] = Field(None, description="线索ID")
    baojia_zhuangtai: Optional[str] = Field(None, description="报价状态")
    search: Optional[str] = Field(None, description="搜索关键词")


class XiansuoBaojiaListResponse(BaseModel):
    """报价列表响应"""
    items: List[XiansuoBaojiaListItem]
    total: int
    page: int
    size: int
    pages: int


class XiansuoBaojiaStatistics(BaseModel):
    """报价统计"""
    total_count: int = Field(..., description="总报价数")
    draft_count: int = Field(..., description="草稿数")
    sent_count: int = Field(..., description="已发送数")
    accepted_count: int = Field(..., description="已接受数")
    rejected_count: int = Field(..., description="已拒绝数")
    expired_count: int = Field(..., description="已过期数")
    total_amount: Decimal = Field(..., description="总金额")
    accepted_amount: Decimal = Field(..., description="已接受金额")


# 产品相关的简化模型（用于报价选择）
class ChanpinFenleiOption(BaseModel):
    """产品分类选项"""
    id: str
    fenlei_mingcheng: str
    chanpin_leixing: str

    class Config:
        from_attributes = True


class ChanpinXiangmuOption(BaseModel):
    """产品项目选项"""
    id: str
    xiangmu_mingcheng: str
    xiangmu_bianma: str
    yewu_baojia: Decimal
    baojia_danwei: str
    banshi_tianshu: int
    fenlei_id: str

    class Config:
        from_attributes = True


class ChanpinDataForBaojia(BaseModel):
    """报价用产品数据"""
    zengzhi_fenlei: List[ChanpinFenleiOption] = Field(default=[], description="增值服务分类")
    daili_jizhang_fenlei: List[ChanpinFenleiOption] = Field(default=[], description="代理记账分类")
    zengzhi_xiangmu: List[ChanpinXiangmuOption] = Field(default=[], description="增值服务项目")
    daili_jizhang_xiangmu: List[ChanpinXiangmuOption] = Field(default=[], description="代理记账项目")


class XiansuoInfoForBaojia(BaseModel):
    """报价单中的线索信息"""
    id: str
    gongsi_mingcheng: str = Field(..., description="公司名称")
    lianxi_ren: str = Field(..., description="联系人")
    lianxi_dianhua: Optional[str] = Field(None, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, description="联系邮箱")

    class Config:
        from_attributes = True


class XiansuoBaojiaDetailResponse(XiansuoBaojiaBase):
    """报价详情响应模型（包含线索信息）"""
    id: str
    xiansuo_id: str
    baojia_bianma: str
    zongji_jine: Decimal = Field(..., description="总计金额")
    baojia_zhuangtai: str = Field(..., description="报价状态")
    is_expired: bool = Field(..., description="是否已过期")
    xiangmu_list: List[XiansuoBaojiaXiangmuResponse] = Field(default=[], description="报价项目列表")
    xiansuo_info: XiansuoInfoForBaojia = Field(..., description="线索信息")
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True
