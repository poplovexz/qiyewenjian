"""
产品管理模块数据验证模式
"""

from .chanpin_fenlei_schemas import (
    ChanpinFenleiCreate,
    ChanpinFenleiUpdate,
    ChanpinFenleiResponse,
    ChanpinFenleiListResponse,
    ChanpinFenleiListParams,
    ChanpinFenleiOption,
    ChanpinFenleiListItem
)

from .chanpin_xiangmu_schemas import (
    ChanpinXiangmuCreate,
    ChanpinXiangmuUpdate,
    ChanpinXiangmuResponse,
    ChanpinXiangmuListResponse,
    ChanpinXiangmuDetailResponse,
    ChanpinXiangmuListParams,
    ChanpinXiangmuListItem
)

from .chanpin_buzou_schemas import (
    ChanpinBuzouCreate,
    ChanpinBuzouUpdate,
    ChanpinBuzouResponse,
    ChanpinBuzouBatchUpdate,
    ChanpinBuzouBatchCreate
)

__all__ = [
    # 产品分类
    "ChanpinFenleiCreate",
    "ChanpinFenleiUpdate",
    "ChanpinFenleiResponse",
    "ChanpinFenleiListResponse",
    "ChanpinFenleiListParams",
    "ChanpinFenleiOption",
    "ChanpinFenleiListItem",

    # 产品项目
    "ChanpinXiangmuCreate",
    "ChanpinXiangmuUpdate",
    "ChanpinXiangmuResponse",
    "ChanpinXiangmuListResponse",
    "ChanpinXiangmuDetailResponse",
    "ChanpinXiangmuListParams",
    "ChanpinXiangmuListItem",

    # 产品步骤
    "ChanpinBuzouCreate",
    "ChanpinBuzouUpdate",
    "ChanpinBuzouResponse",
    "ChanpinBuzouBatchUpdate",
    "ChanpinBuzouBatchCreate"
]
