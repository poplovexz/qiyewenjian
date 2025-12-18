"""
测试产品步骤API的脚本
用于诊断产品步骤保存问题
"""
import sys
sys.path.insert(0, 'src')

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinXiangmu
from services.chanpin_guanli import ChanpinBuzouService
from schemas.chanpin_guanli import ChanpinBuzouCreate, ChanpinBuzouUpdate
from decimal import Decimal
import asyncio


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def test_product_steps():
    """测试产品步骤功能"""
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print_section("1. 查找产品：股权变更（内资）")
        
        product = db.query(ChanpinXiangmu).filter(
            and_(
                ChanpinXiangmu.xiangmu_bianma == 'zengzhi_1_2',
                ChanpinXiangmu.is_deleted == 'N'
            )
        ).first()
        
        if not product:
            print("❌ 未找到产品")
            return
        
        print(f"✅ 找到产品")
        print(f"   产品名称: {product.xiangmu_mingcheng}")
        print(f"   产品编码: {product.xiangmu_bianma}")
        print(f"   产品ID: {product.id}")
        
        print_section("2. 查询现有步骤")
        
        service = ChanpinBuzouService(db)
        existing_steps = await service.get_buzou_list(product.id)
        
        print(f"现有步骤数量: {len(existing_steps)}")
        if existing_steps:
            for i, step in enumerate(existing_steps, 1):
                print(f"  {i}. {step.buzou_mingcheng} - ¥{step.buzou_feiyong}")
        
        print_section("3. 测试创建新步骤")
        
        # 测试各种场景
        test_cases = [
            {
                "name": "正常步骤",
                "data": {
                    "buzou_mingcheng": "测试步骤-正常",
                    "xiangmu_id": product.id,
                    "yugu_shichang": Decimal("1.5"),
                    "shichang_danwei": "xiaoshi",
                    "buzou_feiyong": Decimal("100.00"),
                    "buzou_miaoshu": "这是一个正常的测试步骤",
                    "paixu": 0,
                    "shi_bixu": "Y",
                    "zhuangtai": "active"
                },
                "should_succeed": True
            },
            {
                "name": "预估时长为0（应该失败）",
                "data": {
                    "buzou_mingcheng": "测试步骤-时长为0",
                    "xiangmu_id": product.id,
                    "yugu_shichang": Decimal("0"),
                    "shichang_danwei": "xiaoshi",
                    "buzou_feiyong": Decimal("100.00"),
                    "buzou_miaoshu": "预估时长为0",
                    "paixu": 0,
                    "shi_bixu": "Y",
                    "zhuangtai": "active"
                },
                "should_succeed": False
            },
            {
                "name": "费用为0（应该成功）",
                "data": {
                    "buzou_mingcheng": "测试步骤-费用为0",
                    "xiangmu_id": product.id,
                    "yugu_shichang": Decimal("1.0"),
                    "shichang_danwei": "xiaoshi",
                    "buzou_feiyong": Decimal("0"),
                    "buzou_miaoshu": "费用为0",
                    "paixu": 0,
                    "shi_bixu": "N",
                    "zhuangtai": "active"
                },
                "should_succeed": True
            }
        ]
        
        created_ids = []
        
        for test_case in test_cases:
            print(f"\n测试: {test_case['name']}")
            try:
                buzou_data = ChanpinBuzouCreate(**test_case['data'])
                result = await service.create_buzou(buzou_data, 'test_user')
                
                if test_case['should_succeed']:
                    print(f"  ✅ 创建成功 (ID: {result.id})")
                    created_ids.append(result.id)
                else:
                    print(f"  ⚠️  预期失败但成功了 (ID: {result.id})")
                    created_ids.append(result.id)
                    
            except Exception as e:
                if not test_case['should_succeed']:
                    print(f"  ✅ 预期失败: {str(e)}")
                else:
                    print(f"  ❌ 意外失败: {str(e)}")
        
        print_section("4. 测试更新步骤")
        
        if created_ids:
            test_id = created_ids[0]
            print(f"更新步骤 ID: {test_id}")
            
            try:
                update_data = ChanpinBuzouUpdate(
                    buzou_mingcheng="更新后的步骤名称",
                    buzou_feiyong=Decimal("200.00")
                )
                result = await service.update_buzou(test_id, update_data, 'test_user')
                print(f"  ✅ 更新成功")
                print(f"     新名称: {result.buzou_mingcheng}")
                print(f"     新费用: ¥{result.buzou_feiyong}")
            except Exception as e:
                print(f"  ❌ 更新失败: {str(e)}")
        
        print_section("5. 清理测试数据")
        
        for step_id in created_ids:
            try:
                await service.delete_buzou(step_id, 'test_user')
                print(f"  ✅ 删除步骤 {step_id}")
            except Exception as e:
                print(f"  ❌ 删除失败 {step_id}: {str(e)}")
        
        print_section("测试完成")
        print("✅ 所有测试已完成")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_product_steps())

