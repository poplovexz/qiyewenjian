"""
合同乙方主体表模型
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from ..base import BaseModel

class HetongYifangZhuti(BaseModel):
    """合同乙方主体表"""
    
    __tablename__ = "hetong_yifang_zhuti"
    __table_args__ = {"comment": "合同乙方主体表"}
    
    # 基本信息
    zhuti_mingcheng = Column(
        String(200),
        nullable=False,
        comment="主体名称"
    )
    
    zhuti_leixing = Column(
        String(50),
        nullable=False,
        comment="主体类型：geren(个人)、gongsi(公司)、hehuo(合伙企业)、qita(其他)"
    )
    
    # 联系信息
    lianxi_ren = Column(
        String(100),
        nullable=False,
        comment="联系人"
    )
    
    lianxi_dianhua = Column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    
    lianxi_youxiang = Column(
        String(100),
        nullable=True,
        comment="联系邮箱"
    )
    
    # 地址信息
    zhuce_dizhi = Column(
        String(500),
        nullable=True,
        comment="注册地址"
    )
    
    tongxin_dizhi = Column(
        String(500),
        nullable=True,
        comment="通信地址"
    )
    
    # 证件信息
    zhengjianhao = Column(
        String(100),
        nullable=True,
        comment="证件号码（身份证号/统一社会信用代码等）"
    )
    
    zhengjianleixing = Column(
        String(50),
        nullable=True,
        comment="证件类型：shenfenzheng(身份证)、yingyezhizhao(营业执照)、qita(其他)"
    )
    
    # 银行信息
    kaihuhang = Column(
        String(200),
        nullable=True,
        comment="开户行"
    )
    
    yinhangzhanghu = Column(
        String(50),
        nullable=True,
        comment="银行账户"
    )
    
    # 状态信息
    zhuti_zhuangtai = Column(
        String(20),
        default="active",
        nullable=False,
        comment="主体状态：active(启用)、inactive(停用)"
    )
    
    # 备注信息
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    hetong_list = relationship("Hetong", back_populates="yifang_zhuti")
    zhifu_fangshi_list = relationship("HetongZhifuFangshi", back_populates="yifang_zhuti")
    
    def __repr__(self) -> str:
        return f"<HetongYifangZhuti(zhuti_mingcheng='{self.zhuti_mingcheng}', zhuti_leixing='{self.zhuti_leixing}')>"
