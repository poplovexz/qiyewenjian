"""
请假申请数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class QingjiaShenqing(BaseModel):
    """请假申请表"""
    
    __tablename__ = "qingjia_shenqing"
    __table_args__ = {"comment": "请假申请表"}
    
    # 申请基本信息
    shenqing_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="申请编号，如QJ202411110001"
    )
    
    shenqing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="申请人ID"
    )
    
    # 请假信息
    qingjia_leixing = Column(
        String(50),
        nullable=False,
        comment="请假类型：shijia(事假)、bingjia(病假)、nianjia(年假)、tiaoxiu(调休)、hunjia(婚假)、chanjia(产假)、peichanjia(陪产假)、sangjia(丧假)"
    )
    
    kaishi_shijian = Column(
        DateTime,
        nullable=False,
        comment="开始时间"
    )
    
    jieshu_shijian = Column(
        DateTime,
        nullable=False,
        comment="结束时间"
    )
    
    qingjia_tianshu = Column(
        Integer,
        nullable=False,
        comment="请假天数"
    )
    
    qingjia_yuanyin = Column(
        Text,
        nullable=False,
        comment="请假原因"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径（病假条等），多个文件用逗号分隔"
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
        return f"<QingjiaShenqing(id={self.id}, shenqing_bianhao={self.shenqing_bianhao}, qingjia_tianshu={self.qingjia_tianshu})>"
