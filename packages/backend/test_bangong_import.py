#!/usr/bin/env python3
"""
测试办公管理模块导入
"""
import sys
sys.path.insert(0, 'src')

try:
    print("测试导入办公管理模块...")
    from models.bangong_guanli import (
        BaoxiaoShenqing,
        QingjiaShenqing,
        DuiwaiFukuanShenqing,
        CaigouShenqing,
        GongzuoJiaojie
    )
    print("✓ 模型导入成功")
    
    from schemas.bangong_guanli import (
        BaoxiaoShenqingCreate,
        QingjiaShenqingCreate
    )
    print("✓ Schema导入成功")
    
    from services.bangong_guanli import (
        BaoxiaoService,
        QingjiaService
    )
    print("✓ Service导入成功")
    
    from api.api_v1.endpoints.bangong_guanli import baoxiao, qingjia
    print("✓ API端点导入成功")
    
    print("\n所有导入测试通过！")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

