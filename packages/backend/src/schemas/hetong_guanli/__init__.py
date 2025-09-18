"""
合同管理模块 Schemas
"""
from .hetong_moban_schemas import (
    HetongMobanBase,
    HetongMobanCreate,
    HetongMobanUpdate,
    HetongMobanResponse,
    HetongMobanListResponse,
    HetongMobanPreview
)
from .hetong_schemas import (
    HetongBase,
    HetongCreate,
    HetongUpdate,
    HetongSignRequest,
    HetongResponse,
    HetongListResponse,
    HetongPreviewRequest,
    HetongPreviewResponse
)
from .hetong_yifang_zhuti_schemas import (
    HetongYifangZhutiBase,
    HetongYifangZhutiCreate,
    HetongYifangZhutiUpdate,
    HetongYifangZhutiResponse,
    HetongYifangZhutiListResponse
)
from .hetong_zhifu_fangshi_schemas import (
    HetongZhifuFangshiBase,
    HetongZhifuFangshiCreate,
    HetongZhifuFangshiUpdate,
    HetongZhifuFangshiResponse,
    HetongZhifuFangshiListResponse
)

__all__ = [
    # 合同模板相关
    "HetongMobanBase",
    "HetongMobanCreate",
    "HetongMobanUpdate",
    "HetongMobanResponse",
    "HetongMobanListResponse",
    "HetongMobanPreview",

    # 合同相关
    "HetongBase",
    "HetongCreate",
    "HetongUpdate",
    "HetongSignRequest",
    "HetongResponse",
    "HetongListResponse",
    "HetongPreviewRequest",
    "HetongPreviewResponse",

    # 乙方主体相关
    "HetongYifangZhutiBase",
    "HetongYifangZhutiCreate",
    "HetongYifangZhutiUpdate",
    "HetongYifangZhutiResponse",
    "HetongYifangZhutiListResponse",

    # 支付方式相关
    "HetongZhifuFangshiBase",
    "HetongZhifuFangshiCreate",
    "HetongZhifuFangshiUpdate",
    "HetongZhifuFangshiResponse",
    "HetongZhifuFangshiListResponse"
]
