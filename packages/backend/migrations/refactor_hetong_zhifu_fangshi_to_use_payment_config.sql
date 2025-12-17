-- 重构合同支付方式表，改为关联支付配置而非保存个人收款信息
-- 执行时间: 2025-01-14

-- 1. 添加支付配置ID字段
ALTER TABLE hetong_zhifu_fangshi 
ADD COLUMN IF NOT EXISTS zhifu_peizhi_id VARCHAR(36);

-- 2. 添加外键约束
ALTER TABLE hetong_zhifu_fangshi
ADD CONSTRAINT fk_hetong_zhifu_fangshi_peizhi
FOREIGN KEY (zhifu_peizhi_id) REFERENCES zhifu_peizhi(id) ON DELETE CASCADE;

-- 3. 添加字段注释
COMMENT ON COLUMN hetong_zhifu_fangshi.zhifu_peizhi_id IS '支付配置ID - 关联到支付配置管理';

-- 4. 删除不再需要的个人收款相关字段
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS zhifu_leixing;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS zhanghu_mingcheng;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS zhanghu_haoma;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS kaihuhang_mingcheng;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS kaihuhang_dizhi;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS lianhanghao;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS weixin_haoma;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS weixin_shoukuan_ming;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS zhifubao_haoma;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS zhifubao_shoukuan_ming;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS erweima_lujing;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS danbi_xiange;
ALTER TABLE hetong_zhifu_fangshi DROP COLUMN IF EXISTS riqi_xiange;

-- 5. 更新表注释
COMMENT ON TABLE hetong_zhifu_fangshi IS '合同支付方式表 - 关联乙方主体和支付配置';

