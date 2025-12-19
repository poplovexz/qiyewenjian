#!/usr/bin/env python3
"""
阶段2：合同表结构更新脚本
为合同表添加报价关联、乙方主体、电子签名等字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

def update_hetong_table():
    """更新合同表结构"""
    
    # 要执行的SQL语句列表
    sql_statements = [
        # 启用UUID扩展
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"",

        # 创建合同乙方主体表
        """
        CREATE TABLE IF NOT EXISTS hetong_yifang_zhuti (
            id VARCHAR(36) PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
            zhuti_mingcheng VARCHAR(200) NOT NULL,
            zhuti_leixing VARCHAR(50) NOT NULL,
            lianxi_ren VARCHAR(100) NOT NULL,
            lianxi_dianhua VARCHAR(20),
            lianxi_youxiang VARCHAR(100),
            zhuce_dizhi VARCHAR(500),
            tongxin_dizhi VARCHAR(500),
            zhengjianhao VARCHAR(100),
            zhengjianleixing VARCHAR(50),
            kaihuhang VARCHAR(200),
            yinhangzhanghu VARCHAR(50),
            zhuti_zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
            beizhu TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(36),
            updated_by VARCHAR(36),
            is_deleted VARCHAR(1) DEFAULT 'N' NOT NULL,
            remark TEXT
        )
        """,
        
        # 创建合同支付方式表
        """
        CREATE TABLE IF NOT EXISTS hetong_zhifu_fangshi (
            id VARCHAR(36) PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
            yifang_zhuti_id VARCHAR(36) NOT NULL,
            zhifu_leixing VARCHAR(50) NOT NULL,
            zhifu_mingcheng VARCHAR(100) NOT NULL,
            zhanghu_mingcheng VARCHAR(100),
            zhanghu_haoma VARCHAR(100),
            kaihuhang_mingcheng VARCHAR(200),
            kaihuhang_dizhi VARCHAR(300),
            lianhanghao VARCHAR(50),
            danbi_xiange DECIMAL(15,2),
            riqi_xiange DECIMAL(15,2),
            zhifu_zhuangtai VARCHAR(20) DEFAULT 'active' NOT NULL,
            shi_moren VARCHAR(1) DEFAULT 'N' NOT NULL,
            paixu VARCHAR(10) DEFAULT '0' NOT NULL,
            beizhu TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(36),
            updated_by VARCHAR(36),
            is_deleted VARCHAR(1) DEFAULT 'N' NOT NULL,
            remark TEXT,
            FOREIGN KEY (yifang_zhuti_id) REFERENCES hetong_yifang_zhuti(id) ON DELETE CASCADE
        )
        """,
        
        # 为合同表添加新字段
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS baojia_id VARCHAR(36)",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS yifang_zhuti_id VARCHAR(36)",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS dianziqianming_lujing VARCHAR(500)",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS qianming_ren_id VARCHAR(36)",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS qianming_shijian TIMESTAMP",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS qianming_ip VARCHAR(50)",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS qianming_beizhu TEXT",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS hetong_laiyuan VARCHAR(50) DEFAULT 'manual'",
        "ALTER TABLE hetong ADD COLUMN IF NOT EXISTS zidong_shengcheng VARCHAR(1) DEFAULT 'N'",
        
        # 添加外键约束
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_hetong_baojia_id'
            ) THEN
                ALTER TABLE hetong ADD CONSTRAINT fk_hetong_baojia_id 
                FOREIGN KEY (baojia_id) REFERENCES xiansuo_baojia(id);
            END IF;
        END $$
        """,
        
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_hetong_yifang_zhuti_id'
            ) THEN
                ALTER TABLE hetong ADD CONSTRAINT fk_hetong_yifang_zhuti_id 
                FOREIGN KEY (yifang_zhuti_id) REFERENCES hetong_yifang_zhuti(id);
            END IF;
        END $$
        """,
        
        # 添加注释
        "COMMENT ON TABLE hetong_yifang_zhuti IS '合同乙方主体表'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhuti_mingcheng IS '主体名称'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhuti_leixing IS '主体类型：geren(个人)、gongsi(公司)、hehuo(合伙企业)、qita(其他)'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.lianxi_ren IS '联系人'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.lianxi_dianhua IS '联系电话'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.lianxi_youxiang IS '联系邮箱'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhuce_dizhi IS '注册地址'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.tongxin_dizhi IS '通信地址'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhengjianhao IS '证件号码（身份证号/统一社会信用代码等）'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhengjianleixing IS '证件类型：shenfenzheng(身份证)、yingyezhizhao(营业执照)、qita(其他)'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.kaihuhang IS '开户行'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.yinhangzhanghu IS '银行账户'",
        "COMMENT ON COLUMN hetong_yifang_zhuti.zhuti_zhuangtai IS '主体状态：active(启用)、inactive(停用)'",
        
        "COMMENT ON TABLE hetong_zhifu_fangshi IS '合同支付方式表'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.yifang_zhuti_id IS '乙方主体ID'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.zhifu_leixing IS '支付类型：weixin(微信支付)、zhifubao(支付宝)、yinhangzhuanzhang(银行转账)、xianjin(现金)、qita(其他)'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.zhifu_mingcheng IS '支付方式名称'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.zhanghu_mingcheng IS '账户名称'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.zhanghu_haoma IS '账户号码'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.kaihuhang_mingcheng IS '开户行名称'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.kaihuhang_dizhi IS '开户行地址'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.lianhanghao IS '联行号'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.danbi_xiange IS '单笔限额'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.riqi_xiange IS '日期限额'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.zhifu_zhuangtai IS '支付状态：active(启用)、inactive(停用)'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.shi_moren IS '是否默认：Y(是)、N(否)'",
        "COMMENT ON COLUMN hetong_zhifu_fangshi.paixu IS '排序号'",
        
        "COMMENT ON COLUMN hetong.baojia_id IS '关联报价ID'",
        "COMMENT ON COLUMN hetong.yifang_zhuti_id IS '乙方主体ID'",
        "COMMENT ON COLUMN hetong.dianziqianming_lujing IS '电子签名文件路径'",
        "COMMENT ON COLUMN hetong.qianming_ren_id IS '签名人ID'",
        "COMMENT ON COLUMN hetong.qianming_shijian IS '签名时间'",
        "COMMENT ON COLUMN hetong.qianming_ip IS '签名IP地址'",
        "COMMENT ON COLUMN hetong.qianming_beizhu IS '签名备注'",
        "COMMENT ON COLUMN hetong.hetong_laiyuan IS '合同来源：manual(手动创建)、auto_from_quote(报价自动生成)'",
        "COMMENT ON COLUMN hetong.zidong_shengcheng IS '是否自动生成：Y(是)、N(否)'"
    ]
    
    try:
        with engine.connect() as connection:
            for sql in sql_statements:
                connection.execute(text(sql))
                connection.commit()
        
    except Exception as e:
        raise

if __name__ == "__main__":
    update_hetong_table()
