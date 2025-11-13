"""创建部署历史表"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from core.config import settings

def create_deploy_history_table():
    """创建部署历史表"""
    engine = create_engine(str(settings.DATABASE_URL))

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS deploy_history (
        id SERIAL PRIMARY KEY,
        environment VARCHAR(50) NOT NULL DEFAULT 'production',
        branch VARCHAR(100) NOT NULL DEFAULT 'main',
        commit_hash VARCHAR(40),
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        deployed_by VARCHAR(100) NOT NULL,
        description TEXT,
        logs TEXT,
        error_message TEXT,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        duration INTEGER,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_deleted VARCHAR(1) NOT NULL DEFAULT 'N'
    );
    
    COMMENT ON TABLE deploy_history IS '部署历史记录表';
    COMMENT ON COLUMN deploy_history.id IS '部署ID';
    COMMENT ON COLUMN deploy_history.environment IS '部署环境: production/staging/development';
    COMMENT ON COLUMN deploy_history.branch IS 'Git分支名称';
    COMMENT ON COLUMN deploy_history.commit_hash IS 'Git提交哈希';
    COMMENT ON COLUMN deploy_history.status IS '部署状态: pending/running/success/failed/cancelled';
    COMMENT ON COLUMN deploy_history.deployed_by IS '部署人用户名';
    COMMENT ON COLUMN deploy_history.description IS '部署说明';
    COMMENT ON COLUMN deploy_history.logs IS '部署日志';
    COMMENT ON COLUMN deploy_history.error_message IS '错误信息';
    COMMENT ON COLUMN deploy_history.started_at IS '开始时间';
    COMMENT ON COLUMN deploy_history.completed_at IS '完成时间';
    COMMENT ON COLUMN deploy_history.duration IS '耗时（秒）';
    COMMENT ON COLUMN deploy_history.created_at IS '创建时间';
    COMMENT ON COLUMN deploy_history.updated_at IS '更新时间';
    COMMENT ON COLUMN deploy_history.is_deleted IS '是否删除: Y/N';
    
    CREATE INDEX IF NOT EXISTS idx_deploy_history_environment ON deploy_history(environment);
    CREATE INDEX IF NOT EXISTS idx_deploy_history_status ON deploy_history(status);
    CREATE INDEX IF NOT EXISTS idx_deploy_history_deployed_by ON deploy_history(deployed_by);
    CREATE INDEX IF NOT EXISTS idx_deploy_history_created_at ON deploy_history(created_at DESC);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    
    print("✓ 部署历史表创建成功")


if __name__ == "__main__":
    print("创建部署历史表...")
    create_deploy_history_table()
    print("\n部署历史表创建完成！")

