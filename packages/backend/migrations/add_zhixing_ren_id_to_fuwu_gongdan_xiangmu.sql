-- 添加执行人ID字段到服务工单项目表
-- 创建时间: 2025-11-24
-- 说明: 修复移动端任务统计API 500错误

-- 1. 添加 zhixing_ren_id 字段
ALTER TABLE fuwu_gongdan_xiangmu 
ADD COLUMN IF NOT EXISTS zhixing_ren_id VARCHAR(36);

-- 2. 添加注释
COMMENT ON COLUMN fuwu_gongdan_xiangmu.zhixing_ren_id IS '执行人ID';

-- 3. 添加外键约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fuwu_gongdan_xiangmu_zhixing_ren_id_fkey'
    ) THEN
        ALTER TABLE fuwu_gongdan_xiangmu
        ADD CONSTRAINT fuwu_gongdan_xiangmu_zhixing_ren_id_fkey
        FOREIGN KEY (zhixing_ren_id) REFERENCES yonghu(id);
    END IF;
END $$;

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_fuwu_gongdan_xiangmu_zhixing_ren 
ON fuwu_gongdan_xiangmu(zhixing_ren_id);

-- 5. 验证字段已添加
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fuwu_gongdan_xiangmu' 
        AND column_name = 'zhixing_ren_id'
    ) THEN
        RAISE NOTICE '✓ zhixing_ren_id 字段已成功添加到 fuwu_gongdan_xiangmu 表';
    ELSE
        RAISE EXCEPTION '✗ zhixing_ren_id 字段添加失败';
    END IF;
END $$;

