"""
开票申请表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel

class KaipiaoShenqing(BaseModel):
    """开票申请表"""
    
    __tablename__ = "kaipiao_shenqing"
    __table_args__ = {"comment": "开票申请表"}
    
    # 关联信息
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id", ondelete="CASCADE"),
        nullable=True,
        comment="合同ID"
    )
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    zhifu_dingdan_id = Column(
        String(36),
        ForeignKey("zhifu_dingdan.id", ondelete="CASCADE"),
        nullable=True,
        comment="支付订单ID"
    )
    
    # 申请基本信息
    shenqing_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="申请编号"
    )
    
    kaipiao_leixing = Column(
        String(20),
        nullable=False,
        comment="开票类型：zengzhishui(增值税专用发票)、putong(普通发票)、dianzifapiao(电子发票)"
    )
    
    kaipiao_mingcheng = Column(
        String(200),
        nullable=False,
        comment="开票名称"
    )
    
    kaipiao_neirong = Column(
        Text,
        nullable=True,
        comment="开票内容"
    )
    
    # 金额信息
    kaipiao_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="开票金额"
    )
    
    shuie = Column(
        Numeric(10, 2),
        default=0.00,
        comment="税额"
    )
    
    jia_shui_jine = Column(
        Numeric(10, 2),
        nullable=False,
        comment="价税合计金额"
    )
    
    # 开票信息
    gouwu_fang_mingcheng = Column(
        String(200),
        nullable=False,
        comment="购物方名称"
    )
    
    gouwu_fang_shuihao = Column(
        String(50),
        nullable=True,
        comment="购物方税号"
    )
    
    gouwu_fang_dizhi = Column(
        String(500),
        nullable=True,
        comment="购物方地址"
    )
    
    gouwu_fang_dianhua = Column(
        String(50),
        nullable=True,
        comment="购物方电话"
    )
    
    gouwu_fang_yinhang = Column(
        String(200),
        nullable=True,
        comment="购物方开户银行"
    )
    
    gouwu_fang_zhanghu = Column(
        String(50),
        nullable=True,
        comment="购物方银行账户"
    )
    
    # 销售方信息
    xiaoshou_fang_mingcheng = Column(
        String(200),
        nullable=False,
        comment="销售方名称"
    )
    
    xiaoshou_fang_shuihao = Column(
        String(50),
        nullable=False,
        comment="销售方税号"
    )
    
    xiaoshou_fang_dizhi = Column(
        String(500),
        nullable=True,
        comment="销售方地址"
    )
    
    xiaoshou_fang_dianhua = Column(
        String(50),
        nullable=True,
        comment="销售方电话"
    )
    
    xiaoshou_fang_yinhang = Column(
        String(200),
        nullable=True,
        comment="销售方开户银行"
    )
    
    xiaoshou_fang_zhanghu = Column(
        String(50),
        nullable=True,
        comment="销售方银行账户"
    )
    
    # 状态信息
    shenqing_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="申请状态：draft(草稿)、submitted(已提交)、approved(已审批)、rejected(已拒绝)、invoiced(已开票)、cancelled(已取消)"
    )
    
    kaipiao_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="开票状态：pending(待开票)、processing(开票中)、completed(已完成)、failed(开票失败)"
    )
    
    # 时间信息
    shenqing_shijian = Column(
        DateTime,
        nullable=False,
        comment="申请时间"
    )
    
    yaoqiu_kaipiao_shijian = Column(
        DateTime,
        nullable=True,
        comment="要求开票时间"
    )
    
    kaipiao_shijian = Column(
        DateTime,
        nullable=True,
        comment="实际开票时间"
    )
    
    # 发票信息
    fapiao_hao = Column(
        String(50),
        nullable=True,
        comment="发票号码"
    )
    
    fapiao_daima = Column(
        String(50),
        nullable=True,
        comment="发票代码"
    )
    
    fapiao_wenjian_lujing = Column(
        String(500),
        nullable=True,
        comment="发票文件路径"
    )
    
    # 审核信息
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
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong = relationship("Hetong", back_populates="kaipiao_shenqing_list")
    kehu = relationship("Kehu")
    zhifu_dingdan = relationship("ZhifuDingdan")
    shenhe_jilu = relationship("ShenheJilu")
    shenhe_ren_user = relationship("Yonghu")
    
    def __repr__(self) -> str:
        return f"<KaipiaoShenqing(id={self.id}, shenqing_bianhao={self.shenqing_bianhao}, kaipiao_jine={self.kaipiao_jine})>"
