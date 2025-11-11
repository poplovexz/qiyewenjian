-- 初始化银行转账支付审批流程

-- 1. 创建审批流程步骤表
CREATE TABLE IF NOT EXISTS shenhe_liucheng_buzou (
    id VARCHAR(36) PRIMARY KEY,
    liucheng_id VARCHAR(36) NOT NULL,
    buzou_mingcheng VARCHAR(100) NOT NULL,
    buzou_shunxu INTEGER NOT NULL,
    shenhe_jiaose_id VARCHAR(36),
    buzou_leixing VARCHAR(50),
    buzou_zhuangtai VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted VARCHAR(1) DEFAULT 'N',
    FOREIGN KEY (liucheng_id) REFERENCES shenhe_liucheng(id)
);

-- 2. 创建角色（业务员、财务）
INSERT INTO jiaose (id, jiaose_mingcheng, jiaose_miaoshu, jiaose_daima, zhuangtai, created_at, updated_at, is_deleted)
VALUES 
    (gen_random_uuid(), '业务员', '负责客户对接和汇款单据上传', 'salesperson', 'active', NOW(), NOW(), 'N')
ON CONFLICT (jiaose_daima) WHERE is_deleted = 'N' DO NOTHING;

INSERT INTO jiaose (id, jiaose_mingcheng, jiaose_miaoshu, jiaose_daima, zhuangtai, created_at, updated_at, is_deleted)
VALUES 
    (gen_random_uuid(), '财务', '负责审核汇款单据和确认到账', 'finance', 'active', NOW(), NOW(), 'N')
ON CONFLICT (jiaose_daima) WHERE is_deleted = 'N' DO NOTHING;

-- 3. 创建测试用户
-- 业务员用户
INSERT INTO yonghu (id, yonghu_ming, mima, xingming, youxiang, shouji, zhuangtai, created_at, updated_at, is_deleted)
VALUES 
    (gen_random_uuid(), 'salesperson1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7K6W', 
     '张业务', 'salesperson1@example.com', '13800138001', 'active', NOW(), NOW(), 'N')
ON CONFLICT (yonghu_ming) WHERE is_deleted = 'N' DO NOTHING;

-- 财务用户
INSERT INTO yonghu (id, yonghu_ming, mima, xingming, youxiang, shouji, zhuangtai, created_at, updated_at, is_deleted)
VALUES 
    (gen_random_uuid(), 'finance1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Hs7K6W', 
     '李财务', 'finance1@example.com', '13800138002', 'active', NOW(), NOW(), 'N')
ON CONFLICT (yonghu_ming) WHERE is_deleted = 'N' DO NOTHING;

-- 4. 分配角色给用户
-- 业务员角色
INSERT INTO yonghu_jiaose (id, yonghu_id, jiaose_id, created_at, updated_at, is_deleted)
SELECT gen_random_uuid(), y.id, j.id, NOW(), NOW(), 'N'
FROM yonghu y, jiaose j
WHERE y.yonghu_ming = 'salesperson1' AND y.is_deleted = 'N'
  AND j.jiaose_daima = 'salesperson' AND j.is_deleted = 'N'
  AND NOT EXISTS (
      SELECT 1 FROM yonghu_jiaose yj 
      WHERE yj.yonghu_id = y.id AND yj.jiaose_id = j.id AND yj.is_deleted = 'N'
  );

-- 财务角色
INSERT INTO yonghu_jiaose (id, yonghu_id, jiaose_id, created_at, updated_at, is_deleted)
SELECT gen_random_uuid(), y.id, j.id, NOW(), NOW(), 'N'
FROM yonghu y, jiaose j
WHERE y.yonghu_ming = 'finance1' AND y.is_deleted = 'N'
  AND j.jiaose_daima = 'finance' AND j.is_deleted = 'N'
  AND NOT EXISTS (
      SELECT 1 FROM yonghu_jiaose yj 
      WHERE yj.yonghu_id = y.id AND yj.jiaose_id = j.id AND yj.is_deleted = 'N'
  );

-- 5. 创建审批流程
INSERT INTO shenhe_liucheng (id, liucheng_mingcheng, liucheng_daima, liucheng_miaoshu, shiyong_fanwei, liucheng_zhuangtai, created_at, updated_at, is_deleted)
VALUES 
    (gen_random_uuid(), '银行转账支付审批', 'bank_payment_approval', 
     '客户选择银行转账后，业务员上传汇款单据，财务审核确认', 'payment', 'active', NOW(), NOW(), 'N')
ON CONFLICT DO NOTHING;

-- 6. 创建审批步骤
-- 步骤1: 业务员上传汇款单据
INSERT INTO shenhe_liucheng_buzou (id, liucheng_id, buzou_mingcheng, buzou_shunxu, shenhe_jiaose_id, buzou_leixing, buzou_zhuangtai, created_at, updated_at, is_deleted)
SELECT gen_random_uuid(), lc.id, '业务员上传汇款单据', 1, j.id, 'upload', 'active', NOW(), NOW(), 'N'
FROM shenhe_liucheng lc, jiaose j
WHERE lc.liucheng_daima = 'bank_payment_approval' AND lc.is_deleted = 'N'
  AND j.jiaose_daima = 'salesperson' AND j.is_deleted = 'N'
  AND NOT EXISTS (
      SELECT 1 FROM shenhe_liucheng_buzou b 
      WHERE b.liucheng_id = lc.id AND b.buzou_shunxu = 1 AND b.is_deleted = 'N'
  );

-- 步骤2: 财务审核确认
INSERT INTO shenhe_liucheng_buzou (id, liucheng_id, buzou_mingcheng, buzou_shunxu, shenhe_jiaose_id, buzou_leixing, buzou_zhuangtai, created_at, updated_at, is_deleted)
SELECT gen_random_uuid(), lc.id, '财务审核确认', 2, j.id, 'approval', 'active', NOW(), NOW(), 'N'
FROM shenhe_liucheng lc, jiaose j
WHERE lc.liucheng_daima = 'bank_payment_approval' AND lc.is_deleted = 'N'
  AND j.jiaose_daima = 'finance' AND j.is_deleted = 'N'
  AND NOT EXISTS (
      SELECT 1 FROM shenhe_liucheng_buzou b 
      WHERE b.liucheng_id = lc.id AND b.buzou_shunxu = 2 AND b.is_deleted = 'N'
  );

-- 查询结果
SELECT '=== 角色 ===' AS info;
SELECT jiaose_mingcheng, jiaose_daima FROM jiaose WHERE is_deleted = 'N' AND jiaose_daima IN ('salesperson', 'finance');

SELECT '=== 用户 ===' AS info;
SELECT xingming, yonghu_ming FROM yonghu WHERE is_deleted = 'N' AND yonghu_ming IN ('salesperson1', 'finance1');

SELECT '=== 审批流程 ===' AS info;
SELECT liucheng_mingcheng, liucheng_daima FROM shenhe_liucheng WHERE liucheng_daima = 'bank_payment_approval' AND is_deleted = 'N';

SELECT '=== 审批步骤 ===' AS info;
SELECT b.buzou_mingcheng, b.buzou_shunxu, j.jiaose_mingcheng
FROM shenhe_liucheng_buzou b
JOIN shenhe_liucheng lc ON b.liucheng_id = lc.id
LEFT JOIN jiaose j ON b.shenhe_jiaose_id = j.id
WHERE lc.liucheng_daima = 'bank_payment_approval' AND b.is_deleted = 'N'
ORDER BY b.buzou_shunxu;

