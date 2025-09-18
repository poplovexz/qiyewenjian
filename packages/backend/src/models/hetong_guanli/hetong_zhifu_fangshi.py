"""
合同支付方式表模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..base import BaseModel


class HetongZhifuFangshi(BaseModel):
    """合同支付方式表"""
    
    __tablename__ = "hetong_zhifu_fangshi"
    __table_args__ = {"comment": "合同支付方式表"}
    
    # 关联信息
    yifang_zhuti_id = Column(
        String(36),
        ForeignKey("hetong_yifang_zhuti.id", ondelete="CASCADE"),
        nullable=False,
        comment="乙方主体ID"
    )
    
    # 支付方式信息
    zhifu_leixing = Column(
        String(50),
        nullable=False,
        comment="支付类型：weixin(微信支付)、zhifubao(支付宝)、yinhangzhuanzhang(银行转账)、xianjin(现金)、qita(其他)"
    )
    
    zhifu_mingcheng = Column(
        String(100),
        nullable=False,
        comment="支付方式名称"
    )
    
    # 账户信息
    zhanghu_mingcheng = Column(
        String(100),
        nullable=True,
        comment="账户名称"
    )
    
    zhanghu_haoma = Column(
        String(100),
        nullable=True,
        comment="账户号码"
    )
    
    # 银行信息（银行转账专用）
    kaihuhang_mingcheng = Column(
        String(200),
        nullable=True,
        comment="开户行名称"
    )
    
    kaihuhang_dizhi = Column(
        String(300),
        nullable=True,
        comment="开户行地址"
    )
    
    lianhanghao = Column(
        String(50),
        nullable=True,
        comment="联行号"
    )
    
    # 限额信息
    danbi_xiange = Column(
        Numeric(15, 2),
        nullable=True,
        comment="单笔限额"
    )
    
    riqi_xiange = Column(
        Numeric(15, 2),
        nullable=True,
        comment="日期限额"
    )
    
    # 状态信息
    zhifu_zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="支付状态：active(启用)、inactive(停用)"
    )
    
    shi_moren = Column(
        String(1),
        default="N",
        nullable=False,
        comment="是否默认：Y(是)、N(否)"
    )
    
    # 排序
    paixu = Column(
        String(10),
        default="0",
        nullable=False,
        comment="排序号"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    yifang_zhuti = relationship("HetongYifangZhuti", back_populates="zhifu_fangshi_list")
    
    def __repr__(self) -> str:
        return f"<HetongZhifuFangshi(zhifu_mingcheng='{self.zhifu_mingcheng}', zhifu_leixing='{self.zhifu_leixing}')>"
