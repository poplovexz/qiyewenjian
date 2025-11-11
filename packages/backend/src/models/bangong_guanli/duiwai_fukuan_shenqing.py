"""
对外付款申请数据模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel


class DuiwaiFukuanShenqing(BaseModel):
    """对外付款申请表"""
    
    __tablename__ = "duiwai_fukuan_shenqing"
    __table_args__ = {"comment": "对外付款申请表"}
    
    # 申请基本信息
    shenqing_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="申请编号，如FK202411110001"
    )
    
    shenqing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="申请人ID"
    )
    
    # 付款信息
    fukuan_duixiang = Column(
        String(200),
        nullable=False,
        comment="付款对象（公司/个人名称）"
    )
    
    fukuan_jine = Column(
        Numeric(15, 2),
        nullable=False,
        comment="付款金额"
    )
    
    fukuan_yuanyin = Column(
        Text,
        nullable=False,
        comment="付款原因"
    )
    
    fukuan_fangshi = Column(
        String(50),
        nullable=False,
        comment="付款方式：yinhangzhuanzhang(银行转账)、zhipiao(支票)、xianjin(现金)"
    )
    
    # 收款信息
    shoukuan_zhanghu = Column(
        String(100),
        nullable=False,
        comment="收款账户信息"
    )
    
    shoukuan_yinhang = Column(
        String(200),
        nullable=True,
        comment="收款银行"
    )
    
    # 时间信息
    yaoqiu_fukuan_shijian = Column(
        DateTime,
        nullable=True,
        comment="要求付款时间"
    )
    
    shiji_fukuan_shijian = Column(
        DateTime,
        nullable=True,
        comment="实际付款时间"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径（合同、发票等），多个文件用逗号分隔"
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
    
    # 付款状态
    fukuan_zhuangtai = Column(
        String(20),
        default="daifukuan",
        nullable=False,
        comment="付款状态：daifukuan(待付款)、yifukuan(已付款)"
    )
    
    fukuan_liushui_hao = Column(
        String(100),
        nullable=True,
        comment="付款流水号"
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
        return f"<DuiwaiFukuanShenqing(id={self.id}, shenqing_bianhao={self.shenqing_bianhao}, fukuan_jine={self.fukuan_jine})>"

