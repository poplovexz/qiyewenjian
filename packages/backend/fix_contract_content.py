#!/usr/bin/env python3
"""
修复合同内容 - 重新渲染合同模板变量

使用方法：
python3 fix_contract_content.py <合同ID>

示例：
python3 fix_contract_content.py 6f33cf8e-4df5-4704-ae1b-d889be0fc72f
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong import Hetong
from models.hetong_guanli.hetong_moban import HetongMoban
from models.kehu_guanli.kehu import Kehu
from services.hetong_guanli.hetong_generate_service import HetongGenerateService

# 数据库连接
DATABASE_URL = "postgresql://postgres:password@localhost:5432/proxy_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def fix_contract_content(contract_id: str):
    """修复合同内容"""
    session = Session()
    
    try:
        print(f"=== 修复合同内容 ===")
        print(f"合同ID: {contract_id}")
        
        # 查询合同
        contract = session.query(Hetong).filter(
            Hetong.id == contract_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if not contract:
            print(f"❌ 错误：合同不存在或已删除")
            return False
        
        print(f"✅ 找到合同: {contract.hetong_mingcheng}")
        print(f"   合同编号: {contract.hetong_bianhao}")
        print(f"   合同金额: {contract.payment_amount}")
        
        # 查询客户
        customer = session.query(Kehu).filter(
            Kehu.id == contract.kehu_id,
            Kehu.is_deleted == "N"
        ).first()
        
        if not customer:
            print(f"❌ 错误：客户不存在")
            return False
        
        print(f"✅ 找到客户: {customer.gongsi_mingcheng}")
        
        # 查询模板
        template = session.query(HetongMoban).filter(
            HetongMoban.id == contract.hetong_moban_id,
            HetongMoban.is_deleted == "N"
        ).first()
        
        if not template:
            print(f"❌ 错误：合同模板不存在")
            return False
        
        print(f"✅ 找到模板: {template.moban_mingcheng}")
        
        # 准备变量
        variables = {
            "hetong_bianhao": contract.hetong_bianhao,
            "hetong_jine": float(contract.payment_amount) if contract.payment_amount else 0,
            "hetong_mingcheng": contract.hetong_mingcheng,
        }
        
        # 如果有乙方主体，添加乙方信息
        if contract.yifang_zhuti_id:
            from models.hetong_guanli.hetong_yifang_zhuti import HetongYifangZhuti
            yifang = session.query(HetongYifangZhuti).filter(
                HetongYifangZhuti.id == contract.yifang_zhuti_id,
                HetongYifangZhuti.is_deleted == "N"
            ).first()
            
            if yifang:
                print(f"✅ 找到乙方主体: {yifang.zhuti_mingcheng}")
                variables["yifang_mingcheng"] = yifang.zhuti_mingcheng
                variables["shoukuan_zhanghu_ming"] = yifang.zhuti_mingcheng or ""  # 使用主体名称作为账户名
                variables["shoukuan_zhanghao"] = yifang.yinhangzhanghu or ""  # 银行账户
                variables["shoukuan_kaihuhang"] = yifang.kaihuhang or ""  # 开户行
        
        # 重新渲染模板
        print("\n=== 重新渲染模板 ===")
        service = HetongGenerateService(session)
        new_content = service._render_template(
            template_content=template.moban_neirong,
            customer=customer,
            variables=variables
        )
        
        # 更新合同内容
        print("\n=== 更新合同内容 ===")
        contract.hetong_neirong = new_content
        session.commit()
        
        print("✅ 合同内容已更新！")
        print(f"\n预览前100个字符:")
        print(new_content[:100])
        print("...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 fix_contract_content.py <合同ID>")
        print("示例: python3 fix_contract_content.py 6f33cf8e-4df5-4704-ae1b-d889be0fc72f")
        sys.exit(1)
    
    contract_id = sys.argv[1]
    success = fix_contract_content(contract_id)
    
    if success:
        print("\n✅ 修复完成！请刷新合同签署页面查看效果。")
        sys.exit(0)
    else:
        print("\n❌ 修复失败！")
        sys.exit(1)

