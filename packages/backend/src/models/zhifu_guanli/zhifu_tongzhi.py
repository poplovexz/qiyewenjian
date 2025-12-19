"""
支付通知表模型
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel

class ZhifuTongzhi(BaseModel):
    """支付通知表"""
    
    __tablename__ = "zhifu_tongzhi"
    __table_args__ = {"comment": "支付通知表"}
    
    # 关联信息
    zhifu_dingdan_id = Column(
        String(36),
        ForeignKey("zhifu_dingdan.id", ondelete="CASCADE"),
        nullable=True,
        comment="支付订单ID"
    )
    
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id", ondelete="CASCADE"),
        nullable=True,
        comment="合同ID"
    )
    
    jieshou_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=False,
        comment="接收人ID"
    )
    
    # 通知基本信息
    tongzhi_leixing = Column(
        String(50),
        nullable=False,
        comment="通知类型：payment_success(支付成功)、payment_failed(支付失败)、contract_signed(合同签署)、invoice_generated(发票生成)、task_assigned(任务分配)"
    )
    
    tongzhi_biaoti = Column(
        String(200),
        nullable=False,
        comment="通知标题"
    )
    
    tongzhi_neirong = Column(
        Text,
        nullable=False,
        comment="通知内容"
    )
    
    # 状态信息
    tongzhi_zhuangtai = Column(
        String(20),
        default="unread",
        nullable=False,
        comment="通知状态：unread(未读)、read(已读)、archived(已归档)"
    )
    
    youxian_ji = Column(
        String(20),
        default="normal",
        nullable=False,
        comment="优先级：low(低)、normal(普通)、high(高)、urgent(紧急)"
    )
    
    # 时间信息
    fasong_shijian = Column(
        DateTime,
        nullable=False,
        comment="发送时间"
    )
    
    yuedu_shijian = Column(
        DateTime,
        nullable=True,
        comment="阅读时间"
    )
    
    guoqi_shijian = Column(
        DateTime,
        nullable=True,
        comment="过期时间"
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
    
    # 发送渠道
    fasong_qudao = Column(
        String(50),
        default="system",
        nullable=False,
        comment="发送渠道：system(站内消息)、email(邮件)、sms(短信)、wechat(微信)"
    )
    
    # 关联关系
    zhifu_dingdan = relationship("ZhifuDingdan")
    hetong = relationship("Hetong")
    jieshou_ren = relationship("Yonghu")
    
    def __repr__(self) -> str:
        return f"<ZhifuTongzhi(tongzhi_leixing='{self.tongzhi_leixing}', tongzhi_biaoti='{self.tongzhi_biaoti}', tongzhi_zhuangtai='{self.tongzhi_zhuangtai}')>"
