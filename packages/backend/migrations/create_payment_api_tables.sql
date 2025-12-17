-- ============================================
-- 支付API接入相关表
-- 创建时间: 2025-11-13
-- 说明: 用于微信支付和支付宝商户收款API接入
-- ============================================

-- 1. 支付配置表 (zhifu_peizhi)
-- 用于存储微信和支付宝的商户配置信息
CREATE TABLE IF NOT EXISTS zhifu_peizhi (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- 基本信息
    peizhi_mingcheng VARCHAR(100) NOT NULL,
    peizhi_leixing VARCHAR(20) NOT NULL,
    zhuangtai VARCHAR(20) DEFAULT 'qiyong' NOT NULL,
    shi_moren VARCHAR(1) DEFAULT 'N' NOT NULL,

    -- 微信支付配置
    weixin_appid VARCHAR(100),
    weixin_shanghu_hao VARCHAR(100),
    weixin_api_v3_miyao TEXT,
    weixin_shanghu_siyao TEXT,
    weixin_zhengshu_xuliehao VARCHAR(100),
    weixin_zhengshu_neirong TEXT,

    -- 支付宝配置
    zhifubao_appid VARCHAR(100),
    zhifubao_shanghu_siyao TEXT,
    zhifubao_zhifubao_gongyao TEXT,
    zhifubao_yingyong_gongyao TEXT,

    -- 通用配置
    tongzhi_url VARCHAR(500),
    tuikuan_tongzhi_url VARCHAR(500),
    huanjing VARCHAR(20) DEFAULT 'shengchan',

    -- 备注信息
    beizhu TEXT,

    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    is_deleted VARCHAR(1) DEFAULT 'N'
);

COMMENT ON TABLE zhifu_peizhi IS '支付配置表';
COMMENT ON COLUMN zhifu_peizhi.peizhi_leixing IS '配置类型：weixin(微信支付)、zhifubao(支付宝)';
COMMENT ON COLUMN zhifu_peizhi.zhuangtai IS '状态：qiyong(启用)、tingyong(停用)';
COMMENT ON COLUMN zhifu_peizhi.huanjing IS '环境：shachang(沙箱)、shengchan(生产)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_zhifu_peizhi_leixing ON zhifu_peizhi(peizhi_leixing);
CREATE INDEX IF NOT EXISTS idx_zhifu_peizhi_zhuangtai ON zhifu_peizhi(zhuangtai);
CREATE INDEX IF NOT EXISTS idx_zhifu_peizhi_moren ON zhifu_peizhi(shi_moren);


-- 2. 支付回调日志表 (zhifu_huidiao_rizhi)
-- 用于记录所有支付回调请求
CREATE TABLE IF NOT EXISTS zhifu_huidiao_rizhi (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- 关联信息
    zhifu_peizhi_id VARCHAR(36),
    zhifu_dingdan_id VARCHAR(36),

    -- 回调信息
    huidiao_leixing VARCHAR(20) NOT NULL,
    zhifu_pingtai VARCHAR(20) NOT NULL,

    -- 请求数据
    qingqiu_fangfa VARCHAR(10),
    qingqiu_url VARCHAR(500),
    qingqiu_tou TEXT,
    qingqiu_zhuti TEXT,
    qingqiu_shijian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 签名验证
    qianming VARCHAR(500),
    qianming_yanzheng VARCHAR(20) DEFAULT 'daichuli',
    qianming_cuowu TEXT,

    -- 处理结果
    chuli_zhuangtai VARCHAR(20) DEFAULT 'daichuli',
    chuli_jieguo TEXT,
    chuli_cuowu TEXT,
    chuli_shijian TIMESTAMP,

    -- 响应数据
    xiangying_zhuangtai INT,
    xiangying_zhuti TEXT,

    -- 业务数据
    disanfang_dingdan_hao VARCHAR(100),
    disanfang_liushui_hao VARCHAR(100),
    jiaoy_jine NUMERIC(12, 2),
    jiaoy_zhuangtai VARCHAR(20),

    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted VARCHAR(1) DEFAULT 'N'
);

COMMENT ON TABLE zhifu_huidiao_rizhi IS '支付回调日志表';
COMMENT ON COLUMN zhifu_huidiao_rizhi.huidiao_leixing IS '回调类型：zhifu(支付)、tuikuan(退款)';
COMMENT ON COLUMN zhifu_huidiao_rizhi.zhifu_pingtai IS '支付平台：weixin(微信)、zhifubao(支付宝)';
COMMENT ON COLUMN zhifu_huidiao_rizhi.qianming_yanzheng IS '签名验证：chenggong(成功)、shibai(失败)、daichuli(待处理)';
COMMENT ON COLUMN zhifu_huidiao_rizhi.chuli_zhuangtai IS '处理状态：chenggong(成功)、shibai(失败)、daichuli(待处理)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_peizhi ON zhifu_huidiao_rizhi(zhifu_peizhi_id);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_dingdan ON zhifu_huidiao_rizhi(zhifu_dingdan_id);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_leixing ON zhifu_huidiao_rizhi(huidiao_leixing);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_pingtai ON zhifu_huidiao_rizhi(zhifu_pingtai);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_yanzheng ON zhifu_huidiao_rizhi(qianming_yanzheng);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_zhuangtai ON zhifu_huidiao_rizhi(chuli_zhuangtai);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_disanfang ON zhifu_huidiao_rizhi(disanfang_dingdan_hao);
CREATE INDEX IF NOT EXISTS idx_huidiao_rizhi_shijian ON zhifu_huidiao_rizhi(qingqiu_shijian);


