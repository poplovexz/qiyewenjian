-- 办公管理模块数据库迁移脚本
-- 创建日期: 2024-11-11

-- 1. 创建报销申请表
CREATE TABLE IF NOT EXISTS baoxiao_shenqing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shenqing_bianhao VARCHAR(50) NOT NULL UNIQUE COMMENT '申请编号',
    shenqing_ren_id UUID NOT NULL COMMENT '申请人ID',
    baoxiao_leixing VARCHAR(50) NOT NULL COMMENT '报销类型',
    baoxiao_jine DECIMAL(15, 2) NOT NULL COMMENT '报销金额',
    baoxiao_shijian TIMESTAMP NOT NULL COMMENT '报销事项发生时间',
    baoxiao_yuanyin TEXT NOT NULL COMMENT '报销原因说明',
    fujian_lujing TEXT COMMENT '附件路径',
    shenhe_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daishehe' COMMENT '审核状态',
    shenhe_liucheng_id UUID COMMENT '审核流程ID',
    beizhu TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted CHAR(1) DEFAULT 'N',
    remark TEXT,
    FOREIGN KEY (shenqing_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (shenhe_liucheng_id) REFERENCES shenhe_liucheng(id)
);

CREATE INDEX idx_baoxiao_shenqing_bianhao ON baoxiao_shenqing(shenqing_bianhao);
CREATE INDEX idx_baoxiao_shenqing_ren ON baoxiao_shenqing(shenqing_ren_id);
CREATE INDEX idx_baoxiao_shenhe_zhuangtai ON baoxiao_shenqing(shenhe_zhuangtai);
CREATE INDEX idx_baoxiao_created_at ON baoxiao_shenqing(created_at);

-- 2. 创建请假申请表
CREATE TABLE IF NOT EXISTS qingjia_shenqing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shenqing_bianhao VARCHAR(50) NOT NULL UNIQUE COMMENT '申请编号',
    shenqing_ren_id UUID NOT NULL COMMENT '申请人ID',
    qingjia_leixing VARCHAR(50) NOT NULL COMMENT '请假类型',
    kaishi_shijian TIMESTAMP NOT NULL COMMENT '开始时间',
    jieshu_shijian TIMESTAMP NOT NULL COMMENT '结束时间',
    qingjia_tianshu INTEGER NOT NULL COMMENT '请假天数',
    qingjia_yuanyin TEXT NOT NULL COMMENT '请假原因',
    fujian_lujing TEXT COMMENT '附件路径',
    shenhe_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daishehe' COMMENT '审核状态',
    shenhe_liucheng_id UUID COMMENT '审核流程ID',
    beizhu TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted CHAR(1) DEFAULT 'N',
    remark TEXT,
    FOREIGN KEY (shenqing_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (shenhe_liucheng_id) REFERENCES shenhe_liucheng(id)
);

CREATE INDEX idx_qingjia_shenqing_bianhao ON qingjia_shenqing(shenqing_bianhao);
CREATE INDEX idx_qingjia_shenqing_ren ON qingjia_shenqing(shenqing_ren_id);
CREATE INDEX idx_qingjia_shenhe_zhuangtai ON qingjia_shenqing(shenhe_zhuangtai);
CREATE INDEX idx_qingjia_created_at ON qingjia_shenqing(created_at);

-- 3. 创建对外付款申请表
CREATE TABLE IF NOT EXISTS duiwai_fukuan_shenqing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shenqing_bianhao VARCHAR(50) NOT NULL UNIQUE COMMENT '申请编号',
    shenqing_ren_id UUID NOT NULL COMMENT '申请人ID',
    fukuan_duixiang VARCHAR(200) NOT NULL COMMENT '付款对象',
    fukuan_jine DECIMAL(15, 2) NOT NULL COMMENT '付款金额',
    fukuan_yuanyin TEXT NOT NULL COMMENT '付款原因',
    fukuan_fangshi VARCHAR(50) NOT NULL COMMENT '付款方式',
    shoukuan_zhanghu VARCHAR(200) NOT NULL COMMENT '收款账户信息',
    shoukuan_yinhang VARCHAR(200) COMMENT '收款银行',
    yaoqiu_fukuan_shijian TIMESTAMP COMMENT '要求付款时间',
    fujian_lujing TEXT COMMENT '附件路径',
    shenhe_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daishehe' COMMENT '审核状态',
    shenhe_liucheng_id UUID COMMENT '审核流程ID',
    fukuan_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daifukuan' COMMENT '付款状态',
    shiji_fukuan_shijian TIMESTAMP COMMENT '实际付款时间',
    fukuan_liushui_hao VARCHAR(100) COMMENT '付款流水号',
    beizhu TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted CHAR(1) DEFAULT 'N',
    remark TEXT,
    FOREIGN KEY (shenqing_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (shenhe_liucheng_id) REFERENCES shenhe_liucheng(id)
);

