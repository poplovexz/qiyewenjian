"""
财务设置相关数据模型
"""
from sqlalchemy import Column, String, Integer, Text
from models.base import BaseModel

class ShoufukuanQudao(BaseModel):
    """收付款渠道表"""
    
    __tablename__ = "shoufukuan_qudao"
    __table_args__ = {"comment": "收付款渠道表"}
    
    # 基本信息
    mingcheng = Column(
        String(100),
        nullable=False,
        comment="渠道名称"
    )
    
    leixing = Column(
        String(50),
        nullable=False,
        comment="渠道类型：shoukuan(收款)、fukuan(付款)、shoufukuan(收付款)"
    )
    
    zhanghu_mingcheng = Column(
        String(200),
        nullable=True,
        comment="账户名称"
    )
    
    zhanghu_haoma = Column(
        String(100),
        nullable=True,
        comment="账户号码"
    )
    
    kaihuhang = Column(
        String(200),
        nullable=True,
        comment="开户行"
    )
    
    lianhanghao = Column(
        String(50),
        nullable=True,
        comment="联行号"
    )
    
    miaoshu = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )

class ShouruLeibie(BaseModel):
    """收入类别表"""
    
    __tablename__ = "shouru_leibie"
    __table_args__ = {"comment": "收入类别表"}
    
    # 基本信息
    mingcheng = Column(
        String(100),
        nullable=False,
        comment="类别名称"
    )
    
    bianma = Column(
        String(50),
        nullable=True,
        unique=True,
        comment="类别编码"
    )
    
    miaoshu = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )

class BaoxiaoLeibie(BaseModel):
    """报销类别表"""
    
    __tablename__ = "baoxiao_leibie"
    __table_args__ = {"comment": "报销类别表"}
    
    # 基本信息
    mingcheng = Column(
        String(100),
        nullable=False,
        comment="类别名称"
    )
    
    bianma = Column(
        String(50),
        nullable=True,
        unique=True,
        comment="类别编码"
    )
    
    miaoshu = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )

class ZhichuLeibie(BaseModel):
    """支出类别表"""
    
    __tablename__ = "zhichu_leibie"
    __table_args__ = {"comment": "支出类别表"}
    
    # 基本信息
    mingcheng = Column(
        String(100),
        nullable=False,
        comment="类别名称"
    )
    
    bianma = Column(
        String(50),
        nullable=True,
        unique=True,
        comment="类别编码"
    )
    
    fenlei = Column(
        String(100),
        nullable=True,
        comment="分类（一级分类）"
    )
    
    miaoshu = Column(
        Text,
        nullable=True,
        comment="描述"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(启用)、inactive(禁用)"
    )
