"""
退款记录表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from ..base import BaseModel

class ZhifuTuikuan(BaseModel):
    """退款记录表"""
    
    __tablename__ = "zhifu_tuikuan"
    __table_args__ = {"comment": "退款记录表"}
    
    # 关联信息
    zhifu_dingdan_id = Column(
        String(36),
        ForeignKey("zhifu_dingdan.id", ondelete="CASCADE"),
        nullable=False,
        comment="支付订单ID"
    )
    
    zhifu_peizhi_id = Column(
        String(36),
        ForeignKey("zhifu_peizhi.id", ondelete="SET NULL"),
        comment="支付配置ID"
    )
    
    # 退款基本信息
    tuikuan_danhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="退款单号"
    )
    
    yuanshi_dingdan_hao = Column(
        String(100),
        nullable=False,
        comment="原始订单号"
    )
    
    disanfang_tuikuan_hao = Column(
        String(100),
        comment="第三方退款单号"
    )
    
    # 金额信息
    yuanshi_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="原始订单金额"
    )
    
    tuikuan_jine = Column(
        Numeric(12, 2),
        nullable=False,
        comment="退款金额"
    )
    
    # 退款信息
    tuikuan_yuanyin = Column(
        Text,
        comment="退款原因"
    )
    
    tuikuan_zhuangtai = Column(
        String(20),
        default='chuli_zhong',
        comment="退款状态：chuli_zhong(处理中)、chenggong(成功)、shibai(失败)、yiguanbi(已关闭)"
    )
    
    tuikuan_pingtai = Column(
        String(20),
        nullable=False,
        comment="退款平台：weixin(微信)、zhifubao(支付宝)"
    )
    
    # 时间信息
    shenqing_shijian = Column(
        DateTime,
        comment="申请时间"
    )
    
    chenggong_shijian = Column(
        DateTime,
        comment="成功时间"
    )
    
    daozhang_shijian = Column(
        DateTime,
        comment="到账时间"
    )
    
    # 处理信息
    chuli_jieguo = Column(
        Text,
        comment="处理结果"
    )
    
    cuowu_xinxi = Column(
        Text,
        comment="错误信息"
    )
    
    cuowu_daima = Column(
        String(50),
        comment="错误代码"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        comment="备注"
    )
    
    def __repr__(self):
        return f"<ZhifuTuikuan(id={self.id}, danhao={self.tuikuan_danhao}, zhuangtai={self.tuikuan_zhuangtai})>"
