"""
合规事项模板表
"""
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel


class HeguishixiangMoban(BaseModel):
    """合规事项模板表"""

    __tablename__ = "heguishixiang_moban"
    __table_args__ = {"comment": "合规事项模板表"}

    # 基本信息
    shixiang_mingcheng = Column(
        String(200),
        nullable=False,
        comment="事项名称"
    )

    shixiang_bianma = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="事项编码"
    )

    shixiang_leixing = Column(
        String(50),
        nullable=False,
        comment="事项类型：shuiwu_shenbao(税务申报)、nianbao_shenbao(年报申报)、zhizhao_nianjian(执照年检)、qita_heguishixiang(其他合规事项)"
    )

    # 申报周期配置
    shenbao_zhouqi = Column(
        String(50),
        nullable=False,
        comment="申报周期：monthly(月度)、quarterly(季度)、annually(年度)、custom(自定义)"
    )

    # 截止时间规则
    jiezhi_shijian_guize = Column(
        Text,
        nullable=False,
        comment="截止时间规则（JSON格式）：如每月15日、每季度末次月15日等"
    )

    # 提前提醒配置
    tiqian_tixing_tianshu = Column(
        String(100),
        default="15,7,3,1",
        comment="提前提醒天数（逗号分隔）：如15,7,3,1表示提前15天、7天、3天、1天提醒"
    )

    # 适用范围
    shiyong_qiye_leixing = Column(
        Text,
        nullable=True,
        comment="适用企业类型（JSON数组）：如['一般纳税人','小规模纳税人']"
    )

    shiyong_hangye = Column(
        Text,
        nullable=True,
        comment="适用行业（JSON数组）"
    )

    # 事项描述
    shixiang_miaoshu = Column(
        Text,
        nullable=True,
        comment="事项描述"
    )

    banli_liucheng = Column(
        Text,
        nullable=True,
        comment="办理流程说明"
    )

    suoxu_cailiao = Column(
        Text,
        nullable=True,
        comment="所需材料清单（JSON数组）"
    )

    # 法规依据
    fagui_yiju = Column(
        Text,
        nullable=True,
        comment="法规依据"
    )

    # 风险等级
    fengxian_dengji = Column(
        String(20),
        default="medium",
        comment="风险等级：low(低)、medium(中)、high(高)、critical(严重)"
    )

    # 状态管理
    moban_zhuangtai = Column(
        String(20),
        default="active",
        comment="模板状态：active(启用)、inactive(停用)、draft(草稿)"
    )

    # 排序和分组
    paixu = Column(
        Integer,
        default=0,
        comment="排序号"
    )

    fenlei_biaoqian = Column(
        String(200),
        nullable=True,
        comment="分类标签（逗号分隔）"
    )

    # 扩展信息
    kuozhan_shuju = Column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )

    # 关联关系
    kehu_heguishixiang_list = relationship(
        "KehuHeguishixiang",
        back_populates="heguishixiang_moban",
        cascade="all, delete-orphan"
    )

    heguishixiang_shili_list = relationship(
        "HeguishixiangShili",
        back_populates="heguishixiang_moban",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<HeguishixiangMoban(shixiang_mingcheng='{self.shixiang_mingcheng}', shixiang_leixing='{self.shixiang_leixing}', moban_zhuangtai='{self.moban_zhuangtai}')>"
