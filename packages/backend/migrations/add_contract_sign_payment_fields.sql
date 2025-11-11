-- 添加合同签署和支付相关字段
-- 执行时间：2025-10-13

-- 添加客户签署链接相关字段
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS sign_token VARCHAR(100) UNIQUE;
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS sign_token_expires_at TIMESTAMP;
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS customer_signature TEXT;
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS signed_at TIMESTAMP;

-- 添加支付相关字段
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP;
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS payment_amount VARCHAR(20);
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE hetong ADD COLUMN IF NOT EXISTS payment_transaction_id VARCHAR(100);

-- 添加列注释
COMMENT ON COLUMN hetong.sign_token IS '签署链接的唯一令牌';
COMMENT ON COLUMN hetong.sign_token_expires_at IS '签署链接过期时间';
COMMENT ON COLUMN hetong.customer_signature IS '客户签名图片（base64）';
COMMENT ON COLUMN hetong.signed_at IS '客户签署时间';
COMMENT ON COLUMN hetong.payment_status IS '支付状态：pending-待支付，paid-已支付，failed-支付失败，refunded-已退款';
COMMENT ON COLUMN hetong.paid_at IS '支付时间';
COMMENT ON COLUMN hetong.payment_amount IS '支付金额';
COMMENT ON COLUMN hetong.payment_method IS '支付方式：wechat-微信支付，alipay-支付宝，bank-银行转账';
COMMENT ON COLUMN hetong.payment_transaction_id IS '支付交易号';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_hetong_sign_token ON hetong(sign_token);
CREATE INDEX IF NOT EXISTS idx_hetong_payment_status ON hetong(payment_status);
CREATE INDEX IF NOT EXISTS idx_hetong_signed_at ON hetong(signed_at);
CREATE INDEX IF NOT EXISTS idx_hetong_paid_at ON hetong(paid_at);