CREATE INDEX idx_fukuan_shenqing_bianhao ON duiwai_fukuan_shenqing(shenqing_bianhao);
CREATE INDEX idx_fukuan_shenqing_ren ON duiwai_fukuan_shenqing(shenqing_ren_id);
CREATE INDEX idx_fukuan_shenhe_zhuangtai ON duiwai_fukuan_shenqing(shenhe_zhuangtai);
CREATE INDEX idx_fukuan_created_at ON duiwai_fukuan_shenqing(created_at);

-- 4. 创建采购申请表
CREATE TABLE IF NOT EXISTS caigou_shenqing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shenqing_bianhao VARCHAR(50) NOT NULL UNIQUE COMMENT '申请编号',
    shenqing_ren_id UUID NOT NULL COMMENT '申请人ID',
    caigou_leixing VARCHAR(50) NOT NULL COMMENT '采购类型',
    caigou_mingcheng VARCHAR(200) NOT NULL COMMENT '采购物品名称',
    caigou_shuliang INTEGER NOT NULL COMMENT '采购数量',
    danwei VARCHAR(20) NOT NULL COMMENT '单位',
    yugu_jine DECIMAL(15, 2) NOT NULL COMMENT '预估金额',
    shiji_jine DECIMAL(15, 2) COMMENT '实际金额',
    caigou_yuanyin TEXT NOT NULL COMMENT '采购原因',
    yaoqiu_shijian TIMESTAMP COMMENT '要求到货时间',
    gongyingshang_xinxi TEXT COMMENT '供应商信息',
    fujian_lujing TEXT COMMENT '附件路径',
    shenhe_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daishehe' COMMENT '审核状态',
    shenhe_liucheng_id UUID COMMENT '审核流程ID',
    caigou_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'daicaigou' COMMENT '采购状态',
    beizhu TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted CHAR(1) DEFAULT 'N',
    remark TEXT,
    FOREIGN KEY (shenqing_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (shenhe_liucheng_id) REFERENCES shenhe_liucheng(id)
);

CREATE INDEX idx_caigou_shenqing_bianhao ON caigou_shenqing(shenqing_bianhao);
CREATE INDEX idx_caigou_shenqing_ren ON caigou_shenqing(shenqing_ren_id);
CREATE INDEX idx_caigou_shenhe_zhuangtai ON caigou_shenqing(shenhe_zhuangtai);
CREATE INDEX idx_caigou_created_at ON caigou_shenqing(created_at);

-- 5. 创建工作交接单表
CREATE TABLE IF NOT EXISTS gongzuo_jiaojie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jiaojie_bianhao VARCHAR(50) NOT NULL UNIQUE COMMENT '交接编号',
    jiaojie_ren_id UUID NOT NULL COMMENT '交接人ID',
    jieshou_ren_id UUID NOT NULL COMMENT '接收人ID',
    jiaojie_yuanyin VARCHAR(200) NOT NULL COMMENT '交接原因',
    jiaojie_shijian TIMESTAMP NOT NULL COMMENT '交接时间',
    jiaojie_neirong JSONB COMMENT '交接内容',
    wenjian_qingdan JSONB COMMENT '文件清单',
    shebei_qingdan JSONB COMMENT '设备清单',
    zhanghu_qingdan JSONB COMMENT '账号清单',
    daiban_shixiang JSONB COMMENT '待办事项',
    fujian_lujing TEXT COMMENT '附件路径',
    jiaojie_zhuangtai VARCHAR(20) NOT NULL DEFAULT 'jiaojiezhong' COMMENT '交接状态',
    queren_ren_id UUID COMMENT '确认人ID',
    queren_shijian TIMESTAMP COMMENT '确认时间',
    beizhu TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted CHAR(1) DEFAULT 'N',
    remark TEXT,
    FOREIGN KEY (jiaojie_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (jieshou_ren_id) REFERENCES yonghu(id),
    FOREIGN KEY (queren_ren_id) REFERENCES yonghu(id)
);

CREATE INDEX idx_jiaojie_bianhao ON gongzuo_jiaojie(jiaojie_bianhao);
CREATE INDEX idx_jiaojie_ren ON gongzuo_jiaojie(jiaojie_ren_id);
CREATE INDEX idx_jieshou_ren ON gongzuo_jiaojie(jieshou_ren_id);
CREATE INDEX idx_jiaojie_zhuangtai ON gongzuo_jiaojie(jiaojie_zhuangtai);
CREATE INDEX idx_jiaojie_created_at ON gongzuo_jiaojie(created_at);

-- 添加表注释
COMMENT ON TABLE baoxiao_shenqing IS '报销申请表';
COMMENT ON TABLE qingjia_shenqing IS '请假申请表';
COMMENT ON TABLE duiwai_fukuan_shenqing IS '对外付款申请表';
COMMENT ON TABLE caigou_shenqing IS '采购申请表';
COMMENT ON TABLE gongzuo_jiaojie IS '工作交接单表';

