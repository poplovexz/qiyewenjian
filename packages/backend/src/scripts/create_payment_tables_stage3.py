#!/usr/bin/env python3
"""
阶段3：创建支付管理相关数据表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_payment_tables():
    """创建支付管理相关表"""

    # 支付订单表
    zhifu_dingdan_sql = """
    CREATE TABLE IF NOT EXISTS zhifu_dingdan (
        id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        hetong_id VARCHAR(36) NOT NULL,
        kehu_id VARCHAR(36) NOT NULL,
        yifang_zhuti_id VARCHAR(36),
        zhifu_fangshi_id VARCHAR(36),
        dingdan_bianhao VARCHAR(50) UNIQUE NOT NULL,
        dingdan_mingcheng VARCHAR(200) NOT NULL,
        dingdan_miaoshu TEXT,
        dingdan_jine DECIMAL(10,2) NOT NULL,
        yingfu_jine DECIMAL(10,2) NOT NULL,
        shifu_jine DECIMAL(10,2) DEFAULT 0.00,
        zhifu_leixing VARCHAR(50) NOT NULL,
        zhifu_zhuangtai VARCHAR(20) DEFAULT 'pending' NOT NULL,
        disanfang_dingdan_hao VARCHAR(100),
        disanfang_liushui_hao VARCHAR(100),
        erweima_lujing VARCHAR(500),
        chuangjian_shijian TIMESTAMP NOT NULL,
        zhifu_shijian TIMESTAMP,
        guoqi_shijian TIMESTAMP,
        huidiao_zhuangtai VARCHAR(20) DEFAULT 'pending' NOT NULL,
        huidiao_shijian TIMESTAMP,
        huidiao_xinxi TEXT,
        beizhu TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36) NOT NULL,
        updated_by VARCHAR(36),
        is_deleted CHAR(1) DEFAULT 'N'
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_hetong_id ON zhifu_dingdan(hetong_id);
    CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_kehu_id ON zhifu_dingdan(kehu_id);
    CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_bianhao ON zhifu_dingdan(dingdan_bianhao);
    CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_zhuangtai ON zhifu_dingdan(zhifu_zhuangtai);
    CREATE INDEX IF NOT EXISTS idx_zhifu_dingdan_chuangjian_shijian ON zhifu_dingdan(chuangjian_shijian);

    -- 添加注释
    COMMENT ON TABLE zhifu_dingdan IS '支付订单表';
    COMMENT ON COLUMN zhifu_dingdan.hetong_id IS '合同ID';
    COMMENT ON COLUMN zhifu_dingdan.kehu_id IS '客户ID';
    COMMENT ON COLUMN zhifu_dingdan.yifang_zhuti_id IS '乙方主体ID';
    COMMENT ON COLUMN zhifu_dingdan.zhifu_fangshi_id IS '支付方式ID';
    COMMENT ON COLUMN zhifu_dingdan.dingdan_bianhao IS '支付订单编号';
    COMMENT ON COLUMN zhifu_dingdan.dingdan_mingcheng IS '订单名称';
    COMMENT ON COLUMN zhifu_dingdan.dingdan_miaoshu IS '订单描述';
    COMMENT ON COLUMN zhifu_dingdan.dingdan_jine IS '订单金额';
    COMMENT ON COLUMN zhifu_dingdan.yingfu_jine IS '应付金额';
    COMMENT ON COLUMN zhifu_dingdan.shifu_jine IS '实付金额';
    COMMENT ON COLUMN zhifu_dingdan.zhifu_leixing IS '支付类型';
    COMMENT ON COLUMN zhifu_dingdan.zhifu_zhuangtai IS '支付状态';
    COMMENT ON COLUMN zhifu_dingdan.disanfang_dingdan_hao IS '第三方支付订单号';
    COMMENT ON COLUMN zhifu_dingdan.disanfang_liushui_hao IS '第三方支付流水号';
    COMMENT ON COLUMN zhifu_dingdan.erweima_lujing IS '支付二维码图片路径';
    COMMENT ON COLUMN zhifu_dingdan.chuangjian_shijian IS '创建时间';
    COMMENT ON COLUMN zhifu_dingdan.zhifu_shijian IS '支付时间';
    COMMENT ON COLUMN zhifu_dingdan.guoqi_shijian IS '过期时间';
    COMMENT ON COLUMN zhifu_dingdan.huidiao_zhuangtai IS '回调状态';
    COMMENT ON COLUMN zhifu_dingdan.huidiao_shijian IS '回调时间';
    COMMENT ON COLUMN zhifu_dingdan.huidiao_xinxi IS '回调信息';
    COMMENT ON COLUMN zhifu_dingdan.beizhu IS '备注';
    COMMENT ON COLUMN zhifu_dingdan.created_at IS '创建时间';
    COMMENT ON COLUMN zhifu_dingdan.updated_at IS '更新时间';
    COMMENT ON COLUMN zhifu_dingdan.created_by IS '创建人ID';
    COMMENT ON COLUMN zhifu_dingdan.updated_by IS '更新人ID';
    COMMENT ON COLUMN zhifu_dingdan.is_deleted IS '是否删除：Y-是，N-否';
    """
    
    # 支付流水表
    zhifu_liushui_sql = """
    CREATE TABLE IF NOT EXISTS zhifu_liushui (
        id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        zhifu_dingdan_id VARCHAR(36) NOT NULL,
        kehu_id VARCHAR(36) NOT NULL,
        liushui_bianhao VARCHAR(50) UNIQUE NOT NULL,
        liushui_leixing VARCHAR(20) NOT NULL,
        jiaoyijine DECIMAL(10,2) NOT NULL,
        shouxufei DECIMAL(10,2) DEFAULT 0.00,
        shiji_shouru DECIMAL(10,2) NOT NULL,
        zhifu_fangshi VARCHAR(50) NOT NULL,
        zhifu_zhanghu VARCHAR(100),
        disanfang_liushui_hao VARCHAR(100),
        disanfang_dingdan_hao VARCHAR(100),
        jiaoyishijian TIMESTAMP NOT NULL,
        daozhangjian TIMESTAMP,
        liushui_zhuangtai VARCHAR(20) DEFAULT 'success' NOT NULL,
        duizhang_zhuangtai VARCHAR(20) DEFAULT 'pending' NOT NULL,
        yinhang_mingcheng VARCHAR(100),
        yinhang_zhanghu VARCHAR(50),
        zhuanzhang_pingzheng VARCHAR(500),
        beizhu TEXT,
        caiwu_queren_ren VARCHAR(36),
        caiwu_queren_shijian TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36) NOT NULL,
        updated_by VARCHAR(36),
        is_deleted CHAR(1) DEFAULT 'N'
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_zhifu_liushui_dingdan_id ON zhifu_liushui(zhifu_dingdan_id);
    CREATE INDEX IF NOT EXISTS idx_zhifu_liushui_kehu_id ON zhifu_liushui(kehu_id);
    CREATE INDEX IF NOT EXISTS idx_zhifu_liushui_bianhao ON zhifu_liushui(liushui_bianhao);
    CREATE INDEX IF NOT EXISTS idx_zhifu_liushui_leixing ON zhifu_liushui(liushui_leixing);
    CREATE INDEX IF NOT EXISTS idx_zhifu_liushui_jiaoyishijian ON zhifu_liushui(jiaoyishijian);

    -- 添加注释
    COMMENT ON TABLE zhifu_liushui IS '支付流水表';
    COMMENT ON COLUMN zhifu_liushui.zhifu_dingdan_id IS '支付订单ID';
    COMMENT ON COLUMN zhifu_liushui.kehu_id IS '客户ID';
    COMMENT ON COLUMN zhifu_liushui.liushui_bianhao IS '流水编号';
    COMMENT ON COLUMN zhifu_liushui.liushui_leixing IS '流水类型';
    COMMENT ON COLUMN zhifu_liushui.jiaoyijine IS '交易金额';
    COMMENT ON COLUMN zhifu_liushui.shouxufei IS '手续费';
    COMMENT ON COLUMN zhifu_liushui.shiji_shouru IS '实际收入';
    COMMENT ON COLUMN zhifu_liushui.zhifu_fangshi IS '支付方式';
    COMMENT ON COLUMN zhifu_liushui.zhifu_zhanghu IS '支付账户';
    COMMENT ON COLUMN zhifu_liushui.disanfang_liushui_hao IS '第三方流水号';
    COMMENT ON COLUMN zhifu_liushui.disanfang_dingdan_hao IS '第三方订单号';
    COMMENT ON COLUMN zhifu_liushui.jiaoyishijian IS '交易时间';
    COMMENT ON COLUMN zhifu_liushui.daozhangjian IS '到账时间';
    COMMENT ON COLUMN zhifu_liushui.liushui_zhuangtai IS '流水状态';
    COMMENT ON COLUMN zhifu_liushui.duizhang_zhuangtai IS '对账状态';
    COMMENT ON COLUMN zhifu_liushui.yinhang_mingcheng IS '银行名称';
    COMMENT ON COLUMN zhifu_liushui.yinhang_zhanghu IS '银行账户';
    COMMENT ON COLUMN zhifu_liushui.zhuanzhang_pingzheng IS '转账凭证图片路径';
    COMMENT ON COLUMN zhifu_liushui.beizhu IS '备注';
    COMMENT ON COLUMN zhifu_liushui.caiwu_queren_ren IS '财务确认人ID';
    COMMENT ON COLUMN zhifu_liushui.caiwu_queren_shijian IS '财务确认时间';
    COMMENT ON COLUMN zhifu_liushui.created_at IS '创建时间';
    COMMENT ON COLUMN zhifu_liushui.updated_at IS '更新时间';
    COMMENT ON COLUMN zhifu_liushui.created_by IS '创建人ID';
    COMMENT ON COLUMN zhifu_liushui.updated_by IS '更新人ID';
    COMMENT ON COLUMN zhifu_liushui.is_deleted IS '是否删除：Y-是，N-否';
    """
    
    # 支付通知表
    zhifu_tongzhi_sql = """
    CREATE TABLE IF NOT EXISTS zhifu_tongzhi (
        id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        zhifu_dingdan_id VARCHAR(36),
        hetong_id VARCHAR(36),
        jieshou_ren_id VARCHAR(36) NOT NULL,
        tongzhi_leixing VARCHAR(50) NOT NULL,
        tongzhi_biaoti VARCHAR(200) NOT NULL,
        tongzhi_neirong TEXT NOT NULL,
        tongzhi_zhuangtai VARCHAR(20) DEFAULT 'unread' NOT NULL,
        youxian_ji VARCHAR(20) DEFAULT 'normal' NOT NULL,
        fasong_shijian TIMESTAMP NOT NULL,
        yuedu_shijian TIMESTAMP,
        guoqi_shijian TIMESTAMP,
        kuozhan_shuju TEXT,
        lianjie_url VARCHAR(500),
        fasong_qudao VARCHAR(50) DEFAULT 'system' NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(36) NOT NULL,
        updated_by VARCHAR(36),
        is_deleted CHAR(1) DEFAULT 'N'
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_zhifu_tongzhi_jieshou_ren ON zhifu_tongzhi(jieshou_ren_id);
    CREATE INDEX IF NOT EXISTS idx_zhifu_tongzhi_leixing ON zhifu_tongzhi(tongzhi_leixing);
    CREATE INDEX IF NOT EXISTS idx_zhifu_tongzhi_zhuangtai ON zhifu_tongzhi(tongzhi_zhuangtai);
    CREATE INDEX IF NOT EXISTS idx_zhifu_tongzhi_fasong_shijian ON zhifu_tongzhi(fasong_shijian);

    -- 添加注释
    COMMENT ON TABLE zhifu_tongzhi IS '支付通知表';
    COMMENT ON COLUMN zhifu_tongzhi.zhifu_dingdan_id IS '支付订单ID';
    COMMENT ON COLUMN zhifu_tongzhi.hetong_id IS '合同ID';
    COMMENT ON COLUMN zhifu_tongzhi.jieshou_ren_id IS '接收人ID';
    COMMENT ON COLUMN zhifu_tongzhi.tongzhi_leixing IS '通知类型';
    COMMENT ON COLUMN zhifu_tongzhi.tongzhi_biaoti IS '通知标题';
    COMMENT ON COLUMN zhifu_tongzhi.tongzhi_neirong IS '通知内容';
    COMMENT ON COLUMN zhifu_tongzhi.tongzhi_zhuangtai IS '通知状态';
    COMMENT ON COLUMN zhifu_tongzhi.youxian_ji IS '优先级';
    COMMENT ON COLUMN zhifu_tongzhi.fasong_shijian IS '发送时间';
    COMMENT ON COLUMN zhifu_tongzhi.yuedu_shijian IS '阅读时间';
    COMMENT ON COLUMN zhifu_tongzhi.guoqi_shijian IS '过期时间';
    COMMENT ON COLUMN zhifu_tongzhi.kuozhan_shuju IS '扩展数据（JSON格式）';
    COMMENT ON COLUMN zhifu_tongzhi.lianjie_url IS '相关链接URL';
    COMMENT ON COLUMN zhifu_tongzhi.fasong_qudao IS '发送渠道';
    COMMENT ON COLUMN zhifu_tongzhi.created_at IS '创建时间';
    COMMENT ON COLUMN zhifu_tongzhi.updated_at IS '更新时间';
    COMMENT ON COLUMN zhifu_tongzhi.created_by IS '创建人ID';
    COMMENT ON COLUMN zhifu_tongzhi.updated_by IS '更新人ID';
    COMMENT ON COLUMN zhifu_tongzhi.is_deleted IS '是否删除：Y-是，N-否';
    """
    
    try:
        with engine.connect() as connection:
            logger.info("开始创建支付管理相关表...")
            
            # 创建支付订单表
            logger.info("创建支付订单表...")
            connection.execute(text(zhifu_dingdan_sql))
            connection.commit()
            logger.info("✅ 支付订单表创建成功")
            
            # 创建支付流水表
            logger.info("创建支付流水表...")
            connection.execute(text(zhifu_liushui_sql))
            connection.commit()
            logger.info("✅ 支付流水表创建成功")
            
            # 创建支付通知表
            logger.info("创建支付通知表...")
            connection.execute(text(zhifu_tongzhi_sql))
            connection.commit()
            logger.info("✅ 支付通知表创建成功")
            
            logger.info("🎉 所有支付管理表创建完成！")
            
    except Exception as e:
        logger.error(f"❌ 创建表失败: {e}")
        raise


if __name__ == "__main__":
    create_payment_tables()
    print("✅ 阶段3支付管理表创建完成！")
