"""
合规事项实例表
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel


class HeguishixiangShili(BaseModel):
    """合规事项实例表"""

    __tablename__ = "heguishixiang_shili"
    __table_args__ = {"comment": "合规事项实例表"}

    # 关联信息
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )

    heguishixiang_moban_id = Column(
        String(36),
        ForeignKey("heguishixiang_moban.id", ondelete="CASCADE"),
        nullable=False,
        comment="合规事项模板ID"
    )

    kehu_heguishixiang_id = Column(
        String(36),
        ForeignKey("kehu_heguishixiang.id", ondelete="CASCADE"),
        nullable=True,
        comment="客户合规事项配置ID"
    )

    # 实例基本信息
    shili_bianhao = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="实例编号"
    )

    shili_mingcheng = Column(
        String(200),
        nullable=False,
        comment="实例名称"
    )

    shenbao_qijian = Column(
        String(50),
        nullable=False,
        comment="申报期间：如2024年1月、2024年第1季度、2024年度"
    )

    # 时间管理
    jihua_kaishi_shijian = Column(
        DateTime,
        nullable=True,
        comment="计划开始时间"
    )

    jihua_jieshu_shijian = Column(
        DateTime,
        nullable=False,
        comment="计划结束时间（法定截止时间）"
    )

    shiji_kaishi_shijian = Column(
        DateTime,
        nullable=True,
        comment="实际开始时间"
    )

    shiji_jieshu_shijian = Column(
        DateTime,
        nullable=True,
        comment="实际结束时间"
    )

    # 状态管理
    shili_zhuangtai = Column(
        String(20),
        default="pending",
        comment="实例状态：pending(待处理)、in_progress(进行中)、completed(已完成)、overdue(已逾期)、cancelled(已取消)"
    )

    wancheng_jindu = Column(
        Integer,
        default=0,
        comment="完成进度（0-100）"
    )

    # 负责人信息
    fuzeren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="负责人ID"
    )

    fenpei_shijian = Column(
        DateTime,
        nullable=True,
        comment="分配时间"
    )

    # 完成信息
    wancheng_qingkuang = Column(
        Text,
        nullable=True,
        comment="完成情况说明"
    )

    jiaofei_wenjian = Column(
        Text,
        nullable=True,
        comment="交付文件列表（JSON数组）"
    )

    shenhe_zhuangtai = Column(
        String(20),
        default="pending",
        comment="审核状态：pending(待审核)、approved(已通过)、rejected(已拒绝)"
    )

    shenhe_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="审核人ID"
    )

    shenhe_shijian = Column(
        DateTime,
        nullable=True,
        comment="审核时间"
    )

    shenhe_yijian = Column(
        Text,
        nullable=True,
        comment="审核意见"
    )

    # 风险管理
    fengxian_dengji = Column(
        String(20),
        default="medium",
        comment="风险等级：low(低)、medium(中)、high(高)、critical(严重)"
    )

    yuqi_tianshu = Column(
        Integer,
        default=0,
        comment="逾期天数"
    )

    yuqi_fengxian_pinggu = Column(
        Text,
        nullable=True,
        comment="逾期风险评估"
    )

    # 关联工单
    fuwu_gongdan_id = Column(
        String(36),
        ForeignKey("fuwu_gongdan.id"),
        nullable=True,
        comment="关联的服务工单ID"
    )

    # 提醒记录
    tixing_cishu = Column(
        Integer,
        default=0,
        comment="提醒次数"
    )

    zuijin_tixing_shijian = Column(
        DateTime,
        nullable=True,
        comment="最近提醒时间"
    )

    # 扩展信息
    kuozhan_shuju = Column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )

    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 关联关系
    kehu = relationship("Kehu")
    heguishixiang_moban = relationship("HeguishixiangMoban", back_populates="heguishixiang_shili_list")
    kehu_heguishixiang = relationship("KehuHeguishixiang", back_populates="heguishixiang_shili_list")
    fuzeren = relationship("Yonghu", foreign_keys=[fuzeren_id])
    shenhe_ren = relationship("Yonghu", foreign_keys=[shenhe_ren_id])
    fuwu_gongdan = relationship("FuwuGongdan")

    tixing_jilu_list = relationship(
        "TixingJilu",
        back_populates="heguishixiang_shili",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<HeguishixiangShili(shili_bianhao='{self.shili_bianhao}', shenbao_qijian='{self.shenbao_qijian}', shili_zhuangtai='{self.shili_zhuangtai}')>"
