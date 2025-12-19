"""
办公管理模块服务
"""
from .baoxiao_service import BaoxiaoService
from .qingjia_service import QingjiaService
from .duiwai_fukuan_service import DuiwaiFukuanService
from .caigou_service import CaigouService
from .gongzuo_jiaojie_service import GongzuoJiaojieService

__all__ = [
    "BaoxiaoService",
    "QingjiaService",
    "DuiwaiFukuanService",
    "CaigouService",
    "GongzuoJiaojieService",
]
