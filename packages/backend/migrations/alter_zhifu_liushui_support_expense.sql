-- 修改支付流水表，支持报销支出
-- 执行时间：2025-11-27

-- 1. 修改 zhifu_dingdan_id 和 kehu_id 为可选字段
ALTER TABLE zhifu_liushui 
    ALTER COLUMN zhifu_dingdan_id DROP NOT NULL,
    ALTER COLUMN kehu_id DROP NOT NULL;

-- 2. 添加报销申请关联字段
ALTER TABLE zhifu_liushui
    ADD COLUMN IF NOT EXISTS baoxiao_shenqing_id VARCHAR(36);

COMMENT ON COLUMN zhifu_liushui.baoxiao_shenqing_id IS '报销申请ID（用于报销支出流水）';

-- 3. 添加关联类型字段
ALTER TABLE zhifu_liushui
    ADD COLUMN IF NOT EXISTS guanlian_leixing VARCHAR(20) DEFAULT 'zhifu_dingdan';

COMMENT ON COLUMN zhifu_liushui.guanlian_leixing IS '关联类型：zhifu_dingdan(支付订单)、baoxiao_shenqing(报销申请)';

-- 4. 添加外键约束
ALTER TABLE zhifu_liushui 
    ADD CONSTRAINT fk_zhifu_liushui_baoxiao_shenqing 
    FOREIGN KEY (baoxiao_shenqing_id) 
    REFERENCES baoxiao_shenqing(id) 
    ON DELETE CASCADE;

-- 5. 更新现有数据的关联类型
UPDATE zhifu_liushui 
SET guanlian_leixing = 'zhifu_dingdan' 
WHERE zhifu_dingdan_id IS NOT NULL;

-- 6. 添加注释说明流水类型支持 expense
COMMENT ON COLUMN zhifu_liushui.liushui_leixing IS '流水类型：income(收入)、refund(退款)、fee(手续费)、expense(支出)';

-- 7. 修改实际收入字段注释，改为实际金额
COMMENT ON COLUMN zhifu_liushui.shiji_shouru IS '实际金额（收入为正，支出为负）';

