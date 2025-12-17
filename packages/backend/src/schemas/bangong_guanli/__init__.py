"""
办公管理模块数据模式
"""
from .baoxiao_schemas import (
    BaoxiaoShenqingBase,
    BaoxiaoShenqingCreate,
    BaoxiaoShenqingUpdate,
    BaoxiaoShenqingResponse,
    BaoxiaoShenqingListParams
)

from .qingjia_schemas import (
    QingjiaShenqingBase,
    QingjiaShenqingCreate,
    QingjiaShenqingUpdate,
    QingjiaShenqingResponse,
    QingjiaShenqingListParams
)

from .duiwai_fukuan_schemas import (
    DuiwaiFukuanShenqingBase,
    DuiwaiFukuanShenqingCreate,
    DuiwaiFukuanShenqingUpdate,
    DuiwaiFukuanShenqingResponse,
    DuiwaiFukuanShenqingListParams
)

from .caigou_schemas import (
    CaigouShenqingBase,
    CaigouShenqingCreate,
    CaigouShenqingUpdate,
    CaigouShenqingResponse,
    CaigouShenqingListParams
)

from .gongzuo_jiaojie_schemas import (
    GongzuoJiaojieBase,
    GongzuoJiaojieCreate,
    GongzuoJiaojieUpdate,
    GongzuoJiaojieResponse,
    GongzuoJiaojieListParams
)

__all__ = [
    # 报销申请
    "BaoxiaoShenqingBase",
    "BaoxiaoShenqingCreate",
    "BaoxiaoShenqingUpdate",
    "BaoxiaoShenqingResponse",
    "BaoxiaoShenqingListParams",
    
    # 请假申请
    "QingjiaShenqingBase",
    "QingjiaShenqingCreate",
    "QingjiaShenqingUpdate",
    "QingjiaShenqingResponse",
    "QingjiaShenqingListParams",
    
    # 对外付款申请
    "DuiwaiFukuanShenqingBase",
    "DuiwaiFukuanShenqingCreate",
    "DuiwaiFukuanShenqingUpdate",
    "DuiwaiFukuanShenqingResponse",
    "DuiwaiFukuanShenqingListParams",
    
    # 采购申请
    "CaigouShenqingBase",
    "CaigouShenqingCreate",
    "CaigouShenqingUpdate",
    "CaigouShenqingResponse",
    "CaigouShenqingListParams",
    
    # 工作交接
    "GongzuoJiaojieBase",
    "GongzuoJiaojieCreate",
    "GongzuoJiaojieUpdate",
    "GongzuoJiaojieResponse",
    "GongzuoJiaojieListParams"
]

