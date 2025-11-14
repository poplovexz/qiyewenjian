-- 为 zhifu_tuikuan 表添加 remark 字段
-- 日期: 2025-01-13

-- 添加 remark 字段
ALTER TABLE zhifu_tuikuan
ADD COLUMN IF NOT EXISTS remark VARCHAR(500);

-- 添加字段注释
COMMENT ON COLUMN zhifu_tuikuan.remark IS '备注';

-- 验证字段是否添加成功
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'zhifu_tuikuan' AND column_name = 'remark';

