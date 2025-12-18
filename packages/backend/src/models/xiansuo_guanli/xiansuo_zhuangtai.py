"""
线索状态表模型
"""
from sqlalchemy import Column, String, Integer
from ..base import BaseModel


class XiansuoZhuangtai(BaseModel):
    """线索状态表"""
    
    __tablename__ = "xiansuo_zhuangtai"
    __table_args__ = {"comment": "线索状态表"}
    
    # 基本信息
    zhuangtai_mingcheng = Column(
        String(50),
        nullable=False,
        comment="状态名称"
    )
    
    zhuangtai_bianma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="状态编码"
    )
    
    zhuangtai_leixing = Column(
        String(50),
        nullable=False,
        comment="状态类型：initial-初始，processing-处理中，success-成功，failed-失败"
    )
    
    # 流程信息
    shangyige_zhuangtai = Column(
        String(50),
        nullable=True,
        comment="上一个状态编码"
    )
    
    xiayige_zhuangtai = Column(
        String(500),
        nullable=True,
        comment="下一个状态编码（多个用逗号分隔）"
    )
    
    # 显示信息
    yanse_bianma = Column(
        String(20),
        default="#409EFF",
        comment="颜色编码"
    )
    
    tubiao_mingcheng = Column(
        String(50),
        nullable=True,
        comment="图标名称"
    )
    
    # 配置信息
    shi_zhongzhong_zhuangtai = Column(
        String(1),
        default="N",
        comment="是否终止状态 Y/N"
    )
    
    shi_chenggong_zhuangtai = Column(
        String(1),
        default="N",
        comment="是否成功状态 Y/N"
    )
    
    # 排序和状态
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active-启用，inactive-停用"
    )
    
    miaoshu = Column(
        String(500),
        nullable=True,
        comment="描述"
    )
    
    # 注意：与线索表通过状态编码关联，不是直接外键关联
