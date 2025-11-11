"""
更新增值服务产品数据脚本
"""
import sys
import uuid
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chanpin_guanli import ChanpinFenlei, ChanpinXiangmu


# 增值服务产品数据
ZENGZHI_DATA = {
    "工商": [
        {"name": "公司注册（内资）", "price": 380.00, "unit": "个", "cost": 0.00},
        {"name": "股权变更（内资）", "price": 3000.00, "unit": "个", "cost": 0.00},
        {"name": "公司注册（外资）", "price": 3380.00, "unit": "次", "cost": 0.00},
        {"name": "注销（未核税）", "price": 3000.00, "unit": "个", "cost": 0.00},
        {"name": "工商移除异常名录/税务移除异常名录", "price": 2000.00, "unit": "次", "cost": 0.00},
    ],
    "资质": [
        {"name": "出版物零售、批发", "price": 6800.00, "unit": "次", "cost": 0.00},
        {"name": "食品经营许可证（预包装）", "price": 2000.00, "unit": "张", "cost": 0.00},
        {"name": "医疗器械三类经营许可证", "price": 20000.00, "unit": "个", "cost": 0.00},
        {"name": "劳务派遣许可证", "price": 10800.00, "unit": "份", "cost": 0.00},
        {"name": "医疗器械二类备案", "price": 1800.00, "unit": "个", "cost": 0.00},
    ],
    "知产": [
        {"name": "国内商标注册", "price": 500.00, "unit": "个", "cost": 100.00},
    ],
    "财税": [
        {"name": "审计报告", "price": 2000.00, "unit": "次", "cost": 0.00},
        {"name": "评估报告", "price": 5000.00, "unit": "次", "cost": 0.00},
        {"name": "清算报告", "price": 2000.00, "unit": "个", "cost": 0.00},
        {"name": "税务风险检测报告", "price": 99.00, "unit": "份", "cost": 0.00},
        {"name": "共享开票", "price": 1200.00, "unit": "年", "cost": 0.00},
    ],
    "社保": [
        {"name": "社保开户", "price": 800.00, "unit": "次", "cost": 0.00},
        {"name": "生育津贴报销", "price": 1000.00, "unit": "次", "cost": 200.00},
        {"name": "社保补缴", "price": 300.00, "unit": "次", "cost": 50.00},
        {"name": "社保现场增员", "price": 300.00, "unit": "次", "cost": 50.00},
        {"name": "员工在京退休", "price": 2000.00, "unit": "次", "cost": 300.00},
    ],
    "银行": [
        {"name": "银行变更", "price": 500.00, "unit": "次", "cost": 100.00},
        {"name": "银行注销", "price": 500.00, "unit": "次", "cost": 100.00},
        {"name": "打回单", "price": 100.00, "unit": "月", "cost": 100.00},
        {"name": "银行开户", "price": 1000.00, "unit": "个", "cost": 100.00},
        {"name": "其他", "price": 500.00, "unit": "个", "cost": 50.00},
    ],
    "税务": [
        {"name": "税务核查", "price": 300.00, "unit": "次", "cost": 50.00},
        {"name": "税务疑难处理（会计原因导致）", "price": 300.00, "unit": "个", "cost": 50.00},
        {"name": "代开发票", "price": 300.00, "unit": "次", "cost": 50.00},
        {"name": "税务疑难处理（税局系统导致）", "price": 500.00, "unit": "次", "cost": 50.00},
        {"name": "税务疑难", "price": 300.00, "unit": "个", "cost": 50.00},
    ],
    "其他": [
        {"name": "提供资质人员", "price": 5000.00, "unit": "个", "cost": 0.00},
        {"name": "经济普查", "price": 200.00, "unit": "次", "cost": 0.00},
    ],
    "公积金": [
        {"name": "公积金开户", "price": 800.00, "unit": "次", "cost": 0.00},
        {"name": "公积金年度托管", "price": 600.00, "unit": "个", "cost": 0.00},
    ],
    "年度服务": [
        {"name": "汇算清缴", "price": 500.00, "unit": "年", "cost": 0.00},
        {"name": "社保基数调整", "price": 500.00, "unit": "年", "cost": 0.00},
        {"name": "工商年报", "price": 500.00, "unit": "年", "cost": 0.00},
        {"name": "残保金年报", "price": 500.00, "unit": "年", "cost": 0.00},
        {"name": "印花税", "price": 500.00, "unit": "年", "cost": 0.00},
    ],
    "医保": [
        {"name": "医保开户", "price": 500.00, "unit": "次", "cost": 50.00},
        {"name": "医保补缴", "price": 500.00, "unit": "次", "cost": 50.00},
    ],
    "境外公司服务": [
        {"name": "香港公司年审", "price": 3200.00, "unit": "次", "cost": 0.00},
        {"name": "香港公司审计", "price": 2500.00, "unit": "次", "cost": 0.00},
    ],
}


