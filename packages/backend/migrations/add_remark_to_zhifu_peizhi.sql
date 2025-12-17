-- 添加 remark 字段到 zhifu_peizhi 表
-- 执行时间: 2025-01-14

-- 添加 remark 字段
ALTER TABLE zhifu_peizhi 
ADD COLUMN IF NOT EXISTS remark VARCHAR(500);

-- 添加字段注释
COMMENT ON COLUMN zhifu_peizhi.remark IS '备注';

