"""
银行汇款单据模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel

class YinhangHuikuanDanju(BaseModel):
    """银行汇款单据表"""
    
    __tablename__ = "yinhang_huikuan_danju"
    __table_args__ = {"comment": "银行汇款单据表"}
    
    # 支付关联
    hetong_zhifu_id = Column(
        String(36),
        ForeignKey("hetong_zhifu.id"),
        nullable=False,
        comment="合同支付ID"
    )
    
    # 单据信息
    danju_bianhao = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="单据编号"
    )
    
    danju_lujing = Column(
        String(500),
        nullable=False,
        comment="单据文件路径"
    )
    
    danju_mingcheng = Column(
        String(200),
        nullable=True,
        comment="单据文件名称"
    )
    
    # 汇款信息
    huikuan_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="汇款金额"
    )
    
    huikuan_riqi = Column(
        DateTime,
        nullable=False,
        comment="汇款日期"
    )
    
    huikuan_ren = Column(
        String(100),
        nullable=False,
        comment="汇款人"
    )
    
    huikuan_yinhang = Column(
        String(200),
        nullable=True,
        comment="汇款银行"
    )
    
    huikuan_zhanghu = Column(
        String(50),
        nullable=True,
        comment="汇款账户"
    )
    
    # 上传信息
    shangchuan_ren_id = Column(
        String(36),
        nullable=False,
        comment="上传人ID（业务员）"
    )
    
    shangchuan_shijian = Column(
        DateTime,
        nullable=True,
        comment="上传时间"
    )
    
    # 审核信息
    shenhe_zhuangtai = Column(
        String(20),
        default="daishehe",
        nullable=False,
        comment="审核状态：daishehe(待审核)、tongguo(通过)、jujue(拒绝)"
    )
    
    shenhe_ren_id = Column(
        String(36),
        nullable=True,
        comment="审核人ID（财务）"
    )
    
    shenhe_shijian = Column(
        DateTime,
        nullable=True,
        comment="审核时间"
    )
    
    shenhe_yijian = Column(
        Text,
        nullable=True,
        comment="审核意见"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong_zhifu = relationship(
        "HetongZhifu",
        back_populates="huikuan_danju_list"
    )
    
    def __repr__(self) -> str:
        return f"<YinhangHuikuanDanju(danju_bianhao='{self.danju_bianhao}', huikuan_jine={self.huikuan_jine})>"