def update_zengzhi_products():
    """更新增值服务产品数据"""
    print("🚀 开始更新增值服务产品数据...")
    print("=" * 60)
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 统计信息
        created_categories = 0
        updated_categories = 0
        created_products = 0
        updated_products = 0
        deleted_products = 0
        
        # 获取所有现有的增值服务分类
        existing_categories = db.query(ChanpinFenlei).filter(
            and_(
                ChanpinFenlei.chanpin_leixing == "zengzhi",
                ChanpinFenlei.is_deleted == "N"
            )
        ).all()
        
        existing_category_names = {cat.fenlei_mingcheng: cat for cat in existing_categories}
        
        # 处理每个分类
        paixu = 1
        for category_name, products in ZENGZHI_DATA.items():
            print(f"\n📁 处理分类: {category_name}")
            
            # 检查分类是否存在
            if category_name in existing_category_names:
                category = existing_category_names[category_name]
                print(f"  ✓ 分类已存在，更新排序")
                category.paixu = paixu
                updated_categories += 1
            else:
                # 创建新分类
                category = ChanpinFenlei(
                    id=str(uuid.uuid4()),
                    fenlei_mingcheng=category_name,
                    fenlei_bianma=f"zengzhi_{paixu}",
                    chanpin_leixing="zengzhi",
                    miaoshu=f"{category_name}相关服务",
                    paixu=paixu,
                    zhuangtai="active",
                    created_by="system",
                    is_deleted="N"
                )
                db.add(category)
                db.flush()  # 获取ID
                print(f"  ✓ 创建新分类")
                created_categories += 1
            
            # 获取该分类下的现有产品
            existing_products = db.query(ChanpinXiangmu).filter(
                and_(
                    ChanpinXiangmu.fenlei_id == category.id,
                    ChanpinXiangmu.is_deleted == "N"
                )
            ).all()
            
            existing_product_names = {prod.xiangmu_mingcheng: prod for prod in existing_products}
            current_product_names = {prod["name"] for prod in products}
            
            # 删除不在新数据中的产品（软删除）
            for prod_name, prod in existing_product_names.items():
                if prod_name not in current_product_names:
                    prod.is_deleted = "Y"
                    deleted_products += 1
                    print(f"  ✗ 删除产品: {prod_name}")
            
            # 处理每个产品
            product_paixu = 1
            for product_data in products:
                product_name = product_data["name"]
                
                if product_name in existing_product_names:
                    # 更新现有产品
                    product = existing_product_names[product_name]
                    product.yewu_baojia = Decimal(str(product_data["price"]))
                    product.baojia_danwei = product_data["unit"]
                    product.paixu = product_paixu
                    # 更新成本价（如果有）
                    if hasattr(product, 'chengben_jia'):
                        product.chengben_jia = Decimal(str(product_data["cost"]))
                    print(f"  ↻ 更新产品: {product_name} - ¥{product_data['price']}/{product_data['unit']}")
                    updated_products += 1
                else:
                    # 创建新产品
                    product = ChanpinXiangmu(
                        id=str(uuid.uuid4()),
                        xiangmu_mingcheng=product_name,
                        xiangmu_bianma=f"{category.fenlei_bianma}_{product_paixu}",
                        fenlei_id=category.id,
                        yewu_baojia=Decimal(str(product_data["price"])),
                        baojia_danwei=product_data["unit"],
                        banshi_tianshu=0,
                        xiangmu_beizhu=None,
                        paixu=product_paixu,
                        zhuangtai="active",
                        created_by="system",
                        is_deleted="N"
                    )
                    db.add(product)
                    print(f"  + 创建产品: {product_name} - ¥{product_data['price']}/{product_data['unit']}")
                    created_products += 1
                
                product_paixu += 1
            
            paixu += 1
        
        # 提交所有更改
        db.commit()
        
        # 打印总结
        print("\n" + "=" * 60)
        print("✅ 增值服务产品数据更新完成！")
        print("=" * 60)
        print(f"\n📊 统计信息:")
        print(f"  分类:")
        print(f"    • 新建: {created_categories} 个")
        print(f"    • 更新: {updated_categories} 个")
        print(f"  产品:")
        print(f"    • 新建: {created_products} 个")
        print(f"    • 更新: {updated_products} 个")
        print(f"    • 删除: {deleted_products} 个")
        print(f"\n  总计: {len(ZENGZHI_DATA)} 个分类, {sum(len(prods) for prods in ZENGZHI_DATA.values())} 个产品")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  增值服务产品数据更新工具")
    print("=" * 60)
    
    if update_zengzhi_products():
        print("\n🎉 所有操作完成！")
        print("\n💡 提示:")
        print("  • 请重启后端服务以清除缓存")
        print("  • 刷新前端页面查看最新数据")
    else:
        print("\n⚠️  更新失败，请检查错误信息")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

