#!/usr/bin/env python3
"""
创建用户偏好设置表
"""
import sys
sys.path.insert(0, 'src')

from sqlalchemy import create_engine, text
from core.config import settings


def create_user_preferences_table():
    """创建用户偏好设置表"""
    engine = create_engine(str(settings.DATABASE_URL))

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_preferences (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        preference_key VARCHAR(100) NOT NULL,
        preference_value VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36),
        updated_by VARCHAR(36),
        is_deleted VARCHAR(1) DEFAULT 'N',
        remark VARCHAR(500),
        CONSTRAINT uk_user_preference UNIQUE (user_id, preference_key),
        CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) REFERENCES yonghu(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_preferences_is_deleted ON user_preferences(is_deleted);

    COMMENT ON TABLE user_preferences IS '用户偏好设置表';
    COMMENT ON COLUMN user_preferences.user_id IS '用户ID';
    COMMENT ON COLUMN user_preferences.preference_key IS '偏好键';
    COMMENT ON COLUMN user_preferences.preference_value IS '偏好值';
    COMMENT ON COLUMN user_preferences.created_at IS '创建时间';
    COMMENT ON COLUMN user_preferences.updated_at IS '更新时间';
    COMMENT ON COLUMN user_preferences.created_by IS '创建人';
    COMMENT ON COLUMN user_preferences.updated_by IS '更新人';
    COMMENT ON COLUMN user_preferences.is_deleted IS '是否删除';
    """
    
    with engine.connect() as conn:
        try:
            print("正在创建 user_preferences 表...")
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ user_preferences 表创建成功！")
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    create_user_preferences_table()

