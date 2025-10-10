"""
服务工单管理模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from ..base import BaseModel


class FuwuGongdan(BaseModel):
    """服务工单表"""
    
    __tablename__ = "fuwu_gongdan"
    __table_args__ = {"comment": "服务工单表"}
    
    # 关联信息
    hetong_id = Column(
        String(36),
        ForeignKey("hetong.id"),
        nullable=False,
        comment="关联合同ID"
    )
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id"),
        nullable=False,
        comment="客户ID"
    )
    
    zhixing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="执行人ID（会计师）"
    )
    
    # 工单基本信息
    gongdan_bianhao = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="工单编号"
    )
    
    gongdan_biaoti = Column(
        String(200),
        nullable=False,
        comment="工单标题"
    )
    
    gongdan_miaoshu = Column(
        Text,
        nullable=True,
        comment="工单描述"
    )
    
    fuwu_leixing = Column(
        String(50),
        nullable=False,
        comment="服务类型：daili_jizhang-代理记账，shuiwu_shenbao-税务申报，caiwu_zixun-财务咨询，qita_fuwu-其他服务"
    )
    
    # 优先级和状态
    youxian_ji = Column(
        String(20),
        default="medium",
        nullable=False,
        comment="优先级：low-低，medium-中，high-高，urgent-紧急"
    )
    
    gongdan_zhuangtai = Column(
        String(20),
        default="created",
        nullable=False,
        comment="工单状态：created-已创建，assigned-已分配，in_progress-进行中，pending_review-待审核，completed-已完成，cancelled-已取消"
    )
    
    # 时间信息
    jihua_kaishi_shijian = Column(
        DateTime,
        nullable=True,
        comment="计划开始时间"
    )
    
    jihua_jieshu_shijian = Column(
        DateTime,
        nullable=False,
        comment="计划结束时间"
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
    
    # 分配信息
    fenpei_shijian = Column(
        DateTime,
        nullable=True,
        comment="分配时间"
    )
    
    fenpei_ren_id = Column(
        String(36),
        nullable=True,
        comment="分配人ID"
    )
    
    fenpei_beizhu = Column(
        String(500),
        nullable=True,
        comment="分配备注"
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
        comment="交付文件列表（JSON格式）"
    )
    
    # 客户反馈
    kehu_queren_shijian = Column(
        DateTime,
        nullable=True,
        comment="客户确认时间"
    )
    
    kehu_pingjia = Column(
        String(20),
        nullable=True,
        comment="客户评价：excellent-非常满意，good-满意，average-一般，poor-不满意"
    )
    
    kehu_pingjia_neirong = Column(
        Text,
        nullable=True,
        comment="客户评价内容"
    )
    
    # 关联关系
    hetong = relationship("Hetong", back_populates="fuwu_gongdan_list")
    kehu = relationship("Kehu", back_populates="fuwu_gongdan_list")
    xiangmu_list = relationship(
        "FuwuGongdanXiangmu",
        back_populates="gongdan",
        cascade="all, delete-orphan",
        order_by="FuwuGongdanXiangmu.paixu"
    )
    rizhi_list = relationship(
        "FuwuGongdanRizhi",
        back_populates="gongdan",
        cascade="all, delete-orphan",
        order_by="FuwuGongdanRizhi.created_at.desc()"
    )
    
    @classmethod
    def generate_gongdan_bianhao(cls) -> str:
        """生成工单编号"""
        import random
        import string
        
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return f"WO{timestamp}{random_suffix}"
    
    @property
    def is_overdue(self) -> bool:
        """检查是否已逾期"""
        if self.gongdan_zhuangtai in ["completed", "cancelled"]:
            return False
        return datetime.now() > self.jihua_jieshu_shijian
    
    @property
    def progress_percentage(self) -> int:
        """计算进度百分比"""
        if not self.xiangmu_list:
            return 0
        
        completed_count = sum(1 for item in self.xiangmu_list if item.xiangmu_zhuangtai == "completed")
        total_count = len(self.xiangmu_list)
        
        return int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    def __repr__(self) -> str:
        return f"<FuwuGongdan(gongdan_bianhao='{self.gongdan_bianhao}', gongdan_zhuangtai='{self.gongdan_zhuangtai}')>"


class FuwuGongdanXiangmu(BaseModel):
    """服务工单项目表"""
    
    __tablename__ = "fuwu_gongdan_xiangmu"
    __table_args__ = {"comment": "服务工单项目表"}
    
    gongdan_id = Column(
        String(36),
        ForeignKey("fuwu_gongdan.id"),
        nullable=False,
        comment="工单ID"
    )
    
    xiangmu_mingcheng = Column(
        String(200),
        nullable=False,
        comment="项目名称"
    )
    
    xiangmu_miaoshu = Column(
        Text,
        nullable=True,
        comment="项目描述"
    )
    
    xiangmu_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="项目状态：pending-待处理，in_progress-进行中，completed-已完成，skipped-已跳过"
    )
    
    paixu = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    
    jihua_gongshi = Column(
        Numeric(5, 2),
        nullable=True,
        comment="计划工时"
    )
    
    shiji_gongshi = Column(
        Numeric(5, 2),
        nullable=True,
        comment="实际工时"
    )
    
    kaishi_shijian = Column(
        DateTime,
        nullable=True,
        comment="开始时间"
    )
    
    jieshu_shijian = Column(
        DateTime,
        nullable=True,
        comment="结束时间"
    )
    
    beizhu = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    gongdan = relationship("FuwuGongdan", back_populates="xiangmu_list")
    
    def __repr__(self) -> str:
        return f"<FuwuGongdanXiangmu(xiangmu_mingcheng='{self.xiangmu_mingcheng}', xiangmu_zhuangtai='{self.xiangmu_zhuangtai}')>"


class FuwuGongdanRizhi(BaseModel):
    """服务工单日志表"""
    
    __tablename__ = "fuwu_gongdan_rizhi"
    __table_args__ = {"comment": "服务工单日志表"}
    
    gongdan_id = Column(
        String(36),
        ForeignKey("fuwu_gongdan.id"),
        nullable=False,
        comment="工单ID"
    )
    
    caozuo_leixing = Column(
        String(50),
        nullable=False,
        comment="操作类型：created-创建，assigned-分配，started-开始，paused-暂停，completed-完成，cancelled-取消，commented-评论"
    )
    
    caozuo_neirong = Column(
        Text,
        nullable=False,
        comment="操作内容"
    )
    
    caozuo_ren_id = Column(
        String(36),
        nullable=False,
        comment="操作人ID"
    )
    
    fujian_lujing = Column(
        String(500),
        nullable=True,
        comment="附件路径"
    )
    
    # 关联关系
    gongdan = relationship("FuwuGongdan", back_populates="rizhi_list")
    
    def __repr__(self) -> str:
        return f"<FuwuGongdanRizhi(caozuo_leixing='{self.caozuo_leixing}', caozuo_ren_id='{self.caozuo_ren_id}')>"
