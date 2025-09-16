"""
凭证表模型
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from ..base import BaseModel


class Pingzheng(BaseModel):
    """凭证表"""
    
    __tablename__ = "pingzheng"
    __table_args__ = {"comment": "凭证表"}
    
    kehu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    zhizuo_ren_id = Column(
        UUID(as_uuid=True),
        ForeignKey("yonghu.id"),
        nullable=False,
        comment="制作人ID（会计）"
    )
    
    # 凭证基本信息
    pingzheng_bianhao = Column(
        String(50),
        nullable=False,
        comment="凭证编号"
    )
    
    pingzheng_riqi = Column(
        DateTime,
        nullable=False,
        comment="凭证日期"
    )
    
    zhaiyao = Column(
        String(200),
        nullable=False,
        comment="摘要"
    )
    
    # 会计科目信息
    jiebie_kemu = Column(
        String(100),
        nullable=False,
        comment="借方科目"
    )
    
    jiebie_jine = Column(
        Numeric(15, 2),
        nullable=False,
        comment="借方金额"
    )
    
    daifang_kemu = Column(
        String(100),
        nullable=False,
        comment="贷方科目"
    )
    
    daifang_jine = Column(
        Numeric(15, 2),
        nullable=False,
        comment="贷方金额"
    )
    
    # 凭证状态
    pingzheng_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="凭证状态：draft-草稿，submitted-已提交，approved-已审核，posted-已过账，cancelled-已作废"
    )
    
    # 审核信息
    shenhe_ren_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="审核人ID"
    )
    
    shenhe_riqi = Column(
        DateTime,
        nullable=True,
        comment="审核日期"
    )
    
    shenhe_yijian = Column(
        Text,
        nullable=True,
        comment="审核意见"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件文件路径（发票、合同等）"
    )
    
    fujian_miaoshu = Column(
        String(200),
        nullable=True,
        comment="附件描述"
    )
    
    # 过账信息
    guozhang_riqi = Column(
        DateTime,
        nullable=True,
        comment="过账日期"
    )
    
    guozhang_ren_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="过账人ID"
    )
    
    def __repr__(self) -> str:
        return f"<Pingzheng(pingzheng_bianhao='{self.pingzheng_bianhao}', zhaiyao='{self.zhaiyao}')>"
