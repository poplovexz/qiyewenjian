"""
账簿表模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey


from ..base import BaseModel


class Zhangbu(BaseModel):
    """账簿表"""
    
    __tablename__ = "zhangbu"
    __table_args__ = {"comment": "账簿表"}
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    pingzheng_id = Column(
        String(36),
        ForeignKey("pingzheng.id"),
        nullable=False,
        comment="凭证ID"
    )
    
    # 账簿基本信息
    zhangbu_leixing = Column(
        String(20),
        nullable=False,
        comment="账簿类型：zongzhang-总账，mingxizhang-明细账，rixuzhang-日序账"
    )
    
    kuaiji_kemu = Column(
        String(100),
        nullable=False,
        comment="会计科目"
    )
    
    kemu_bianma = Column(
        String(20),
        nullable=False,
        comment="科目编码"
    )
    
    # 金额信息
    jiebie_jine = Column(
        Numeric(15, 2),
        default=0.00,
        comment="借方金额"
    )
    
    daifang_jine = Column(
        Numeric(15, 2),
        default=0.00,
        comment="贷方金额"
    )
    
    yue_fangxiang = Column(
        String(10),
        nullable=False,
        comment="余额方向：jie-借方，dai-贷方"
    )
    
    qichu_yue = Column(
        Numeric(15, 2),
        default=0.00,
        comment="期初余额"
    )
    
    qimo_yue = Column(
        Numeric(15, 2),
        default=0.00,
        comment="期末余额"
    )
    
    # 时间信息
    kuaiji_qijian = Column(
        String(7),
        nullable=False,
        comment="会计期间（YYYY-MM）"
    )
    
    dengji_riqi = Column(
        DateTime,
        nullable=False,
        comment="登记日期"
    )
    
    # 摘要信息
    zhaiyao = Column(
        String(200),
        nullable=True,
        comment="摘要"
    )
    
    # 对方科目
    duifang_kemu = Column(
        String(100),
        nullable=True,
        comment="对方科目"
    )
    
    def __repr__(self) -> str:
        return f"<Zhangbu(kuaiji_kemu='{self.kuaiji_kemu}', kuaiji_qijian='{self.kuaiji_qijian}')>"
