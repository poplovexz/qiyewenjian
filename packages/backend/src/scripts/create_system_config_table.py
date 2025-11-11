#!/usr/bin/env python3
"""
创建系统配置表并初始化默认配置
"""
import sys
sys.path.insert(0, 'src')

import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from core.config import settings


def create_system_config_table():
    """创建系统配置表并初始化默认配置"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    # 创建表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS system_config (
        id VARCHAR(36) PRIMARY KEY,
        config_key VARCHAR(100) NOT NULL UNIQUE,
        config_value TEXT,
        config_type VARCHAR(50) NOT NULL,
        config_name VARCHAR(200),
        config_desc TEXT,
        default_value TEXT,
        value_type VARCHAR(50),
        is_editable VARCHAR(1) DEFAULT 'Y',
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36),
        updated_by VARCHAR(36),
        is_deleted VARCHAR(1) DEFAULT 'N',
        CONSTRAINT idx_system_config_key UNIQUE (config_key)
    );
    
    CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type);
    CREATE INDEX IF NOT EXISTS idx_system_config_is_deleted ON system_config(is_deleted);
    
    COMMENT ON TABLE system_config IS '系统配置表';
    COMMENT ON COLUMN system_config.config_key IS '配置键';
    COMMENT ON COLUMN system_config.config_value IS '配置值';
    COMMENT ON COLUMN system_config.config_type IS '配置类型';
    COMMENT ON COLUMN system_config.config_name IS '配置名称';
    COMMENT ON COLUMN system_config.config_desc IS '配置描述';
    COMMENT ON COLUMN system_config.default_value IS '默认值';
    COMMENT ON COLUMN system_config.value_type IS '值类型';
    COMMENT ON COLUMN system_config.is_editable IS '是否可编辑';
    COMMENT ON COLUMN system_config.sort_order IS '排序';
    """
    
    # 默认配置数据
    default_configs = [
        # 安全配置
        {
            'config_key': 'token_expire_hours',
            'config_value': '8',
            'config_type': 'security',
            'config_name': 'Token过期时间（小时）',
            'config_desc': 'JWT Token的过期时间，单位：小时',
            'default_value': '8',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 1
        },
        {
            'config_key': 'refresh_token_expire_days',
            'config_value': '30',
            'config_type': 'security',
            'config_name': '刷新Token过期时间（天）',
            'config_desc': '刷新Token的过期时间，单位：天',
            'default_value': '30',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 2
        },
        {
            'config_key': 'password_min_length',
            'config_value': '6',
            'config_type': 'security',
            'config_name': '密码最小长度',
            'config_desc': '用户密码的最小长度要求',
            'default_value': '6',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 3
        },
        # 缓存配置
        {
            'config_key': 'cache_default_minutes',
            'config_value': '15',
            'config_type': 'cache',
            'config_name': '默认缓存时间（分钟）',
            'config_desc': '默认缓存过期时间，单位：分钟',
            'default_value': '15',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 1
        },
        {
            'config_key': 'cache_long_hours',
            'config_value': '24',
            'config_type': 'cache',
            'config_name': '长期缓存时间（小时）',
            'config_desc': '长期缓存过期时间，单位：小时',
            'default_value': '24',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 2
        },
        {
            'config_key': 'cache_short_seconds',
            'config_value': '60',
            'config_type': 'cache',
            'config_name': '短期缓存时间（秒）',
            'config_desc': '短期缓存过期时间，单位：秒',
            'default_value': '60',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 3
        },
        # 业务参数
        {
            'config_key': 'contract_price_diff_threshold',
            'config_value': '0.05',
            'config_type': 'business',
            'config_name': '合同价格差异审核阈值',
            'config_desc': '合同价格与报价差异超过此比例时触发审核（如：0.05表示5%）',
            'default_value': '0.05',
            'value_type': 'float',
            'is_editable': 'Y',
            'sort_order': 1
        },
        {
            'config_key': 'compliance_remind_days',
            'config_value': '15,7,3,1',
            'config_type': 'business',
            'config_name': '合规提醒天数',
            'config_desc': '合规事项到期前提醒的天数，多个值用逗号分隔',
            'default_value': '15,7,3,1',
            'value_type': 'string',
            'is_editable': 'Y',
            'sort_order': 2
        },
        {
            'config_key': 'audit_timeout_hours',
            'config_value': '24',
            'config_type': 'business',
            'config_name': '审核超时提醒时间（小时）',
            'config_desc': '审核超过此时间未处理时发送提醒，单位：小时',
            'default_value': '24',
            'value_type': 'int',
            'is_editable': 'Y',
            'sort_order': 3
        },
        # 系统信息
        {
            'config_key': 'system_name',
            'config_value': '代理记账营运内部系统',
            'config_type': 'system',
            'config_name': '系统名称',
            'config_desc': '系统的显示名称',
            'default_value': '代理记账营运内部系统',
            'value_type': 'string',
            'is_editable': 'N',
            'sort_order': 1
        },
        {
            'config_key': 'system_version',
            'config_value': '1.0.0',
            'config_type': 'system',
            'config_name': '系统版本',
            'config_desc': '当前系统版本号',
            'default_value': '1.0.0',
            'value_type': 'string',
            'is_editable': 'N',
            'sort_order': 2
        }
    ]
    
    with engine.connect() as conn:
        try:
            print("正在创建 system_config 表...")
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ system_config 表创建成功！")
            
            # 插入默认配置
            print("\n正在插入默认配置...")
            for config in default_configs:
                config_id = str(uuid.uuid4())
                now = datetime.now()
                
                insert_sql = text("""
                    INSERT INTO system_config (
                        id, config_key, config_value, config_type, config_name,
                        config_desc, default_value, value_type, is_editable,
                        sort_order, created_at, updated_at, is_deleted
                    ) VALUES (
                        :id, :config_key, :config_value, :config_type, :config_name,
                        :config_desc, :default_value, :value_type, :is_editable,
                        :sort_order, :created_at, :updated_at, 'N'
                    )
                    ON CONFLICT (config_key) DO NOTHING
                """)
                
                conn.execute(insert_sql, {
                    'id': config_id,
                    'config_key': config['config_key'],
                    'config_value': config['config_value'],
                    'config_type': config['config_type'],
                    'config_name': config['config_name'],
                    'config_desc': config['config_desc'],
                    'default_value': config['default_value'],
                    'value_type': config['value_type'],
                    'is_editable': config['is_editable'],
                    'sort_order': config['sort_order'],
                    'created_at': now,
                    'updated_at': now
                })
                
                print(f"  ✓ {config['config_name']}")
            
            conn.commit()
            print(f"\n✅ 成功插入 {len(default_configs)} 条默认配置！")
            
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    create_system_config_table()

