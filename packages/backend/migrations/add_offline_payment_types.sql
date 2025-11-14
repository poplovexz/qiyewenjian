-- 添加线下支付类型支持（银行汇款、现金）
-- 执行时间：2024-01-XX

-- 1. 添加银行账户相关字段到支付配置表
ALTER TABLE zhifu_peizhi ADD COLUMN IF NOT EXISTS yinhang_mingcheng VARCHAR(100);
ALTER TABLE zhifu_peizhi ADD COLUMN IF NOT EXISTS yinhang_zhanghu_mingcheng VARCHAR(100);
ALTER TABLE zhifu_peizhi ADD COLUMN IF NOT EXISTS yinhang_zhanghu_haoma VARCHAR(100);
ALTER TABLE zhifu_peizhi ADD COLUMN IF NOT EXISTS kaihuhang_mingcheng VARCHAR(200);
ALTER TABLE zhifu_peizhi ADD COLUMN IF NOT EXISTS kaihuhang_lianhanghao VARCHAR(50);

-- 2. 添加字段注释
COMMENT ON COLUMN zhifu_peizhi.yinhang_mingcheng IS '银行名称';
COMMENT ON COLUMN zhifu_peizhi.yinhang_zhanghu_mingcheng IS '银行账户名称';
COMMENT ON COLUMN zhifu_peizhi.yinhang_zhanghu_haoma IS '银行账号';
COMMENT ON COLUMN zhifu_peizhi.kaihuhang_mingcheng IS '开户行名称';
COMMENT ON COLUMN zhifu_peizhi.kaihuhang_lianhanghao IS '开户行联行号';

-- 3. 更新配置类型注释，增加银行汇款和现金类型
COMMENT ON COLUMN zhifu_peizhi.peizhi_leixing IS '配置类型：weixin(微信)、zhifubao(支付宝)、yinhang(银行汇款)、xianjin(现金)';

-- 4. 更新环境字段注释，对于线下支付不需要环境区分
COMMENT ON COLUMN zhifu_peizhi.huanjing IS '环境：shachang(沙箱)、shengchan(生产)、wuxu(无需，用于线下支付)';

