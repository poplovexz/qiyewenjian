"""
线索主表模型
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from ..base import BaseModel

class Xiansuo(BaseModel):
    """线索表"""
    
    __tablename__ = "xiansuo"
    __table_args__ = {"comment": "线索表"}
    
    # 基本信息
    xiansuo_bianma = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="线索编码"
    )
    
    gongsi_mingcheng = Column(
        String(200),
        nullable=False,
        comment="公司名称"
    )
    
    lianxi_ren = Column(
        String(50),
        nullable=False,
        comment="联系人"
    )
    
    lianxi_dianhua = Column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    
    lianxi_youxiang = Column(
        String(100),
        nullable=True,
        comment="联系邮箱"
    )
    
    # 公司信息
    hangye_leixing = Column(
        String(100),
        nullable=True,
        comment="行业类型"
    )
    
    gongsi_guimo = Column(
        String(50),
        nullable=True,
        comment="公司规模：small-小型，medium-中型，large-大型"
    )
    
    zhuce_dizhi = Column(
        String(500),
        nullable=True,
        comment="注册地址"
    )
    
    # 需求信息
    fuwu_leixing = Column(
        String(200),
        nullable=True,
        comment="服务类型"
    )
    
    yusuan_fanwei = Column(
        String(100),
        nullable=True,
        comment="预算范围"
    )
    
    shijian_yaoqiu = Column(
        String(200),
        nullable=True,
        comment="时间要求"
    )
    
    xiangxi_xuqiu = Column(
        Text,
        nullable=True,
        comment="详细需求"
    )
    
    # 线索质量评估
    zhiliang_pinggu = Column(
        String(20),
        default="medium",
        comment="质量评估：high-高质量，medium-中等质量，low-低质量"
    )
    
    zhiliang_fenshu = Column(
        Integer,
        default=0,
        comment="质量分数（0-100）"
    )
    
    # 来源信息
    laiyuan_id = Column(
        String(36),
        ForeignKey("xiansuo_laiyuan.id"),
        nullable=False,
        comment="来源ID"
    )
    
    laiyuan_xiangxi = Column(
        String(500),
        nullable=True,
        comment="来源详细信息"
    )
    
    # 状态信息
    xiansuo_zhuangtai = Column(
        String(50),
        default="new",
        nullable=False,
        comment="线索状态"
    )
    
    # 分配信息
    fenpei_ren_id = Column(
        String(36),
        nullable=True,
        comment="分配人ID（销售人员）"
    )
    
    fenpei_shijian = Column(
        DateTime,
        nullable=True,
        comment="分配时间"
    )
    
    # 跟进信息
    shouci_genjin_shijian = Column(
        DateTime,
        nullable=True,
        comment="首次跟进时间"
    )
    
    zuijin_genjin_shijian = Column(
        DateTime,
        nullable=True,
        comment="最近跟进时间"
    )
    
    xiaci_genjin_shijian = Column(
        DateTime,
        nullable=True,
        comment="下次跟进时间"
    )
    
    genjin_cishu = Column(
        Integer,
        default=0,
        comment="跟进次数"
    )
    
    # 转化信息
    shi_zhuanhua = Column(
        String(1),
        default="N",
        comment="是否转化 Y/N"
    )
    
    zhuanhua_shijian = Column(
        DateTime,
        nullable=True,
        comment="转化时间"
    )
    
    zhuanhua_jine = Column(
        Numeric(10, 2),
        default=0.00,
        comment="转化金额"
    )
    
    kehu_id = Column(
        String(36),
        nullable=True,
        comment="转化后的客户ID"
    )
    
    # 关联关系
    laiyuan = relationship(
        "XiansuoLaiyuan",
        back_populates="xiansuo_list"
    )
    
    # 注意：状态关联通过编码字段关联，不是外键关联
    
    genjin_jilu_list = relationship(
        "XiansuoGenjin",
        back_populates="xiansuo",
        cascade="all, delete-orphan"
    )

    baojia_list = relationship(
        "XiansuoBaojia",
        back_populates="xiansuo",
        cascade="all, delete-orphan",
        order_by="XiansuoBaojia.created_at.desc()"
    )
