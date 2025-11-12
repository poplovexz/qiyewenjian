"""
财务管理模块 Pydantic 模式
"""
from .kaipiao_schemas import (
    KaipiaoShenqingCreate,
    KaipiaoShenqingUpdate,
    KaipiaoShenqingResponse,
    KaipiaoShenqingListResponse,
    KaipiaoShenqingListParams
)
from .chengben_schemas import (
    ChengbenJiluCreate,
    ChengbenJiluUpdate,
    ChengbenJiluResponse,
    ChengbenJiluListResponse,
    ChengbenJiluListParams,
    ChengbenStatistics,
    ChengbenAnalysis
)
from .caiwu_shezhi_schemas import (
    ShoufukuanQudaoCreate,
    ShoufukuanQudaoUpdate,
    ShoufukuanQudaoResponse,
    ShoufukuanQudaoListResponse,
    ShouruLeibieCreate,
    ShouruLeibieUpdate,
    ShouruLeibieResponse,
    ShouruLeibieListResponse,
    BaoxiaoLeibieCreate,
    BaoxiaoLeibieUpdate,
    BaoxiaoLeibieResponse,
    BaoxiaoLeibieListResponse,
    ZhichuLeibieCreate,
    ZhichuLeibieUpdate,
    ZhichuLeibieResponse,
    ZhichuLeibieListResponse
)

__all__ = [
    # 开票申请
    "KaipiaoShenqingCreate",
    "KaipiaoShenqingUpdate",
    "KaipiaoShenqingResponse",
    "KaipiaoShenqingListResponse",
    "KaipiaoShenqingListParams",

    # 成本记录
    "ChengbenJiluCreate",
    "ChengbenJiluUpdate",
    "ChengbenJiluResponse",
    "ChengbenJiluListResponse",
    "ChengbenJiluListParams",
    "ChengbenStatistics",
    "ChengbenAnalysis",

    # 收付款渠道
    "ShoufukuanQudaoCreate",
    "ShoufukuanQudaoUpdate",
    "ShoufukuanQudaoResponse",
    "ShoufukuanQudaoListResponse",

    # 收入类别
    "ShouruLeibieCreate",
    "ShouruLeibieUpdate",
    "ShouruLeibieResponse",
    "ShouruLeibieListResponse",

    # 报销类别
    "BaoxiaoLeibieCreate",
    "BaoxiaoLeibieUpdate",
    "BaoxiaoLeibieResponse",
    "BaoxiaoLeibieListResponse",

    # 支出类别
    "ZhichuLeibieCreate",
    "ZhichuLeibieUpdate",
    "ZhichuLeibieResponse",
    "ZhichuLeibieListResponse"
]
