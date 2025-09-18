"""
线索管理模块 Pydantic 模式
"""
from .xiansuo_schemas import (
    XiansuoCreate,
    XiansuoUpdate,
    XiansuoResponse,
    XiansuoListResponse,
    XiansuoDetailResponse,
    XiansuoStatusUpdate,
    XiansuoAssignUpdate,
    XiansuoStatistics
)
from .xiansuo_laiyuan_schemas import (
    XiansuoLaiyuanCreate,
    XiansuoLaiyuanUpdate,
    XiansuoLaiyuanResponse,
    XiansuoLaiyuanListResponse
)
from .xiansuo_zhuangtai_schemas import (
    XiansuoZhuangtaiCreate,
    XiansuoZhuangtaiUpdate,
    XiansuoZhuangtaiResponse,
    XiansuoZhuangtaiListResponse
)
from .xiansuo_genjin_schemas import (
    XiansuoGenjinCreate,
    XiansuoGenjinUpdate,
    XiansuoGenjinResponse,
    XiansuoGenjinListResponse
)
from .xiansuo_baojia_schemas import (
    XiansuoBaojiaCreate,
    XiansuoBaojiaUpdate,
    XiansuoBaojiaResponse,
    XiansuoBaojiaListResponse,
    XiansuoBaojiaStatistics,
    XiansuoBaojiaXiangmuCreate,
    XiansuoBaojiaXiangmuResponse,
    ChanpinDataForBaojia
)

__all__ = [
    # 线索主表
    "XiansuoCreate",
    "XiansuoUpdate", 
    "XiansuoResponse",
    "XiansuoListResponse",
    "XiansuoDetailResponse",
    "XiansuoStatusUpdate",
    "XiansuoAssignUpdate",
    "XiansuoStatistics",
    
    # 线索来源
    "XiansuoLaiyuanCreate",
    "XiansuoLaiyuanUpdate",
    "XiansuoLaiyuanResponse",
    "XiansuoLaiyuanListResponse",
    
    # 线索状态
    "XiansuoZhuangtaiCreate",
    "XiansuoZhuangtaiUpdate",
    "XiansuoZhuangtaiResponse",
    "XiansuoZhuangtaiListResponse",
    
    # 线索跟进
    "XiansuoGenjinCreate",
    "XiansuoGenjinUpdate",
    "XiansuoGenjinResponse",
    "XiansuoGenjinListResponse",

    # 线索报价
    "XiansuoBaojiaCreate",
    "XiansuoBaojiaUpdate",
    "XiansuoBaojiaResponse",
    "XiansuoBaojiaListResponse",
    "XiansuoBaojiaStatistics",
    "XiansuoBaojiaXiangmuCreate",
    "XiansuoBaojiaXiangmuResponse",
    "ChanpinDataForBaojia"
]
