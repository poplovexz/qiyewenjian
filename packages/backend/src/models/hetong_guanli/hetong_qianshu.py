"""
合同签署模型
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.mysql import CHAR
from src.core.database import Base
from src.core.mixins import TimestampMixin, UUIDMixin
import uuid
from datetime import datetime


class HetongQianshu(Base, UUIDMixin, TimestampMixin):
    """合同签署模型"""
    __tablename__ = "hetong_qianshu"
    __table_args__ = {'comment': '合同签署表'}

    # 基本信息
    hetong_id = Column(CHAR(36), nullable=False, comment="合同ID")
    qianshu_lianjie = Column(String(500), nullable=False, comment="签署链接")
    qianshu_token = Column(String(100), nullable=False, unique=True, comment="签署令牌")
    qianshu_zhuangtai = Column(String(20), nullable=False, default="daiqianshu", comment="签署状态：daiqianshu-待签署，yiqianshu-已签署，guoqi-已过期")
    
    # 签署信息
    qianshu_ren_mingcheng = Column(String(100), comment="签署人姓名")
    qianshu_ren_dianhua = Column(String(20), comment="签署人电话")
    qianshu_ren_youxiang = Column(String(100), comment="签署人邮箱")
    qianshu_shijian = Column(DateTime, comment="签署时间")
    qianshu_ip = Column(String(50), comment="签署IP地址")
    qianshu_shebei = Column(String(200), comment="签署设备信息")
    
    # 签名信息
    qianming_tupian = Column(Text, comment="签名图片Base64")
    qianming_zuobiao = Column(String(100), comment="签名坐标")
    qianming_daxiao = Column(String(50), comment="签名大小")
    
    # 有效期设置
    youxiao_kaishi = Column(DateTime, nullable=False, default=datetime.utcnow, comment="有效期开始时间")
    youxiao_jieshu = Column(DateTime, nullable=False, comment="有效期结束时间")
    
    # 其他信息
    beizhu = Column(Text, comment="备注")
    is_deleted = Column(String(1), nullable=False, default="N", comment="是否删除：Y-是，N-否")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.qianshu_token:
            self.qianshu_token = str(uuid.uuid4()).replace('-', '')

    def __repr__(self):
        return f"<HetongQianshu(id='{self.id}', hetong_id='{self.hetong_id}', qianshu_zhuangtai='{self.qianshu_zhuangtai}')>"
