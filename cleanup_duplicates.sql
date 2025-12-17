-- 清理重复数据脚本

-- 1. 查看当前角色
SELECT '=== 当前角色 ===' AS info;
SELECT id, jiaose_ming, jiaose_bianma, zhuangtai, created_at 
FROM jiaose 
WHERE is_deleted = 'N' 
ORDER BY created_at;

-- 2. 查看当前用户
SELECT '=== 当前用户 ===' AS info;
SELECT id, xingming, yonghu_ming, zhuangtai, created_at 
FROM yonghu 
WHERE is_deleted = 'N' 
ORDER BY created_at;

-- 3. 查看用户角色关联
SELECT '=== 用户角色关联 ===' AS info;
SELECT y.xingming, y.yonghu_ming, j.jiaose_ming, yj.created_at
FROM yonghu y
JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
JOIN jiaose j ON yj.jiaose_id = j.id
WHERE y.is_deleted = 'N' AND yj.is_deleted = 'N' AND j.is_deleted = 'N'
ORDER BY yj.created_at;

-- 4. 清理重复的角色（如果有）
-- 保留最新的，删除旧的
-- 注意：这里只是示例，实际执行前请先查看数据

-- 示例：如果有重复的"业务员"角色
-- WITH duplicate_roles AS (
--     SELECT id, jiaose_bianma, created_at,
--            ROW_NUMBER() OVER (PARTITION BY jiaose_bianma ORDER BY created_at DESC) as rn
--     FROM jiaose
--     WHERE is_deleted = 'N' AND jiaose_bianma = 'salesperson'
-- )
-- UPDATE jiaose 
-- SET is_deleted = 'Y', updated_at = NOW()
-- WHERE id IN (SELECT id FROM duplicate_roles WHERE rn > 1);

-- 5. 清理重复的用户（如果有）
-- 保留最新的，删除旧的

-- 示例：如果有重复的用户
-- WITH duplicate_users AS (
--     SELECT id, yonghu_ming, created_at,
--            ROW_NUMBER() OVER (PARTITION BY yonghu_ming ORDER BY created_at DESC) as rn
--     FROM yonghu
--     WHERE is_deleted = 'N' AND yonghu_ming IN ('salesperson1', 'finance1')
-- )
-- UPDATE yonghu 
-- SET is_deleted = 'Y', updated_at = NOW()
-- WHERE id IN (SELECT id FROM duplicate_users WHERE rn > 1);

-- 6. 清理重复的用户角色关联（如果有）
-- WITH duplicate_user_roles AS (
--     SELECT id, yonghu_id, jiaose_id, created_at,
--            ROW_NUMBER() OVER (PARTITION BY yonghu_id, jiaose_id ORDER BY created_at DESC) as rn
--     FROM yonghu_jiaose
--     WHERE is_deleted = 'N'
-- )
-- UPDATE yonghu_jiaose 
-- SET is_deleted = 'Y', updated_at = NOW()
-- WHERE id IN (SELECT id FROM duplicate_user_roles WHERE rn > 1);

-- 7. 最终检查
SELECT '=== 清理后的角色 ===' AS info;
SELECT jiaose_ming, jiaose_bianma, zhuangtai 
FROM jiaose 
WHERE is_deleted = 'N' 
ORDER BY jiaose_bianma;

SELECT '=== 清理后的用户 ===' AS info;
SELECT xingming, yonghu_ming, zhuangtai 
FROM yonghu 
WHERE is_deleted = 'N' 
ORDER BY yonghu_ming;

SELECT '=== 清理后的用户角色关联 ===' AS info;
SELECT y.xingming, y.yonghu_ming, j.jiaose_ming
FROM yonghu y
JOIN yonghu_jiaose yj ON y.id = yj.yonghu_id
JOIN jiaose j ON yj.jiaose_id = j.id
WHERE y.is_deleted = 'N' AND yj.is_deleted = 'N' AND j.is_deleted = 'N'
ORDER BY y.yonghu_ming;

