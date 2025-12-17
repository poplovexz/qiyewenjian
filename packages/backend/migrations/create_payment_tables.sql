-- 创建合同支付表
CREATE TABLE IF NOT EXISTS hetong_zhifu (
    id VARCHAR(36) PRIMARY KEY,
    hetong_id VARCHAR(36) NOT NULL,
    zhifu_fangshi VARCHAR(50) NOT NULL,
    zhifu_jine NUMERIC(12, 2) NOT NULL,
    zhifu_zhuangtai VARCHAR(20) DEFAULT 'daizhi' NOT NULL,
    zhifu_liushui_hao VARCHAR(100),
    zhifu_shijian TIMESTAMP,
    disanfang_dingdan_hao VARCHAR(100),
    disanfang_liushui_hao VARCHAR(100),
    zhifu_beizhu TEXT,
    tuikuan_jine NUMERIC(12, 2) DEFAULT 0.00,
    tuikuan_shijian TIMESTAMP,
    tuikuan_yuanyin TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    is_deleted VARCHAR(1) DEFAULT 'N',
    FOREIGN KEY (hetong_id) REFERENCES hetong(id)
);

COMMENT ON TABLE hetong_zhifu IS '合同支付表';
COMMENT ON COLUMN hetong_zhifu.zhifu_fangshi IS '支付方式：zhifubao(支付宝)、weixin(微信)、yinhang_zhuanzhang(银行转账)';
COMMENT ON COLUMN hetong_zhifu.zhifu_jine IS '支付金额';
COMMENT ON COLUMN hetong_zhifu.zhifu_zhuangtai IS '支付状态：daizhi(待支付)、yizhi(已支付)、shibai(支付失败)、tuikuan(已退款)';

-- 创建银行汇款单据表
CREATE TABLE IF NOT EXISTS yinhang_huikuan_danju (
    id VARCHAR(36) PRIMARY KEY,
    hetong_zhifu_id VARCHAR(36) NOT NULL,
    danju_bianhao VARCHAR(50) NOT NULL UNIQUE,
    danju_lujing VARCHAR(500) NOT NULL,
    danju_mingcheng VARCHAR(200),
    huikuan_jine NUMERIC(12, 2) NOT NULL,
    huikuan_riqi TIMESTAMP NOT NULL,
    huikuan_ren VARCHAR(100) NOT NULL,
    huikuan_yinhang VARCHAR(200),
    huikuan_zhanghu VARCHAR(50),
    shangchuan_ren_id VARCHAR(36) NOT NULL,
    shangchuan_shijian TIMESTAMP,
    shenhe_zhuangtai VARCHAR(20) DEFAULT 'daishehe' NOT NULL,
    shenhe_ren_id VARCHAR(36),
    shenhe_shijian TIMESTAMP,
    shenhe_yijian TEXT,
    beizhu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    is_deleted VARCHAR(1) DEFAULT 'N',
    FOREIGN KEY (hetong_zhifu_id) REFERENCES hetong_zhifu(id)
);

COMMENT ON TABLE yinhang_huikuan_danju IS '银行汇款单据表';
COMMENT ON COLUMN yinhang_huikuan_danju.shenhe_zhuangtai IS '审核状态：daishehe(待审核)、tongguo(通过)、jujue(拒绝)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_hetong_zhifu_hetong_id ON hetong_zhifu(hetong_id);
CREATE INDEX IF NOT EXISTS idx_hetong_zhifu_zhuangtai ON hetong_zhifu(zhifu_zhuangtai);
CREATE INDEX IF NOT EXISTS idx_huikuan_danju_zhifu_id ON yinhang_huikuan_danju(hetong_zhifu_id);
CREATE INDEX IF NOT EXISTS idx_huikuan_danju_shenhe_zhuangtai ON yinhang_huikuan_danju(shenhe_zhuangtai);
CREATE INDEX IF NOT EXISTS idx_huikuan_danju_shangchuan_ren ON yinhang_huikuan_danju(shangchuan_ren_id);
CREATE INDEX IF NOT EXISTS idx_huikuan_danju_shenhe_ren ON yinhang_huikuan_danju(shenhe_ren_id);

