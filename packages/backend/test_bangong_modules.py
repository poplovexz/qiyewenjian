#!/usr/bin/env python3
"""
办公管理模块完整性测试脚本
测试所有5个模块的后端功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块是否可以正常导入"""
    print("=" * 60)
    print("测试1: 模块导入测试")
    print("=" * 60)
    
    modules_to_test = [
        # Models
        ("models.bangong_guanli.baoxiao", "BaoxiaoShenqing"),
        ("models.bangong_guanli.qingjia", "QingjiaShenqing"),
        ("models.bangong_guanli.duiwai_fukuan", "DuiwaiFukuanShenqing"),
        ("models.bangong_guanli.caigou", "CaigouShenqing"),
        ("models.bangong_guanli.gongzuo_jiaojie", "GongzuoJiaojieDan"),
        
        # Schemas
        ("schemas.bangong_guanli.baoxiao_schemas", "BaoxiaoShenqingCreate"),
        ("schemas.bangong_guanli.qingjia_schemas", "QingjiaShenqingCreate"),
        ("schemas.bangong_guanli.duiwai_fukuan_schemas", "DuiwaiFukuanShenqingCreate"),
        ("schemas.bangong_guanli.caigou_schemas", "CaigouShenqingCreate"),
        ("schemas.bangong_guanli.gongzuo_jiaojie_schemas", "GongzuoJiaojieDanCreate"),
        
        # Services
        ("services.bangong_guanli.baoxiao_service", "BaoxiaoService"),
        ("services.bangong_guanli.qingjia_service", "QingjiaService"),
        ("services.bangong_guanli.duiwai_fukuan_service", "DuiwaiFukuanService"),
        ("services.bangong_guanli.caigou_service", "CaigouService"),
        ("services.bangong_guanli.gongzuo_jiaojie_service", "GongzuoJiaojieService"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {module_path}.{class_name}")
            success_count += 1
        except Exception as e:
            print(f"✗ {module_path}.{class_name}: {str(e)}")
            fail_count += 1
    
    print(f"\n导入测试结果: {success_count} 成功, {fail_count} 失败")
    return fail_count == 0


def test_api_endpoints():
    """测试API端点是否正确定义"""
    print("\n" + "=" * 60)
    print("测试2: API端点测试")
    print("=" * 60)
    
    api_modules = [
        "api.api_v1.endpoints.bangong_guanli.baoxiao",
        "api.api_v1.endpoints.bangong_guanli.qingjia",
        "api.api_v1.endpoints.bangong_guanli.duiwai_fukuan",
        "api.api_v1.endpoints.bangong_guanli.caigou",
        "api.api_v1.endpoints.bangong_guanli.gongzuo_jiaojie",
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_path in api_modules:
        try:
            module = __import__(module_path, fromlist=['router'])
            router = getattr(module, 'router')
            routes = router.routes
            print(f"✓ {module_path}: {len(routes)} 个路由")
            
            # 显示路由详情
            for route in routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = ', '.join(route.methods) if route.methods else 'N/A'
                    print(f"  - {methods:10} {route.path}")
            
            success_count += 1
        except Exception as e:
            print(f"✗ {module_path}: {str(e)}")
            fail_count += 1
    
    print(f"\nAPI端点测试结果: {success_count} 成功, {fail_count} 失败")
    return fail_count == 0


def test_service_methods():
    """测试Service类是否包含必要的方法"""
    print("\n" + "=" * 60)
    print("测试3: Service方法测试")
    print("=" * 60)
    
    required_methods = [
        'create',
        'get_by_id',
        'get_list',
        'update',
        'delete',
        'submit_for_approval',
        'approve_application',
        'reject_application',
    ]
    
    services = [
        ("services.bangong_guanli.baoxiao_service", "BaoxiaoService"),
        ("services.bangong_guanli.qingjia_service", "QingjiaService"),
        ("services.bangong_guanli.duiwai_fukuan_service", "DuiwaiFukuanService"),
        ("services.bangong_guanli.caigou_service", "CaigouService"),
    ]
    
    # 交接单使用不同的方法名
    handover_methods = [
        'create',
        'get_by_id',
        'get_list',
        'update',
        'delete',
        'submit_for_confirm',
        'confirm_handover',
        'reject_handover',
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_path, class_name in services:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(cls, method):
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"✗ {class_name}: 缺少方法 {', '.join(missing_methods)}")
                fail_count += 1
            else:
                print(f"✓ {class_name}: 所有必需方法都存在")
                success_count += 1
        except Exception as e:
            print(f"✗ {class_name}: {str(e)}")
            fail_count += 1
    
    # 测试交接单Service
    try:
        module = __import__("services.bangong_guanli.gongzuo_jiaojie_service", fromlist=["GongzuoJiaojieService"])
        cls = getattr(module, "GongzuoJiaojieService")
        
        missing_methods = []
        for method in handover_methods:
            if not hasattr(cls, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ GongzuoJiaojieService: 缺少方法 {', '.join(missing_methods)}")
            fail_count += 1
        else:
            print("✓ GongzuoJiaojieService: 所有必需方法都存在")
            success_count += 1
    except Exception as e:
        print(f"✗ GongzuoJiaojieService: {str(e)}")
        fail_count += 1
    
    print(f"\nService方法测试结果: {success_count} 成功, {fail_count} 失败")
    return fail_count == 0


def test_schema_fields():
    """测试Schema是否包含必要的字段"""
    print("\n" + "=" * 60)
    print("测试4: Schema字段测试")
    print("=" * 60)
    
    schemas = [
        ("schemas.bangong_guanli.baoxiao_schemas", "BaoxiaoShenqingCreate", 
         ['baoxiao_leixing', 'baoxiao_jine', 'baoxiao_yuanyin']),
        ("schemas.bangong_guanli.qingjia_schemas", "QingjiaShenqingCreate",
         ['qingjia_leixing', 'kaishi_shijian', 'jieshu_shijian', 'qingjia_tianshu']),
        ("schemas.bangong_guanli.duiwai_fukuan_schemas", "DuiwaiFukuanShenqingCreate",
         ['fukuan_duixiang', 'fukuan_jine', 'fukuan_yuanyin']),
        ("schemas.bangong_guanli.caigou_schemas", "CaigouShenqingCreate",
         ['caigou_leixing', 'caigou_mingcheng', 'caigou_shuliang']),
        ("schemas.bangong_guanli.gongzuo_jiaojie_schemas", "GongzuoJiaojieDanCreate",
         ['jieshou_ren_id', 'jiaojie_yuanyin', 'jiaojie_neirong']),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_path, class_name, required_fields in schemas:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            
            # 获取schema的字段
            if hasattr(cls, 'model_fields'):
                fields = cls.model_fields.keys()
            elif hasattr(cls, '__fields__'):
                fields = cls.__fields__.keys()
            else:
                fields = []
            
            missing_fields = [f for f in required_fields if f not in fields]
            
            if missing_fields:
                print(f"✗ {class_name}: 缺少字段 {', '.join(missing_fields)}")
                fail_count += 1
            else:
                print(f"✓ {class_name}: 所有必需字段都存在 ({len(fields)} 个字段)")
                success_count += 1
        except Exception as e:
            print(f"✗ {class_name}: {str(e)}")
            fail_count += 1
    
    print(f"\nSchema字段测试结果: {success_count} 成功, {fail_count} 失败")
    return fail_count == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("办公管理模块完整性测试")
    print("=" * 60 + "\n")
    
    results = [("模块导入", test_imports()), ("API端点", test_api_endpoints()), ("Service方法", test_service_methods()), ("Schema字段", test_schema_fields())]
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name:20} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！")
        print("=" * 60)
        return 0
    else:
        print("✗ 部分测试失败，请检查上述错误信息")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

