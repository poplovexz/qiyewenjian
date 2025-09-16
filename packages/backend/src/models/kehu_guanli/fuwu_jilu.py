"""
服务记录表模型
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import BaseModel


class FuwuJilu(BaseModel):
    """服务记录表"""
    
    __tablename__ = "fuwu_jilu"
    __table_args__ = {"comment": "服务记录表"}
    
    kehu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    # 沟通记录
    goutong_fangshi = Column(
        String(20),
        nullable=False,
        comment="沟通方式：phone-电话，email-邮件，online-在线聊天，meeting-会议"
    )
    
    goutong_neirong = Column(
        Text,
        nullable=False,
        comment="沟通内容"
    )
    
    goutong_shijian = Column(
        String(50),
        nullable=False,
        comment="沟通时间"
    )
    
    # 问题处理
    wenti_leixing = Column(
        String(50),
        nullable=True,
        comment="问题类型：zhangwu-账务类，shuiwu-税务类，zixun-咨询类，other-其他"
    )
    
    wenti_miaoshu = Column(
        Text,
        nullable=True,
        comment="问题描述"
    )
    
    chuli_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="处理状态：pending-待处理，processing-处理中，completed-已完成，cancelled-已取消"
    )
    
    chuli_jieguo = Column(
        Text,
        nullable=True,
        comment="处理结果"
    )
    
    chuli_ren_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="处理人ID"
    )
    
    # 关联关系
    kehu = relationship("Kehu", back_populates="fuwu_jilu_list")
    
    def __repr__(self) -> str:
        return f"<FuwuJilu(kehu_id='{self.kehu_id}', goutong_fangshi='{self.goutong_fangshi}')>"
