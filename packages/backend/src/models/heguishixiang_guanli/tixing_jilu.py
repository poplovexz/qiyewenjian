"""
提醒记录表
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel


class TixingJilu(BaseModel):
    """提醒记录表"""

    __tablename__ = "tixing_jilu"
    __table_args__ = {"comment": "提醒记录表"}

    # 关联信息
    heguishixiang_shili_id = Column(
        String(36),
        ForeignKey("heguishixiang_shili.id", ondelete="CASCADE"),
        nullable=False,
        comment="合规事项实例ID"
    )

    heguishixiang_tixing_id = Column(
        String(36),
        ForeignKey("heguishixiang_tixing.id", ondelete="CASCADE"),
        nullable=False,
        comment="合规事项提醒配置ID"
    )

    # 提醒基本信息
    tixing_bianhao = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="提醒编号"
    )

    tixing_leixing = Column(
        String(50),
        nullable=False,
        comment="提醒类型：deadline_reminder(截止日期提醒)、overdue_reminder(逾期提醒)、status_change(状态变更提醒)"
    )

    # 接收人信息
    jieshou_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=False,
        comment="接收人ID"
    )

    jieshou_ren_leixing = Column(
        String(50),
        nullable=False,
        comment="接收人类型：customer(客户)、accountant(会计)、manager(经理)"
    )

    # 提醒内容
    tixing_biaoti = Column(
        String(500),
        nullable=False,
        comment="提醒标题"
    )

    tixing_neirong = Column(
        Text,
        nullable=False,
        comment="提醒内容"
    )

    # 发送信息
    fasong_fangshi = Column(
        String(50),
        nullable=False,
        comment="发送方式：system(站内消息)、email(邮件)、sms(短信)、wechat(微信)"
    )

    jihua_fasong_shijian = Column(
        DateTime,
        nullable=False,
        comment="计划发送时间"
    )

    shiji_fasong_shijian = Column(
        DateTime,
        nullable=True,
        comment="实际发送时间"
    )

    # 状态管理
    fasong_zhuangtai = Column(
        String(20),
        default="pending",
        comment="发送状态：pending(待发送)、sent(已发送)、failed(发送失败)、cancelled(已取消)"
    )

    shibai_yuanyin = Column(
        Text,
        nullable=True,
        comment="失败原因"
    )

    chongshi_cishu = Column(
        Integer,
        default=0,
        comment="重试次数"
    )

    # 接收状态
    jieshou_zhuangtai = Column(
        String(20),
        default="unread",
        comment="接收状态：unread(未读)、read(已读)、ignored(已忽略)"
    )

    yuedu_shijian = Column(
        DateTime,
        nullable=True,
        comment="阅读时间"
    )

    # 响应信息
    yonghu_fankui = Column(
        Text,
        nullable=True,
        comment="用户反馈"
    )

    caozuo_jieguo = Column(
        String(50),
        nullable=True,
        comment="操作结果：completed(已完成)、postponed(已延期)、ignored(已忽略)"
    )

    # 优先级
    youxian_ji = Column(
        String(20),
        default="normal",
        comment="优先级：low(低)、normal(普通)、high(高)、urgent(紧急)"
    )

    # 扩展信息
    kuozhan_shuju = Column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )

    lianjie_url = Column(
        String(500),
        nullable=True,
        comment="相关链接URL"
    )

    # 关联关系
    heguishixiang_shili = relationship("HeguishixiangShili", back_populates="tixing_jilu_list")
    heguishixiang_tixing = relationship("HeguishixiangTixing", back_populates="tixing_jilu_list")
    jieshou_ren = relationship("Yonghu")

    def __repr__(self) -> str:
        return f"<TixingJilu(tixing_bianhao='{self.tixing_bianhao}', tixing_leixing='{self.tixing_leixing}', fasong_zhuangtai='{self.fasong_zhuangtai}')>"
