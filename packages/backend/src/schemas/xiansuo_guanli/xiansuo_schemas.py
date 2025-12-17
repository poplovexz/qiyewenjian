"""
线索相关的 Pydantic 模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from .xiansuo_laiyuan_schemas import XiansuoLaiyuanResponse
from .xiansuo_genjin_schemas import XiansuoGenjinListItem


class XiansuoBase(BaseModel):
    """线索基础模式"""
    gongsi_mingcheng: str = Field(..., min_length=1, max_length=200, description="公司名称")
    lianxi_ren: str = Field(..., min_length=1, max_length=50, description="联系人")
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    hangye_leixing: Optional[str] = Field(None, max_length=100, description="行业类型")
    gongsi_guimo: Optional[str] = Field(None, description="公司规模：small-小型，medium-中型，large-大型")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    fuwu_leixing: Optional[str] = Field(None, max_length=200, description="服务类型")
    yusuan_fanwei: Optional[str] = Field(None, max_length=100, description="预算范围")
    shijian_yaoqiu: Optional[str] = Field(None, max_length=200, description="时间要求")
    xiangxi_xuqiu: Optional[str] = Field(None, description="详细需求")
    zhiliang_pinggu: Optional[str] = Field("medium", description="质量评估：high-高质量，medium-中等质量，low-低质量")
    zhiliang_fenshu: Optional[int] = Field(0, ge=0, le=100, description="质量分数（0-100）")
    laiyuan_id: str = Field(..., description="来源ID")
    laiyuan_xiangxi: Optional[str] = Field(None, max_length=500, description="来源详细信息")


class XiansuoCreate(XiansuoBase):
    """创建线索模式"""
    pass


class XiansuoUpdate(BaseModel):
    """更新线索模式"""
    gongsi_mingcheng: Optional[str] = Field(None, min_length=1, max_length=200, description="公司名称")
    lianxi_ren: Optional[str] = Field(None, min_length=1, max_length=50, description="联系人")
    lianxi_dianhua: Optional[str] = Field(None, max_length=20, description="联系电话")
    lianxi_youxiang: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    hangye_leixing: Optional[str] = Field(None, max_length=100, description="行业类型")
    gongsi_guimo: Optional[str] = Field(None, description="公司规模")
    zhuce_dizhi: Optional[str] = Field(None, max_length=500, description="注册地址")
    fuwu_leixing: Optional[str] = Field(None, max_length=200, description="服务类型")
    yusuan_fanwei: Optional[str] = Field(None, max_length=100, description="预算范围")
    shijian_yaoqiu: Optional[str] = Field(None, max_length=200, description="时间要求")
    xiangxi_xuqiu: Optional[str] = Field(None, description="详细需求")
    zhiliang_pinggu: Optional[str] = Field(None, description="质量评估")
    zhiliang_fenshu: Optional[int] = Field(None, ge=0, le=100, description="质量分数")
    laiyuan_id: Optional[str] = Field(None, description="来源ID")
    laiyuan_xiangxi: Optional[str] = Field(None, max_length=500, description="来源详细信息")


class XiansuoStatusUpdate(BaseModel):
    """线索状态更新模式"""
    xiansuo_zhuangtai: str = Field(..., description="线索状态")
    beizhu: Optional[str] = Field(None, max_length=500, description="状态变更备注")


class XiansuoAssignUpdate(BaseModel):
    """线索分配更新模式"""
    fenpei_ren_id: str = Field(..., description="分配人ID（销售人员）")
    beizhu: Optional[str] = Field(None, max_length=500, description="分配备注")


class XiansuoResponse(XiansuoBase):
    """线索响应模式"""
    id: str
    xiansuo_bianma: str
    xiansuo_zhuangtai: str
    fenpei_ren_id: Optional[str]
    fenpei_shijian: Optional[datetime]
    shouci_genjin_shijian: Optional[datetime]
    zuijin_genjin_shijian: Optional[datetime]
    xiaci_genjin_shijian: Optional[datetime]
    genjin_cishu: int
    shi_zhuanhua: str
    zhuanhua_shijian: Optional[datetime]
    zhuanhua_jine: Decimal
    kehu_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class XiansuoListItem(BaseModel):
    """线索列表项模式"""
    id: str
    xiansuo_bianma: str
    gongsi_mingcheng: str
    lianxi_ren: str
    lianxi_dianhua: Optional[str]
    lianxi_youxiang: Optional[str]
    hangye_leixing: Optional[str]
    gongsi_guimo: Optional[str]
    zhuce_dizhi: Optional[str]
    fuwu_leixing: Optional[str]
    yusuan_fanwei: Optional[str]
    shijian_yaoqiu: Optional[str]
    xiangxi_xuqiu: Optional[str]
    zhiliang_pinggu: str
    zhiliang_fenshu: int
    laiyuan_id: str
    laiyuan_xiangxi: Optional[str]
    xiansuo_zhuangtai: str
    fenpei_ren_id: Optional[str]
    zuijin_genjin_shijian: Optional[datetime]
    xiaci_genjin_shijian: Optional[datetime]
    genjin_cishu: int
    shi_zhuanhua: str
    zhuanhua_jine: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class XiansuoListResponse(BaseModel):
    """线索列表响应模式"""
    items: List[XiansuoListItem]
    total: int
    page: int
    size: int


class XiansuoDetailResponse(XiansuoResponse):
    """线索详情响应模式"""
    laiyuan: Optional[XiansuoLaiyuanResponse] = None
    genjin_jilu_list: List[XiansuoGenjinListItem] = []


class XiansuoStatistics(BaseModel):
    """线索统计模式"""
    total_xiansuo: int = Field(description="总线索数")
    new_xiansuo: int = Field(description="新线索数")
    following_xiansuo: int = Field(description="跟进中线索数")
    interested_xiansuo: int = Field(description="有意向线索数")
    quoted_xiansuo: int = Field(description="已报价线索数")
    won_xiansuo: int = Field(description="成交线索数")
    lost_xiansuo: int = Field(description="无效线索数")
    zhuanhua_lv: Decimal = Field(description="转化率（%）")
    pingjun_zhuanhua_zhouzqi: int = Field(description="平均转化周期（天）")
    pingjun_zhuanhua_jine: Decimal = Field(description="平均转化金额")
