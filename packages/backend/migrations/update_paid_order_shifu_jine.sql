-- 更新已支付订单的实付金额
-- 将所有已支付但实付金额为0的订单，设置实付金额等于应付金额

UPDATE zhifu_dingdan 
SET shifu_jine = yingfu_jine,
    updated_at = NOW()
WHERE zhifu_zhuangtai = 'paid' 
  AND shifu_jine = 0 
  AND is_deleted = 'N';

