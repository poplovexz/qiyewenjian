-- 修复审核规则配置
-- 将 audit_type 从 "contract" 改为 "hetong_jine_xiuzheng"

-- 更新审核规则的触发条件
UPDATE shenhe_guize
SET chufa_tiaojian = jsonb_set(
    chufa_tiaojian::jsonb,
    '{audit_type}',
    '"hetong_jine_xiuzheng"'::jsonb
)
WHERE id = 'fca756c1-a744-4b38-9961-ac6f2bbe2683'
AND is_deleted = 'N';

-- 验证更新结果
SELECT
    guize_mingcheng,
    guize_leixing,
    (chufa_tiaojian::jsonb)->>'audit_type' as audit_type,
    shi_qiyong
FROM shenhe_guize
WHERE id = 'fca756c1-a744-4b38-9961-ac6f2bbe2683';

