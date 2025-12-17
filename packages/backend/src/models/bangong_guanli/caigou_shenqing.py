"""
采购申请数据模型
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel


class CaigouShenqing(BaseModel):
    """采购申请表"""
    
    __tablename__ = "caigou_shenqing"
    __table_args__ = {"comment": "采购申请表"}
    
    # 申请基本信息
    shenqing_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="申请编号，如CG202411110001"
    )
    
    shenqing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id", ondelete="CASCADE"),
        nullable=False,
        comment="申请人ID"
    )
    
    # 采购信息
    caigou_leixing = Column(
        String(50),
        nullable=False,
        comment="采购类型：bangongyongpin(办公用品)、shebei(设备)、ruanjian(软件)、fuwu(服务)"
    )
    
    caigou_mingcheng = Column(
        String(200),
        nullable=False,
        comment="采购物品名称"
    )
    
    caigou_shuliang = Column(
        Integer,
        nullable=False,
        comment="采购数量"
    )
    
    danwei = Column(
        String(20),
        nullable=False,
        comment="单位（个、台、套、件等）"
    )
    
    yugu_jine = Column(
        Numeric(15, 2),
        nullable=False,
        comment="预估金额"
    )
    
    shiji_jine = Column(
        Numeric(15, 2),
        nullable=True,
        comment="实际金额"
    )
    
    caigou_yuanyin = Column(
        Text,
        nullable=False,
        comment="采购原因"
    )
    
    # 时间信息
    yaoqiu_shijian = Column(
        DateTime,
        nullable=True,
        comment="要求到货时间"
    )
    
    # 供应商信息
    gongyingshang_xinxi = Column(
        Text,
        nullable=True,
        comment="供应商信息（JSON格式）"
    )
    
    # 附件信息
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径（报价单等），多个文件用逗号分隔"
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
    
    # 采购状态
    caigou_zhuangtai = Column(
        String(20),
        default="daicaigou",
        nullable=False,
        comment="采购状态：daicaigou(待采购)、caigouzhong(采购中)、yidaohuo(已到货)、yiyanshou(已验收)"
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
        return f"<CaigouShenqing(id={self.id}, shenqing_bianhao={self.shenqing_bianhao}, caigou_mingcheng={self.caigou_mingcheng})>"

