"""
报销申请数据模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel


class BaoxiaoShenqing(BaseModel):
    """报销申请表"""
    
    __tablename__ = "baoxiao_shenqing"
    __table_args__ = {"comment": "报销申请表"}
    
    # 申请基本信息
    shenqing_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="申请编号，如BX202411110001"
    )
    
    shenqing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="申请人ID"
    )
    
    # 报销信息
    baoxiao_leixing = Column(
        String(50),
        nullable=False,
        comment="报销类型：chalvfei(差旅费)、canyinfei(餐饮费)、jiaotongfei(交通费)、bangongyongpin(办公用品)、qita(其他)"
    )
    
    baoxiao_jine = Column(
        Numeric(15, 2),
        nullable=False,
        comment="报销金额"
    )
    
    baoxiao_shijian = Column(
        DateTime,
        nullable=False,
        comment="报销事项发生时间"
    )
    
    baoxiao_yuanyin = Column(
        Text,
        nullable=False,
        comment="报销原因说明"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径（发票、收据等），多个文件用逗号分隔"
    )
    
    # 审核信息
    shenhe_zhuangtai = Column(
        String(20),
        default="daishehe",
        nullable=False,
        comment="审核状态：daishehe(待审核)、shenhezhong(审核中)、tongguo(已通过)、jujue(已拒绝)"
    )
    
    shenhe_liucheng_id = Column(
        String(36),
        ForeignKey("shenhe_liucheng.id"),
        nullable=True,
        comment="审核流程ID"
    )
    
    # 备注
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    shenqing_ren = relationship("Yonghu", foreign_keys=[shenqing_ren_id])
    shenhe_liucheng = relationship("ShenheLiucheng")
    
    def __repr__(self) -> str:
        return f"<BaoxiaoShenqing(id={self.id}, shenqing_bianhao={self.shenqing_bianhao}, baoxiao_jine={self.baoxiao_jine})>"

