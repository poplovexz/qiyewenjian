"""
成本记录表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel

class ChengbenJilu(BaseModel):
    """成本记录表"""
    
    __tablename__ = "chengben_jilu"
    __table_args__ = {"comment": "成本记录表"}
    
    # 关联信息
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id", ondelete="CASCADE"),
        nullable=True,
        comment="合同ID"
    )
    
    xiangmu_id = Column(
        String(36),
        nullable=True,
        comment="项目ID"
    )
    
    bumen_id = Column(
        String(36),
        nullable=True,
        comment="部门ID"
    )
    
    # 成本基本信息
    chengben_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="成本编号"
    )
    
    chengben_mingcheng = Column(
        String(200),
        nullable=False,
        comment="成本名称"
    )
    
    chengben_leixing = Column(
        String(50),
        nullable=False,
        comment="成本类型：rengong(人工成本)、cailiao(材料成本)、shebei(设备成本)、waibao(外包成本)、qita(其他成本)"
    )
    
    chengben_fenlei = Column(
        String(50),
        nullable=False,
        comment="成本分类：zhijie(直接成本)、jianjie(间接成本)、guding(固定成本)、biandong(变动成本)"
    )
    
    chengben_miaoshu = Column(
        Text,
        nullable=True,
        comment="成本描述"
    )
    
    # 金额信息
    chengben_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="成本金额"
    )
    
    yusuan_jine = Column(
        Numeric(10, 2),
        nullable=True,
        comment="预算金额"
    )
    
    shiji_jine = Column(
        Numeric(10, 2),
        nullable=True,
        comment="实际金额"
    )
    
    # 时间信息
    fasheng_shijian = Column(
        DateTime,
        nullable=False,
        comment="发生时间"
    )
    
    jizhangjian = Column(
        DateTime,
        nullable=True,
        comment="记账时间"
    )
    
    # 供应商信息
    gongyingshang_id = Column(
        String(36),
        nullable=True,
        comment="供应商ID"
    )
    
    gongyingshang_mingcheng = Column(
        String(200),
        nullable=True,
        comment="供应商名称"
    )
    
    # 发票信息
    fapiao_hao = Column(
        String(50),
        nullable=True,
        comment="发票号码"
    )
    
    fapiao_jine = Column(
        Numeric(10, 2),
        nullable=True,
        comment="发票金额"
    )
    
    fapiao_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="发票状态：pending(待开票)、received(已收票)、verified(已验证)、recorded(已入账)"
    )
    
    # 审核信息
    shenhe_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="审核状态：draft(草稿)、submitted(已提交)、approved(已审批)、rejected(已拒绝)、recorded(已入账)"
    )
    
    shenhe_jilu_id = Column(
        String(36),
        ForeignKey("shenhe_jilu.id"),
        nullable=True,
        comment="审核记录ID"
    )
    
    shenhe_ren = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="审核人"
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
    
    # 财务信息
    kuaiji_kemu = Column(
        String(100),
        nullable=True,
        comment="会计科目"
    )
    
    chengben_zhongxin = Column(
        String(100),
        nullable=True,
        comment="成本中心"
    )
    
    fentan_fangshi = Column(
        String(50),
        nullable=True,
        comment="分摊方式：zhijie(直接分摊)、bili(按比例分摊)、shijian(按时间分摊)、gongzuoliang(按工作量分摊)"
    )
    
    fentan_bili = Column(
        Numeric(5, 4),
        nullable=True,
        comment="分摊比例"
    )
    
    # 附件信息
    fujian_lujing = Column(
        Text,
        nullable=True,
        comment="附件路径（JSON格式存储多个文件路径）"
    )
    
    # 状态信息
    zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态：active(有效)、cancelled(已取消)、adjusted(已调整)"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong = relationship("Hetong", back_populates="chengben_jilu_list")
    shenhe_jilu = relationship("ShenheJilu")
    shenhe_ren_user = relationship("Yonghu")
    
    def __repr__(self) -> str:
        return f"<ChengbenJilu(id={self.id}, chengben_bianhao={self.chengben_bianhao}, chengben_jine={self.chengben_jine})>"
