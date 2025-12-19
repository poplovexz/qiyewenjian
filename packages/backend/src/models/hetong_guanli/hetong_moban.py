"""
合同模板表模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship

from ..base import BaseModel

class HetongMoban(BaseModel):
    """合同模板表"""

    __tablename__ = "hetong_moban"
    __table_args__ = {"comment": "合同模板表"}

    # 基本信息
    moban_mingcheng = Column(
        String(200),
        nullable=False,
        comment="模板名称"
    )

    moban_bianma = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="模板编码"
    )

    hetong_leixing = Column(
        String(50),
        nullable=False,
        comment="合同类型：daili_jizhang(代理记账合同)、zengzhi_fuwu(增值服务合同)、zixun_fuwu(咨询服务合同)"
    )

    # 模板内容
    moban_neirong = Column(
        Text,
        nullable=False,
        comment="模板内容（支持HTML格式和变量占位符）"
    )

    # 变量配置
    bianliang_peizhi = Column(
        Text,
        nullable=True,
        comment="变量配置（JSON格式，定义可用变量和默认值）"
    )

    # 版本管理
    banben_hao = Column(
        String(20),
        nullable=False,
        default="1.0",
        comment="版本号"
    )

    shi_dangqian_banben = Column(
        String(1),
        default="Y",
        comment="是否当前版本：Y(是)、N(否)"
    )

    # 分类和状态
    moban_fenlei = Column(
        String(50),
        nullable=True,
        comment="模板分类：biaozhun(标准模板)、dingzhi(定制模板)"
    )

    moban_zhuangtai = Column(
        String(20),
        default="draft",
        comment="模板状态：draft(草稿)、active(启用)、archived(归档)"
    )

    # 使用统计
    shiyong_cishu = Column(
        Integer,
        default=0,
        comment="使用次数"
    )

    # 审批信息
    shenpi_zhuangtai = Column(
        String(20),
        default="pending",
        comment="审批状态：pending(待审批)、approved(已审批)、rejected(已拒绝)"
    )

    shenpi_ren = Column(
        String(36),
        nullable=True,
        comment="审批人ID"
    )

    shenpi_shijian = Column(
        DateTime,
        nullable=True,
        comment="审批时间"
    )

    shenpi_yijian = Column(
        Text,
        nullable=True,
        comment="审批意见"
    )

    # 其他信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    # 关联关系
    hetong_list = relationship(
        "Hetong",
        back_populates="hetong_moban",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<HetongMoban(moban_mingcheng='{self.moban_mingcheng}', hetong_leixing='{self.hetong_leixing}')>"
