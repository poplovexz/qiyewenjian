#!/usr/bin/env python3
"""
测试支付方式新字段

验证微信和支付宝字段是否正确添加
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'backend' / 'src'))

from sqlalchemy import text, inspect
from core.database import SessionLocal


def test_payment_method_fields():
    """测试支付方式表的新字段"""
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("测试支付方式表字段")
        print("=" * 60)
        print()
        
        # 检查表结构
        print("1. 检查表结构...")
        inspector = inspect(db.bind)
        
        if 'hetong_zhifu_fangshi' not in inspector.get_table_names():
            print("❌ 表 hetong_zhifu_fangshi 不存在")
            return False
        
        columns = inspector.get_columns('hetong_zhifu_fangshi')
        column_names = [col['name'] for col in columns]
        
        print(f"✓ 表存在，共有 {len(columns)} 个字段")
        print()
        
        # 检查新字段
        print("2. 检查新增字段...")
        new_fields = [
            'weixin_haoma',
            'weixin_shoukuan_ming',
            'zhifubao_haoma',
            'zhifubao_shoukuan_ming',
            'erweima_lujing'
        ]
        
        all_exist = True
        for field in new_fields:
            if field in column_names:
                # 获取字段详细信息
                col_info = next((col for col in columns if col['name'] == field), None)
                if col_info:
                    col_type = str(col_info['type'])
                    nullable = "可空" if col_info['nullable'] else "非空"
                    print(f"  ✓ {field}: {col_type} ({nullable})")
            else:
                print(f"  ✗ {field}: 不存在")
                all_exist = False
        
        print()
        
        if not all_exist:
            print("❌ 部分字段缺失")
            return False
        
        # 测试插入数据
        print("3. 测试插入微信支付方式...")
        
        # 先查找一个乙方主体
        result = db.execute(text("""
            SELECT id FROM hetong_yifang_zhuti 
            WHERE is_deleted = 'N' 
            LIMIT 1
        """)).fetchone()
        
        if not result:
            print("  ⚠️  没有可用的乙方主体，跳过插入测试")
        else:
            yifang_id = result[0]
            
            # 插入测试数据
            insert_sql = text("""
                INSERT INTO hetong_zhifu_fangshi (
                    id, yifang_zhuti_id, zhifu_leixing, zhifu_mingcheng,
                    weixin_haoma, weixin_shoukuan_ming, erweima_lujing,
                    zhifu_zhuangtai, shi_moren, paixu, is_deleted,
                    created_at, updated_at, created_by
                ) VALUES (
                    gen_random_uuid()::text, :yifang_id, 'weixin', '测试微信支付',
                    'test_weixin_123', '测试收款人', '/uploads/test_qrcode.jpg',
                    'active', 'N', '0', 'N',
                    NOW(), NOW(), 'test_user'
                )
                RETURNING id, zhifu_mingcheng, weixin_haoma, weixin_shoukuan_ming, erweima_lujing
            """)
            
            result = db.execute(insert_sql, {'yifang_id': yifang_id}).fetchone()
            db.commit()
            
            if result:
                print("  ✓ 插入成功")
                print(f"    ID: {result[0]}")
                print(f"    名称: {result[1]}")
                print(f"    微信号: {result[2]}")
                print(f"    收款名: {result[3]}")
                print(f"    二维码: {result[4]}")
                
                # 删除测试数据
                delete_sql = text("DELETE FROM hetong_zhifu_fangshi WHERE id = :id")
                db.execute(delete_sql, {'id': result[0]})
                db.commit()
                print("  ✓ 测试数据已清理")
            else:
                print("  ✗ 插入失败")
                return False
        
        print()
        
        # 测试支付宝
        print("4. 测试插入支付宝支付方式...")
        
        if not result:
            print("  ⚠️  没有可用的乙方主体，跳过插入测试")
        else:
            insert_sql = text("""
                INSERT INTO hetong_zhifu_fangshi (
                    id, yifang_zhuti_id, zhifu_leixing, zhifu_mingcheng,
                    zhifubao_haoma, zhifubao_shoukuan_ming, erweima_lujing,
                    zhifu_zhuangtai, shi_moren, paixu, is_deleted,
                    created_at, updated_at, created_by
                ) VALUES (
                    gen_random_uuid()::text, :yifang_id, 'zhifubao', '测试支付宝',
                    'test@alipay.com', '测试支付宝收款人', '/uploads/test_alipay_qrcode.jpg',
                    'active', 'N', '0', 'N',
                    NOW(), NOW(), 'test_user'
                )
                RETURNING id, zhifu_mingcheng, zhifubao_haoma, zhifubao_shoukuan_ming, erweima_lujing
            """)
            
            result = db.execute(insert_sql, {'yifang_id': yifang_id}).fetchone()
            db.commit()
            
            if result:
                print("  ✓ 插入成功")
                print(f"    ID: {result[0]}")
                print(f"    名称: {result[1]}")
                print(f"    支付宝账号: {result[2]}")
                print(f"    收款名: {result[3]}")
                print(f"    二维码: {result[4]}")
                
                # 删除测试数据
                delete_sql = text("DELETE FROM hetong_zhifu_fangshi WHERE id = :id")
                db.execute(delete_sql, {'id': result[0]})
                db.commit()
                print("  ✓ 测试数据已清理")
            else:
                print("  ✗ 插入失败")
                return False
        
        print()
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_payment_method_fields()
    sys.exit(0 if success else 1)

