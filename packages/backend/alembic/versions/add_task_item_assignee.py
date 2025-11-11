"""add task item assignee

Revision ID: add_task_item_assignee
Revises: 
Create Date: 2025-11-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_task_item_assignee'
down_revision = None  # 请根据实际情况修改为上一个版本的revision ID
branch_labels = None
depends_on = None


def upgrade():
    """添加任务项执行人字段"""
    
    # 1. 添加 zhixing_ren_id 字段到 fuwu_gongdan_xiangmu 表
    op.add_column(
        'fuwu_gongdan_xiangmu',
        sa.Column('zhixing_ren_id', sa.String(36), nullable=True, comment='执行人ID')
    )
    
    # 2. 添加外键约束
    op.create_foreign_key(
        'fk_fuwu_gongdan_xiangmu_zhixing_ren',
        'fuwu_gongdan_xiangmu',
        'users',
        ['zhixing_ren_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # 3. 添加索引以提高查询性能
    op.create_index(
        'idx_fuwu_gongdan_xiangmu_zhixing_ren',
        'fuwu_gongdan_xiangmu',
        ['zhixing_ren_id']
    )
    
    print("✅ 成功添加任务项执行人字段")


def downgrade():
    """回滚：删除任务项执行人字段"""
    
    # 1. 删除索引
    op.drop_index('idx_fuwu_gongdan_xiangmu_zhixing_ren', 'fuwu_gongdan_xiangmu')
    
    # 2. 删除外键约束
    op.drop_constraint('fk_fuwu_gongdan_xiangmu_zhixing_ren', 'fuwu_gongdan_xiangmu', type_='foreignkey')
    
    # 3. 删除字段
    op.drop_column('fuwu_gongdan_xiangmu', 'zhixing_ren_id')
    
    print("✅ 成功回滚任务项执行人字段")

