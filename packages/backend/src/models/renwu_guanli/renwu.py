"""
任务表模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey


from ..base import BaseModel


class Renwu(BaseModel):
    """任务表"""
    
    __tablename__ = "renwu"
    __table_args__ = {"comment": "任务表"}
    
    kehu_id = Column(
        String(36),
        ForeignKey("kehu.id", ondelete="CASCADE"),
        nullable=False,
        comment="客户ID"
    )
    
    zhixing_ren_id = Column(
        String(36),
        ForeignKey("yonghu.id"),
        nullable=True,
        comment="执行人ID（会计）"
    )
    
    # 任务基本信息
    renwu_biaoti = Column(
        String(200),
        nullable=False,
        comment="任务标题"
    )
    
    renwu_miaoshu = Column(
        Text,
        nullable=True,
        comment="任务描述"
    )
    
    renwu_leixing = Column(
        String(50),
        nullable=False,
        comment="任务类型：zhangwu_chuli-账务处理，shuiwu_shenbao-税务申报，baobiao_shengcheng-报表生成，zixun_fuwu-咨询服务"
    )
    
    # 任务优先级和状态
    youxian_ji = Column(
        String(20),
        default="medium",
        nullable=False,
        comment="优先级：low-低，medium-中，high-高，urgent-紧急"
    )
    
    renwu_zhuangtai = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="任务状态：pending-待处理，assigned-已分配，in_progress-进行中，completed-已完成，cancelled-已取消"
    )
    
    # 时间信息
    jihua_kaishi = Column(
        DateTime,
        nullable=True,
        comment="计划开始时间"
    )
    
    jihua_jieshu = Column(
        DateTime,
        nullable=False,
        comment="计划结束时间"
    )
    
    shiji_kaishi = Column(
        DateTime,
        nullable=True,
        comment="实际开始时间"
    )
    
    shiji_jieshu = Column(
        DateTime,
        nullable=True,
        comment="实际结束时间"
    )
    
    # 分配信息
    fenpei_riqi = Column(
        DateTime,
        nullable=True,
        comment="分配日期"
    )
    
    fenpei_ren_id = Column(
        String(36),
        nullable=True,
        comment="分配人ID"
    )
    
    fenpei_yuanyin = Column(
        String(200),
        nullable=True,
        comment="分配原因"
    )
    
    # 完成信息
    wancheng_qingkuang = Column(
        Text,
        nullable=True,
        comment="完成情况说明"
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
    
    def __repr__(self) -> str:
        return f"<Renwu(renwu_biaoti='{self.renwu_biaoti}', renwu_zhuangtai='{self.renwu_zhuangtai}')>"
