"""
创建产品管理相关数据表的脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from core.config import settings
from core.database import Base
from models.chanpin_guanli import ChanpinFenlei, ChanpinXiangmu, ChanpinBuzou


def create_product_tables():
    """创建产品管理相关数据表"""
    print("开始创建产品管理数据表...")
    
    # 创建数据库引擎
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            ChanpinFenlei.__table__,
            ChanpinXiangmu.__table__,
            ChanpinBuzou.__table__
        ])
        
        print("✅ 产品管理数据表创建成功！")
        print("已创建的表：")
        print("  - chanpin_fenlei (产品分类表)")
        print("  - chanpin_xiangmu (产品项目表)")
        print("  - chanpin_buzou (产品步骤表)")
        
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False
    
    return True


def insert_sample_data():
    """插入示例数据"""
    print("\n开始插入示例数据...")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as conn:
            # 插入产品分类示例数据
            category_sql = """
            INSERT INTO chanpin_fenlei (
                id, fenlei_mingcheng, fenlei_bianma, chanpin_leixing,
                miaoshu, paixu, zhuangtai, created_by, created_at, updated_at, is_deleted
            ) VALUES
            (
                'cat_001', '工商注册', 'gongshang_zhuce', 'zengzhi',
                '企业工商注册相关服务', 1, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'cat_002', '税务服务', 'shuiwu_fuwu', 'zengzhi',
                '税务申报、筹划等服务', 2, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'cat_003', '代理记账基础', 'daili_jizhang_jchu', 'daili_jizhang',
                '基础代理记账服务', 1, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'cat_004', '代理记账增值', 'daili_jizhang_zengzhi', 'daili_jizhang',
                '代理记账增值服务', 2, 'active', 'system', NOW(), NOW(), 'N'
            )
            ON CONFLICT (id) DO NOTHING;
            """
            
            conn.execute(text(category_sql))
            
            # 插入产品项目示例数据
            product_sql = """
            INSERT INTO chanpin_xiangmu (
                id, xiangmu_mingcheng, xiangmu_bianma, fenlei_id,
                yewu_baojia, baojia_danwei, banshi_tianshu, xiangmu_beizhu,
                paixu, zhuangtai, created_by, created_at, updated_at, is_deleted
            ) VALUES
            (
                'prod_001', '有限公司注册', 'youxian_gongsi_zhuce', 'cat_001',
                1500.00, 'yuan', 15, '普通有限责任公司注册服务',
                1, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'prod_002', '个体工商户注册', 'geti_gongshanghu_zhuce', 'cat_001',
                800.00, 'yuan', 7, '个体工商户营业执照办理',
                2, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'prod_003', '一般纳税人申请', 'yiban_nashuiren_shenqing', 'cat_002',
                500.00, 'yuan', 10, '一般纳税人资格申请服务',
                1, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'prod_004', '小规模代理记账', 'xiaogui_daili_jizhang', 'cat_003',
                200.00, 'yue', 30, '小规模纳税人代理记账服务',
                1, 'active', 'system', NOW(), NOW(), 'N'
            ),
            (
                'prod_005', '一般纳税人代理记账', 'yiban_daili_jizhang', 'cat_003',
                400.00, 'yue', 30, '一般纳税人代理记账服务',
                2, 'active', 'system', NOW(), NOW(), 'N'
            )
            ON CONFLICT (id) DO NOTHING;
            """
            
            conn.execute(text(product_sql))
            
            # 插入产品步骤示例数据
            step_sql = """
            INSERT INTO chanpin_buzou (
                id, buzou_mingcheng, xiangmu_id, yugu_shichang, shichang_danwei,
                buzou_feiyong, buzou_miaoshu, paixu, shi_bixu, zhuangtai,
                created_by, created_at, updated_at, is_deleted
            ) VALUES
            (
                'step_001', '核名申请', 'prod_001', 2.0, 'xiaoshi',
                0.00, '企业名称预先核准申请', 1, 'Y', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'step_002', '准备注册材料', 'prod_001', 4.0, 'xiaoshi',
                0.00, '准备公司注册所需的各类材料', 2, 'Y', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'step_003', '工商局提交申请', 'prod_001', 1.0, 'xiaoshi',
                0.00, '到工商局提交注册申请材料', 3, 'Y', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'step_004', '领取营业执照', 'prod_001', 1.0, 'xiaoshi',
                0.00, '审核通过后领取营业执照', 4, 'Y', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'step_005', '刻制公章', 'prod_001', 2.0, 'xiaoshi',
                200.00, '刻制企业公章、财务章等', 5, 'Y', 'active',
                'system', NOW(), NOW(), 'N'
            ),
            (
                'step_006', '银行开户', 'prod_001', 3.0, 'xiaoshi',
                0.00, '协助企业开设银行基本户', 6, 'N', 'active',
                'system', NOW(), NOW(), 'N'
            )
            ON CONFLICT (id) DO NOTHING;
            """
            
            conn.execute(text(step_sql))
            
            conn.commit()
            
        print("✅ 示例数据插入成功！")
        print("已插入：")
        print("  - 4个产品分类")
        print("  - 5个产品项目")
        print("  - 6个产品步骤")
        
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("产品管理模块数据库初始化")
    print("=" * 50)
    
    # 创建数据表
    if not create_product_tables():
        return
    
    # 插入示例数据
    if not insert_sample_data():
        return
    
    print("\n🎉 产品管理模块数据库初始化完成！")
    print("\n接下来您可以：")
    print("1. 启动后端服务")
    print("2. 在前端访问产品管理页面")
    print("3. 根据需要添加产品管理相关权限")


if __name__ == "__main__":
    main()
