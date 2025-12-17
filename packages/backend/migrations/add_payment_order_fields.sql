-- 为支付订单表添加新字段
-- 支持第三方支付集成

-- 添加支付配置ID
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_peizhi_id VARCHAR(36);
ALTER TABLE zhifu_dingdan ADD CONSTRAINT fk_zhifu_dingdan_peizhi 
    FOREIGN KEY (zhifu_peizhi_id) REFERENCES zhifu_peizhi(id);

-- 添加支付平台字段
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_pingtai VARCHAR(20);

-- 添加支付方式明细字段
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_fangshi_mingxi VARCHAR(50);

-- 添加二维码内容字段
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS erweima_neirong TEXT;

-- 添加退款金额字段
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_jine NUMERIC(10, 2) DEFAULT 0.00;

-- 添加退款次数字段
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_cishu VARCHAR(10) DEFAULT '0';

-- 添加字段注释
COMMENT ON COLUMN zhifu_dingdan.zhifu_peizhi_id IS '支付配置ID';
COMMENT ON COLUMN zhifu_dingdan.zhifu_pingtai IS '支付平台：weixin(微信)、zhifubao(支付宝)';
COMMENT ON COLUMN zhifu_dingdan.zhifu_fangshi_mingxi IS '支付方式明细：jsapi(公众号)、app(APP)、h5(H5)、native(扫码)、page(网页)、wap(手机网页)';
COMMENT ON COLUMN zhifu_dingdan.erweima_neirong IS '支付二维码内容（code_url或支付链接）';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_jine IS '退款金额';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_cishu IS '退款次数';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_peizhi ON zhifu_dingdan(zhifu_peizhi_id);
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_pingtai ON zhifu_dingdan(zhifu_pingtai);
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_fangshi ON zhifu_dingdan(zhifu_fangshi_mingxi);

