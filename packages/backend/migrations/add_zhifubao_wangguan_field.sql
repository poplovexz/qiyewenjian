-- 添加支付宝网关字段到支付配置表
-- 执行时间: 2024-11-25

-- 添加支付宝网关字段
ALTER TABLE zhifu_peizhi 
ADD COLUMN IF NOT EXISTS zhifubao_wangguan VARCHAR(500);

COMMENT ON COLUMN zhifu_peizhi.zhifubao_wangguan IS '支付宝网关地址';

-- 为现有的支付宝配置设置默认网关
UPDATE zhifu_peizhi 
SET zhifubao_wangguan = CASE 
    WHEN huanjing = 'shachang' THEN 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
    WHEN huanjing = 'shengchan' THEN 'https://openapi.alipay.com/gateway.do'
    ELSE NULL
END
WHERE peizhi_leixing = 'zhifubao' 
  AND zhifubao_wangguan IS NULL;

