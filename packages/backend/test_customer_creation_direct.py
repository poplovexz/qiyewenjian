#!/usr/bin/env python3
"""
直接测试客户创建逻辑
"""
import sys
sys.path.insert(0, '/var/www/packages/backend/src')

from src.database import SessionLocal
from src.models.kehu_guanli.kehu import Kehu
import uuid

def test_create_customer():
    """测试创建客户"""
    db = SessionLocal()
    
    try:
        # 生成临时信用代码
        temp_credit_code = f"TEMP{uuid.uuid4().hex[:14].upper()}"
        
        # 创建客户数据
        kehu_data = {
            "gongsi_mingcheng": "测试公司XYZ",
            "tongyi_shehui_xinyong_daima": temp_credit_code,
            "faren_xingming": "测试法人",
            "lianxi_dianhua": "13800138000",
            "lianxi_youxiang": "test@example.com",
            "lianxi_dizhi": "测试地址",
            "zhuce_dizhi": "测试注册地址",
            "kehu_zhuangtai": "active",
            "created_by": "test-user-id"
        }
        
        print(f"创建客户数据: {kehu_data['gongsi_mingcheng']}")
        print(f"临时信用代码: {temp_credit_code}")
        
        # 创建客户
        kehu = Kehu(**kehu_data)
        db.add(kehu)
        db.flush()
        
        print("✅ 客户创建成功")
        print(f"   客户ID: {kehu.id}")
        print(f"   公司名称: {kehu.gongsi_mingcheng}")
        
        db.commit()
        
        return kehu.id
        
    except Exception as e:
        print(f"❌ 创建客户失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    customer_id = test_create_customer()
    if customer_id:
        print(f"\n测试成功！客户ID: {customer_id}")
    else:
        print("\n测试失败！")

