"""
支付回调日志表模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from ..base import BaseModel


class ZhifuHuidiaoRizhi(BaseModel):
    """支付回调日志表"""
    
    __tablename__ = "zhifu_huidiao_rizhi"
    __table_args__ = {"comment": "支付回调日志表"}
    
    # 关联信息
    zhifu_peizhi_id = Column(
        String(36),
        ForeignKey("zhifu_peizhi.id", ondelete="SET NULL"),
        comment="支付配置ID"
    )
    
    # 回调基本信息
    huidiao_leixing = Column(
        String(20),
        nullable=False,
        comment="回调类型：zhifu(支付)、tuikuan(退款)"
    )
    
    zhifu_pingtai = Column(
        String(20),
        nullable=False,
        comment="支付平台：weixin(微信)、zhifubao(支付宝)"
    )
    
    # 请求信息
    qingqiu_url = Column(
        String(500),
        comment="请求URL"
    )
    
    qingqiu_fangfa = Column(
        String(10),
        comment="请求方法：GET、POST"
    )
    
    qingqiu_tou = Column(
        Text,
        comment="请求头（JSON格式）"
    )
    
    qingqiu_shuju = Column(
        Text,
        comment="请求数据（JSON格式）"
    )
    
    # 签名验证
    qianming = Column(
        Text,
        comment="签名"
    )
    
    qianming_yanzheng = Column(
        String(20),
        comment="签名验证：chenggong(成功)、shibai(失败)、weiyanzhen(未验证)"
    )
    
    # 处理信息
    chuli_zhuangtai = Column(
        String(20),
        comment="处理状态：chenggong(成功)、shibai(失败)、chuli_zhong(处理中)"
    )
    
    chuli_jieguo = Column(
        Text,
        comment="处理结果"
    )
    
    cuowu_xinxi = Column(
        Text,
        comment="错误信息"
    )
    
    # 时间信息
    jieshou_shijian = Column(
        DateTime,
        comment="接收时间"
    )
    
    chuli_shijian = Column(
        DateTime,
        comment="处理时间"
    )
    
    def __repr__(self):
        return f"<ZhifuHuidiaoRizhi(id={self.id}, leixing={self.huidiao_leixing}, pingtai={self.zhifu_pingtai})>"

