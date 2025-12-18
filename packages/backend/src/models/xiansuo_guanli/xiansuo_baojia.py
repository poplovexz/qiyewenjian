"""
线索报价数据模型
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from ..base import BaseModel


class XiansuoBaojia(BaseModel):
    """线索报价模型"""
    
    __tablename__ = "xiansuo_baojia"
    __table_args__ = {"comment": "线索报价表"}
    
    xiansuo_id = Column(
        String(36),
        ForeignKey("xiansuo.id"),
        nullable=False,
        comment="线索ID"
    )
    
    baojia_bianma = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="报价编码"
    )
    
    baojia_mingcheng = Column(
        String(200),
        nullable=False,
        comment="报价名称"
    )
    
    zongji_jine = Column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
        comment="总计金额"
    )
    
    youxiao_qi = Column(
        DateTime,
        nullable=False,
        comment="有效期"
    )
    
    baojia_zhuangtai = Column(
        String(20),
        default="draft",
        nullable=False,
        comment="报价状态：draft(草稿)、sent(已发送)、accepted(已接受)、rejected(已拒绝)、expired(已过期)"
    )
    
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 报价确认相关字段
    queren_ren_id = Column(
        String(36),
        nullable=True,
        comment="确认人ID（外键关联用户表）"
    )

    queren_shijian = Column(
        DateTime,
        nullable=True,
        comment="确认时间（报价被确认或拒绝的时间戳）"
    )
    
    # 关联关系
    xiansuo = relationship(
        "Xiansuo",
        back_populates="baojia_list"
    )
    
    xiangmu_list = relationship(
        "XiansuoBaojiaXiangmu",
        back_populates="baojia",
        cascade="all, delete-orphan",
        order_by="XiansuoBaojiaXiangmu.paixu"
    )

    hetong_list = relationship(
        "Hetong",
        back_populates="baojia"
    )
    
    @property
    def is_expired(self) -> bool:
        """检查报价是否已过期"""
        return datetime.now() > self.youxiao_qi
    
    @classmethod
    def generate_baojia_bianma(cls) -> str:
        """生成报价编码（包含微秒和随机后缀避免重复）"""
        import random
        import string

        now = datetime.now()
        # 使用微秒级时间戳
        timestamp = now.strftime('%Y%m%d%H%M%S%f')[:-3]  # 保留3位微秒
        # 添加2位随机字符
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        return f"BJ{timestamp}{random_suffix}"
    
    @classmethod
    def get_default_youxiao_qi(cls) -> datetime:
        """获取默认有效期（15天后）"""
        return datetime.now() + timedelta(days=15)
    
    def __repr__(self):
        return f"<XiansuoBaojia(id={self.id}, baojia_bianma={self.baojia_bianma})>"


class XiansuoBaojiaXiangmu(BaseModel):
    """线索报价项目模型"""
    
    __tablename__ = "xiansuo_baojia_xiangmu"
    __table_args__ = {"comment": "线索报价项目表"}
    
    baojia_id = Column(
        String(36),
        ForeignKey("xiansuo_baojia.id"),
        nullable=False,
        comment="报价ID"
    )
    
    chanpin_xiangmu_id = Column(
        String(36),
        ForeignKey("chanpin_xiangmu.id"),
        nullable=False,
        comment="产品项目ID"
    )
    
    xiangmu_mingcheng = Column(
        String(200),
        nullable=False,
        comment="项目名称"
    )
    
    shuliang = Column(
        Numeric(10, 2),
        nullable=False,
        default=1.00,
        comment="数量"
    )
    
    danjia = Column(
        Numeric(10, 2),
        nullable=False,
        default=0.00,
        comment="单价"
    )
    
    xiaoji = Column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
        comment="小计"
    )
    
    danwei = Column(
        String(20),
        default="yuan",
        comment="单位"
    )
    
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )
    
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    baojia = relationship(
        "XiansuoBaojia",
        back_populates="xiangmu_list"
    )
    
    chanpin_xiangmu = relationship(
        "ChanpinXiangmu"
    )
    
    def calculate_xiaoji(self):
        """计算小计"""
        self.xiaoji = self.shuliang * self.danjia
        return self.xiaoji
    
    def __repr__(self):
        return f"<XiansuoBaojiaXiangmu(id={self.id}, xiangmu_mingcheng={self.xiangmu_mingcheng})>"
