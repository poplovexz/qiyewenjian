"""
系统配置模型
"""
from sqlalchemy import Column, String, Text, Integer
from models.base import BaseModel

class SystemConfig(BaseModel):
    """系统配置表"""
    __tablename__ = 'system_config'
    __table_args__ = {'comment': '系统配置表'}

    config_key = Column(String(100), unique=True, nullable=False, index=True, comment='配置键')
    config_value = Column(Text, comment='配置值')
    config_type = Column(String(50), nullable=False, comment='配置类型：security/cache/business/system')
    config_name = Column(String(200), comment='配置名称')
    config_desc = Column(Text, comment='配置描述')
    default_value = Column(Text, comment='默认值')
    value_type = Column(String(50), comment='值类型：string/int/float/bool/json')
    is_editable = Column(String(1), default='Y', comment='是否可编辑：Y/N')
    sort_order = Column(Integer, default=0, comment='排序')
