"""
合同表模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey

from sqlalchemy.orm import relationship

from ..base import BaseModel


class Hetong(BaseModel):
    """合同表"""
    
    __tablename__ = "hetong"
    __table_args__ = {"comment": "合同表"}
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    hetong_moban_id = Column(
        String(36),
        ForeignKey("hetong_moban.id"),
        nullable=False,
        comment="合同模板ID"
    )

    # 阶段2新增：报价关联
    baojia_id = Column(
        String(36),
        ForeignKey("xiansuo_baojia.id"),
        nullable=True,
        comment="关联报价ID"
    )

    # 阶段2新增：乙方主体关联
    yifang_zhuti_id = Column(
        String(36),
        ForeignKey("hetong_yifang_zhuti.id"),
        nullable=True,
        comment="乙方主体ID"
    )
    
    # 合同基本信息
    hetong_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="合同编号"
    )
    
    hetong_mingcheng = Column(
        String(200),
        nullable=False,
        comment="合同名称"
    )
    
    hetong_neirong = Column(
        Text,
        nullable=False,
        comment="合同内容"
    )
    
    # 合同状态
    hetong_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="合同状态：draft-草稿，pending-待审批，approved-已审批，signed-已签署，expired-已过期，cancelled-已取消"
    )
    
    # 时间信息
    qianshu_riqi = Column(
        DateTime,
        nullable=True,
        comment="签署日期"
    )
    
    shengxiao_riqi = Column(
        DateTime,
        nullable=True,
        comment="生效日期"
    )
    
    daoqi_riqi = Column(
        DateTime,
        nullable=False,
        comment="到期日期"
    )
    
    # 文件信息
    pdf_lujing = Column(
        String(500),
        nullable=True,
        comment="PDF文件路径"
    )
    
    qianshu_lujing = Column(
        String(500),
        nullable=True,
        comment="签署文件路径"
    )
    
    # 审批信息
    shenpi_ren_id = Column(
        String(36),
        nullable=True,
        comment="审批人ID"
    )
    
    shenpi_riqi = Column(
        DateTime,
        nullable=True,
        comment="审批日期"
    )
    
    shenpi_yijian = Column(
        Text,
        nullable=True,
        comment="审批意见"
    )

    # 阶段2新增：电子签名相关字段
    dianziqianming_lujing = Column(
        String(500),
        nullable=True,
        comment="电子签名文件路径"
    )

    qianming_ren_id = Column(
        String(36),
        nullable=True,
        comment="签名人ID"
    )

    qianming_shijian = Column(
        DateTime,
        nullable=True,
        comment="签名时间"
    )

    qianming_ip = Column(
        String(50),
        nullable=True,
        comment="签名IP地址"
    )

    qianming_beizhu = Column(
        Text,
        nullable=True,
        comment="签名备注"
    )

    # 阶段2新增：合同来源信息
    hetong_laiyuan = Column(
        String(50),
        default="manual",
        nullable=False,
        comment="合同来源：manual(手动创建)、auto_from_quote(报价自动生成)"
    )

    zidong_shengcheng = Column(
        String(1),
        default="N",
        nullable=False,
        comment="是否自动生成：Y(是)、N(否)"
    )

    # 关联关系
    hetong_moban = relationship("HetongMoban", back_populates="hetong_list")
    baojia = relationship("XiansuoBaojia", back_populates="hetong_list")
    yifang_zhuti = relationship("HetongYifangZhuti", back_populates="hetong_list")
    zhifu_dingdan_list = relationship(
        "ZhifuDingdan",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    # 新增关联关系
    zhifu_list = relationship(
        "HetongZhifu",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )

    jine_biangeng_list = relationship(
        "HetongJineBiangeng",
        back_populates="hetong",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Hetong(hetong_bianhao='{self.hetong_bianhao}', hetong_zhuangtai='{self.hetong_zhuangtai}')>"
