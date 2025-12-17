"""
客户管理模块 Schemas
"""
from .kehu_schemas import (
    KehuBase,
    KehuCreate,
    KehuUpdate,
    KehuResponse,
    KehuListResponse
)
from .fuwu_jilu_schemas import (
    FuwuJiluBase,
    FuwuJiluCreate,
    FuwuJiluUpdate,
    FuwuJiluResponse,
    FuwuJiluListResponse
)

__all__ = [
    # 客户相关
    "KehuBase",
    "KehuCreate", 
    "KehuUpdate",
    "KehuResponse",
    "KehuListResponse",
    
    # 服务记录相关
    "FuwuJiluBase",
    "FuwuJiluCreate",
    "FuwuJiluUpdate", 
    "FuwuJiluResponse",
    "FuwuJiluListResponse"
]