-- 3. 退款记录表 (zhifu_tuikuan)
-- 用于管理退款流程
CREATE TABLE IF NOT EXISTS zhifu_tuikuan (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- 关联信息
    zhifu_dingdan_id VARCHAR(36) NOT NULL,
    zhifu_peizhi_id VARCHAR(36),

    -- 退款基本信息
    tuikuan_danhao VARCHAR(50) UNIQUE NOT NULL,
    yuanshi_dingdan_hao VARCHAR(100) NOT NULL,
    disanfang_tuikuan_hao VARCHAR(100),

    -- 金额信息
    yuanshi_jine NUMERIC(12, 2) NOT NULL,
    tuikuan_jine NUMERIC(12, 2) NOT NULL,

    -- 退款信息
    tuikuan_yuanyin TEXT,
    tuikuan_zhuangtai VARCHAR(20) DEFAULT 'chuli_zhong',
    tuikuan_pingtai VARCHAR(20) NOT NULL,

    -- 时间信息
    shenqing_shijian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chenggong_shijian TIMESTAMP,
    daozhang_shijian TIMESTAMP,

    -- 处理信息
    chuli_jieguo TEXT,
    cuowu_xinxi TEXT,
    cuowu_daima VARCHAR(50),

    -- 备注信息
    beizhu TEXT,

    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    is_deleted VARCHAR(1) DEFAULT 'N',

    FOREIGN KEY (zhifu_dingdan_id) REFERENCES zhifu_dingdan(id) ON DELETE CASCADE
);

COMMENT ON TABLE zhifu_tuikuan IS '退款记录表';
COMMENT ON COLUMN zhifu_tuikuan.tuikuan_zhuangtai IS '退款状态：chuli_zhong(处理中)、chenggong(成功)、shibai(失败)、yiguanbi(已关闭)';
COMMENT ON COLUMN zhifu_tuikuan.tuikuan_pingtai IS '退款平台：weixin(微信)、zhifubao(支付宝)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tuikuan_dingdan ON zhifu_tuikuan(zhifu_dingdan_id);
CREATE INDEX IF NOT EXISTS idx_tuikuan_peizhi ON zhifu_tuikuan(zhifu_peizhi_id);
CREATE INDEX IF NOT EXISTS idx_tuikuan_zhuangtai ON zhifu_tuikuan(tuikuan_zhuangtai);
CREATE INDEX IF NOT EXISTS idx_tuikuan_pingtai ON zhifu_tuikuan(tuikuan_pingtai);
CREATE INDEX IF NOT EXISTS idx_tuikuan_disanfang ON zhifu_tuikuan(disanfang_tuikuan_hao);
CREATE INDEX IF NOT EXISTS idx_tuikuan_shijian ON zhifu_tuikuan(shenqing_shijian);


-- 4. 扩展支付订单表 (zhifu_dingdan)
-- 添加新字段支持第三方支付
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_peizhi_id VARCHAR(36);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS disanfang_dingdan_hao VARCHAR(100);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS disanfang_liushui_hao VARCHAR(100);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_shijian TIMESTAMP;
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_jine NUMERIC(12, 2) DEFAULT 0.00;
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS tuikuan_cishu INT DEFAULT 0;
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_pingtai VARCHAR(20);
ALTER TABLE zhifu_dingdan ADD COLUMN IF NOT EXISTS zhifu_fangshi_mingxi VARCHAR(50);

-- 添加外键约束
ALTER TABLE zhifu_dingdan ADD CONSTRAINT fk_zhifu_dingdan_peizhi 
    FOREIGN KEY (zhifu_peizhi_id) REFERENCES zhifu_peizhi(id) ON DELETE SET NULL;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_peizhi ON zhifu_dingdan(zhifu_peizhi_id);
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_disanfang ON zhifu_dingdan(disanfang_dingdan_hao);
CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_pingtai ON zhifu_dingdan(zhifu_pingtai);

-- 添加注释
COMMENT ON COLUMN zhifu_dingdan.zhifu_peizhi_id IS '支付配置ID';
COMMENT ON COLUMN zhifu_dingdan.disanfang_dingdan_hao IS '第三方订单号';
COMMENT ON COLUMN zhifu_dingdan.disanfang_liushui_hao IS '第三方流水号';
COMMENT ON COLUMN zhifu_dingdan.zhifu_shijian IS '支付时间';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_jine IS '退款金额';
COMMENT ON COLUMN zhifu_dingdan.tuikuan_cishu IS '退款次数';
COMMENT ON COLUMN zhifu_dingdan.zhifu_pingtai IS '支付平台：weixin(微信)、zhifubao(支付宝)';
COMMENT ON COLUMN zhifu_dingdan.zhifu_fangshi_mingxi IS '支付方式明细：jsapi、app、h5、native等';

