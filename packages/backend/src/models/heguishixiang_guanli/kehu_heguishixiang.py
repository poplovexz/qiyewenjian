"""
客户合规事项配置表
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel


class KehuHeguishixiang(BaseModel):
    """客户合规事项配置表"""

    __tablename__ = "kehu_heguishixiang"
    __table_args__ = {"comment": "客户合规事项配置表"}

    # 关联信息
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )

    heguishixiang_moban_id = Column(
        String(36),
        ForeignKey("heguishixiang_moban.id", ondelete="CASCADE"),
        nullable=False,
        comment="合规事项模板ID"
    )

    # 客户特殊配置
    teshu_jiezhi_shijian = Column(
        Text,
        nullable=True,
        comment="特殊截止时间配置（JSON格式）：覆盖模板的默认配置"
    )

    teshu_tixing_peizhi = Column(
        Text,
        nullable=True,
        comment="特殊提醒配置（JSON格式）：如特殊的提醒时间、方式等"
    )

    # 负责人配置
    fuzeren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="负责人ID（内部会计）"
    )

    kehu_lianxiren_id = Column(
        String(36),
        nullable=True,
        comment="客户联系人ID"
    )

    # 风险评估
    kehu_fengxian_dengji = Column(
        String(20),
        default="medium",
        comment="客户风险等级：low(低)、medium(中)、high(高)、critical(严重)"
    )

    lishi_yuqi_cishu = Column(
        Integer,
        default=0,
        comment="历史逾期次数"
    )

    zuijin_yuqi_shijian = Column(
        DateTime,
        nullable=True,
        comment="最近逾期时间"
    )

    # 状态管理
    peizhi_zhuangtai = Column(
        String(20),
        default="active",
        comment="配置状态：active(启用)、inactive(停用)、suspended(暂停)"
    )

    qiyong_shijian = Column(
        DateTime,
        nullable=True,
        comment="启用时间"
    )

    tingyong_shijian = Column(
        DateTime,
        nullable=True,
        comment="停用时间"
    )

    tingyong_yuanyin = Column(
        Text,
        nullable=True,
        comment="停用原因"
    )

    # 自动化配置
    zidong_shengcheng = Column(
        Boolean,
        default=True,
        comment="是否自动生成合规事项实例"
    )

    zidong_tixing = Column(
        Boolean,
        default=True,
        comment="是否自动发送提醒"
    )

    # 备注信息
    teshu_shuoming = Column(
        Text,
        nullable=True,
        comment="特殊说明"
    )

    # 扩展信息
    kuozhan_shuju = Column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )

    # 关联关系
    kehu = relationship("Kehu", back_populates="heguishixiang_peizhi_list")
    heguishixiang_moban = relationship("HeguishixiangMoban", back_populates="kehu_heguishixiang_list")
    fuzeren = relationship("Yonghu", foreign_keys=[fuzeren_id])

    heguishixiang_shili_list = relationship(
        "HeguishixiangShili",
        back_populates="kehu_heguishixiang",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KehuHeguishixiang(kehu_id='{self.kehu_id}', heguishixiang_moban_id='{self.heguishixiang_moban_id}', peizhi_zhuangtai='{self.peizhi_zhuangtai}')>"
