#!/usr/bin/env python3
"""
添加支付方式表的微信和支付宝相关字段

运行方式:
cd packages/backend
source venv/bin/activate
export PYTHONPATH=/path/to/packages/backend/src
python3 scripts/add_payment_method_fields.py
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from sqlalchemy import text
from core.database import SessionLocal

def add_payment_method_fields():
    """添加支付方式表的新字段"""
    
    db = SessionLocal()
    
    try:
        
        # 检查表是否存在
        check_table_sql = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'hetong_zhifu_fangshi'
            );
        """)
        
        result = db.execute(check_table_sql).scalar()
        
        if not result:
            return False
        
        # 要添加的字段列表
        fields_to_add = [
            {
                'name': 'weixin_haoma',
                'sql': """
                    ALTER TABLE hetong_zhifu_fangshi 
                    ADD COLUMN IF NOT EXISTS weixin_haoma VARCHAR(100);
                """,
                'comment': """
                    COMMENT ON COLUMN hetong_zhifu_fangshi.weixin_haoma 
                    IS '微信号/微信收款账号';
                """
            },
            {
                'name': 'weixin_shoukuan_ming',
                'sql': """
                    ALTER TABLE hetong_zhifu_fangshi 
                    ADD COLUMN IF NOT EXISTS weixin_shoukuan_ming VARCHAR(100);
                """,
                'comment': """
                    COMMENT ON COLUMN hetong_zhifu_fangshi.weixin_shoukuan_ming 
                    IS '微信收款名';
                """
            },
            {
                'name': 'zhifubao_haoma',
                'sql': """
                    ALTER TABLE hetong_zhifu_fangshi 
                    ADD COLUMN IF NOT EXISTS zhifubao_haoma VARCHAR(100);
                """,
                'comment': """
                    COMMENT ON COLUMN hetong_zhifu_fangshi.zhifubao_haoma 
                    IS '支付宝账号';
                """
            },
            {
                'name': 'zhifubao_shoukuan_ming',
                'sql': """
                    ALTER TABLE hetong_zhifu_fangshi 
                    ADD COLUMN IF NOT EXISTS zhifubao_shoukuan_ming VARCHAR(100);
                """,
                'comment': """
                    COMMENT ON COLUMN hetong_zhifu_fangshi.zhifubao_shoukuan_ming 
                    IS '支付宝收款名';
                """
            },
            {
                'name': 'erweima_lujing',
                'sql': """
                    ALTER TABLE hetong_zhifu_fangshi 
                    ADD COLUMN IF NOT EXISTS erweima_lujing VARCHAR(500);
                """,
                'comment': """
                    COMMENT ON COLUMN hetong_zhifu_fangshi.erweima_lujing 
                    IS '收款二维码图片路径';
                """
            }
        ]
        
        # 添加每个字段
        for field in fields_to_add:
            try:
                # 检查字段是否已存在
                check_column_sql = text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'hetong_zhifu_fangshi' 
                        AND column_name = '{field['name']}'
                    );
                """)
                
                column_exists = db.execute(check_column_sql).scalar()
                
                if column_exists:
                    continue
                
                # 添加字段
                db.execute(text(field['sql']))
                
                # 添加注释
                db.execute(text(field['comment']))
                
            except Exception as e:
                raise
        
        # 提交事务
        db.commit()
        
        # 验证字段
        verify_sql = text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'hetong_zhifu_fangshi'
            AND column_name IN ('weixin_haoma', 'weixin_shoukuan_ming', 
                               'zhifubao_haoma', 'zhifubao_shoukuan_ming', 
                               'erweima_lujing')
            ORDER BY column_name;
        """)
        
        results = db.execute(verify_sql).fetchall()
        
        if results:
            for row in results:
        else:
        
        return True
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    
    success = add_payment_method_fields()
    
    if success:
    else:
    
    sys.exit(0 if success else 1)
