#!/usr/bin/env python3
"""
更新合同模板表结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import SessionLocal

def update_contract_template_table():
    """更新合同模板表结构"""
    db: Session = SessionLocal()
    
    try:
        
        # 添加缺失的字段
        alter_statements = [
            # 添加模板编码字段
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS moban_bianma VARCHAR(100) UNIQUE",
            
            # 重命名字段
            "ALTER TABLE hetong_moban RENAME COLUMN moban_leixing TO hetong_leixing",
            "ALTER TABLE hetong_moban RENAME COLUMN moban_banben TO banben_hao",
            "ALTER TABLE hetong_moban RENAME COLUMN zhuangtai TO moban_zhuangtai",
            
            # 添加新字段
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS bianliang_peizhi TEXT",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shi_dangqian_banben VARCHAR(1) DEFAULT 'Y'",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS moban_fenlei VARCHAR(50)",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shiyong_cishu INTEGER DEFAULT 0",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shenpi_zhuangtai VARCHAR(20) DEFAULT 'pending'",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shenpi_ren VARCHAR(36)",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shenpi_shijian TIMESTAMP",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS shenpi_yijian TEXT",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS beizhu TEXT",
            "ALTER TABLE hetong_moban ADD COLUMN IF NOT EXISTS paixu INTEGER DEFAULT 0",
            
            # 删除不需要的字段
            "ALTER TABLE hetong_moban DROP COLUMN IF EXISTS shiyong_fanwei",
            
            # 更新字段约束
            "ALTER TABLE hetong_moban ALTER COLUMN moban_zhuangtai SET DEFAULT 'draft'",
            "ALTER TABLE hetong_moban ALTER COLUMN banben_hao SET DEFAULT '1.0'",
            
            # 添加注释
            "COMMENT ON COLUMN hetong_moban.moban_bianma IS '模板编码'",
            "COMMENT ON COLUMN hetong_moban.hetong_leixing IS '合同类型：daili_jizhang(代理记账合同)、zengzhi_fuwu(增值服务合同)、zixun_fuwu(咨询服务合同)'",
            "COMMENT ON COLUMN hetong_moban.bianliang_peizhi IS '变量配置（JSON格式，定义可用变量和默认值）'",
            "COMMENT ON COLUMN hetong_moban.banben_hao IS '版本号'",
            "COMMENT ON COLUMN hetong_moban.shi_dangqian_banben IS '是否当前版本：Y(是)、N(否)'",
            "COMMENT ON COLUMN hetong_moban.moban_fenlei IS '模板分类：biaozhun(标准模板)、dingzhi(定制模板)'",
            "COMMENT ON COLUMN hetong_moban.moban_zhuangtai IS '模板状态：draft(草稿)、active(启用)、archived(归档)'",
            "COMMENT ON COLUMN hetong_moban.shiyong_cishu IS '使用次数'",
            "COMMENT ON COLUMN hetong_moban.shenpi_zhuangtai IS '审批状态：pending(待审批)、approved(已审批)、rejected(已拒绝)'",
            "COMMENT ON COLUMN hetong_moban.shenpi_ren IS '审批人ID'",
            "COMMENT ON COLUMN hetong_moban.shenpi_shijian IS '审批时间'",
            "COMMENT ON COLUMN hetong_moban.shenpi_yijian IS '审批意见'",
            "COMMENT ON COLUMN hetong_moban.beizhu IS '备注'",
            "COMMENT ON COLUMN hetong_moban.paixu IS '排序号'"
        ]
        
        for statement in alter_statements:
            try:
                db.execute(text(statement))
            except Exception as e:
                # 某些操作可能会失败（比如字段已存在），这是正常的
                logger.warning(f"操作失败: {str(e)}")

        # 提交更改
        db.commit()
        
        # 显示更新后的表结构
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'hetong_moban' 
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"  {row[0]}: {row[1]}")

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_contract_template_table()
