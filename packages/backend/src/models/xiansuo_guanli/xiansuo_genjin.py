"""
线索跟进记录表模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel

class XiansuoGenjin(BaseModel):
    """线索跟进记录表"""
    
    __tablename__ = "xiansuo_genjin"
    __table_args__ = {"comment": "线索跟进记录表"}
    
    # 关联信息
    xiansuo_id = Column(
        String(36),
        ForeignKey("xiansuo.id"),
        nullable=False,
        comment="线索ID"
    )
    
    # 跟进信息
    genjin_fangshi = Column(
        String(50),
        nullable=False,
        comment="跟进方式：phone-电话，email-邮件，wechat-微信，visit-拜访，other-其他"
    )
    
    genjin_shijian = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="跟进时间"
    )
    
    genjin_neirong = Column(
        Text,
        nullable=False,
        comment="跟进内容"
    )
    
    # 客户反馈
    kehu_fankui = Column(
        Text,
        nullable=True,
        comment="客户反馈"
    )
    
    kehu_taidu = Column(
        String(50),
        nullable=True,
        comment="客户态度：positive-积极，neutral-中性，negative-消极"
    )
    
    # 下次跟进计划
    xiaci_genjin_shijian = Column(
        DateTime,
        nullable=True,
        comment="下次跟进时间"
    )
    
    xiaci_genjin_neirong = Column(
        String(500),
        nullable=True,
        comment="下次跟进内容计划"
    )
    
    # 跟进结果
    genjin_jieguo = Column(
        String(50),
        nullable=True,
        comment="跟进结果：interested-有兴趣，considering-考虑中，rejected-拒绝，no_response-无回应"
    )
    
    # 操作人信息
    genjin_ren_id = Column(
        String(36),
        nullable=False,
        comment="跟进人ID"
    )
    
    genjin_ren_xingming = Column(
        String(50),
        nullable=True,
        comment="跟进人姓名"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径（多个用逗号分隔）"
    )
    
    # 关联关系
    xiansuo = relationship(
        "Xiansuo",
        back_populates="genjin_jilu_list"
    )
