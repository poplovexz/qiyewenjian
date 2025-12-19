"""
工作交接单数据模型
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class GongzuoJiaojie(BaseModel):
    """工作交接单表"""
    
    __tablename__ = "gongzuo_jiaojie"
    __table_args__ = {"comment": "工作交接单表"}
    
    # 交接基本信息
    jiaojie_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="交接编号，如JJ202411110001"
    )
    
    jiaojie_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="交接人ID"
    )
    
    jieshou_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="接收人ID"
    )
    
    # 交接信息
    jiaojie_yuanyin = Column(
        String(50),
        nullable=False,
        comment="交接原因：lizhi(离职)、diaogang(调岗)、xiujia(休假)、qita(其他)"
    )
    
    jiaojie_shijian = Column(
        DateTime,
        nullable=False,
        comment="交接时间"
    )
    
    # 交接内容
    jiaojie_neirong = Column(
        Text,
        nullable=True,
        comment="交接内容（JSON格式，包含多个交接项）"
    )
    
    wenjian_qingdan = Column(
        Text,
        nullable=True,
        comment="文件清单（JSON格式）"
    )
    
    shebei_qingdan = Column(
        Text,
        nullable=True,
        comment="设备清单（JSON格式）"
    )
    
    zhanghu_qingdan = Column(
        Text,
        nullable=True,
        comment="账号清单（JSON格式）"
    )
    
    daiban_shixiang = Column(
        Text,
        nullable=True,
        comment="待办事项（JSON格式）"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径，多个文件用逗号分隔"
    )
    
    # 交接状态
    jiaojie_zhuangtai = Column(
        String(20),
        default="jiaojiezhong",
        nullable=False,
        comment="交接状态：jiaojiezhong(交接中)、yiwancheng(已完成)、yiqueren(已确认)"
    )
    
    # 确认信息
    queren_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="确认人ID（通常是部门负责人）"
    )
    
    queren_shijian = Column(
        DateTime,
        nullable=True,
        comment="确认时间"
    )
    
    # 备注
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    jiaojie_ren = relationship("Yonghu", foreign_keys=[jiaojie_ren_id])
    jieshou_ren = relationship("Yonghu", foreign_keys=[jieshou_ren_id])
    queren_ren = relationship("Yonghu", foreign_keys=[queren_ren_id])
    
    def __repr__(self) -> str:
        return f"<GongzuoJiaojie(id={self.id}, jiaojie_bianhao={self.jiaojie_bianhao}, jiaojie_zhuangtai={self.jiaojie_zhuangtai})>"
