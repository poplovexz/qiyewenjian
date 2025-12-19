"""
合规事项提醒配置表
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel

class HeguishixiangTixing(BaseModel):
    """合规事项提醒配置表"""

    __tablename__ = "heguishixiang_tixing"
    __table_args__ = {"comment": "合规事项提醒配置表"}

    # 关联信息
    heguishixiang_moban_id = Column(
        String(36),
        ForeignKey("heguishixiang_moban.id", ondelete="CASCADE"),
        nullable=True,
        comment="合规事项模板ID（全局配置时为空）"
    )

    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=True,
        comment="客户ID（客户特定配置时填写）"
    )

    # 提醒基本信息
    tixing_mingcheng = Column(
        String(200),
        nullable=False,
        comment="提醒名称"
    )

    tixing_leixing = Column(
        String(50),
        nullable=False,
        comment="提醒类型：deadline_reminder(截止日期提醒)、overdue_reminder(逾期提醒)、status_change(状态变更提醒)"
    )

    # 提醒时间配置
    tiqian_tianshu = Column(
        Integer,
        nullable=False,
        comment="提前天数"
    )

    tixing_shijian = Column(
        String(20),
        default="09:00",
        comment="提醒时间（HH:MM格式）"
    )

    # 提醒方式配置
    tixing_fangshi = Column(
        String(100),
        default="system",
        comment="提醒方式（逗号分隔）：system(站内消息)、email(邮件)、sms(短信)、wechat(微信)"
    )

    # 接收人配置
    jieshou_ren_leixing = Column(
        String(50),
        nullable=False,
        comment="接收人类型：customer(客户)、accountant(会计)、manager(经理)、custom(自定义)"
    )

    jieshou_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="接收人ID（自定义时填写）"
    )

    jieshou_ren_jiaose = Column(
        String(50),
        nullable=True,
        comment="接收人角色（按角色发送时填写）"
    )

    # 提醒内容配置
    tixing_biaoti_moban = Column(
        String(500),
        nullable=False,
        comment="提醒标题模板"
    )

    tixing_neirong_moban = Column(
        Text,
        nullable=False,
        comment="提醒内容模板"
    )

    # 重复提醒配置
    chongfu_tixing = Column(
        Boolean,
        default=False,
        comment="是否重复提醒"
    )

    chongfu_jiangetianshu = Column(
        Integer,
        nullable=True,
        comment="重复间隔天数"
    )

    zuida_chongfu_cishu = Column(
        Integer,
        nullable=True,
        comment="最大重复次数"
    )

    # 条件配置
    tixing_tiaojian = Column(
        Text,
        nullable=True,
        comment="提醒条件（JSON格式）：如特定状态、风险等级等"
    )

    # 优先级配置
    youxian_ji = Column(
        String(20),
        default="normal",
        comment="优先级：low(低)、normal(普通)、high(高)、urgent(紧急)"
    )

    # 状态管理
    tixing_zhuangtai = Column(
        String(20),
        default="active",
        comment="提醒状态：active(启用)、inactive(停用)、draft(草稿)"
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

    # 统计信息
    fasong_cishu = Column(
        Integer,
        default=0,
        comment="发送次数"
    )

    chenggong_cishu = Column(
        Integer,
        default=0,
        comment="成功次数"
    )

    shibai_cishu = Column(
        Integer,
        default=0,
        comment="失败次数"
    )

    zuijin_fasong_shijian = Column(
        DateTime,
        nullable=True,
        comment="最近发送时间"
    )

    # 扩展信息
    kuozhan_shuju = Column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )

    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 关联关系
    heguishixiang_moban = relationship("HeguishixiangMoban")
    kehu = relationship("Kehu")
    jieshou_ren = relationship("Yonghu")

    tixing_jilu_list = relationship(
        "TixingJilu",
        back_populates="heguishixiang_tixing",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<HeguishixiangTixing(tixing_mingcheng='{self.tixing_mingcheng}', tixing_leixing='{self.tixing_leixing}', tixing_zhuangtai='{self.tixing_zhuangtai}')>"
