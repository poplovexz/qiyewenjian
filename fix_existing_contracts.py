#!/usr/bin/env python3
"""
修复已存在合同中未替换的变量
"""
import sys
import os
import re

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong import Hetong
from models.hetong_guanli.hetong_moban import HetongMoban
from models.kehu_guanli.kehu import Kehu
from services.hetong_guanli.hetong_generate_service import HetongGenerateService
from core.config import settings

def fix_contracts():
    """修复合同中未替换的变量"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 查询所有有未替换变量的合同
        contracts = session.query(Hetong).filter(
            Hetong.is_deleted == "N"
        ).all()
        
        fixed_count = 0
        skip_count = 0
        
        print("\n=== 开始修复合同变量 ===\n")
        
        for contract in contracts:
            content = contract.hetong_neirong or ""
            
            # 检查是否有未替换的变量
            variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', content)
            
            if not variables:
                skip_count += 1
                continue
            
            print(f"\n【修复合同】{contract.hetong_bianhao}")
            print(f"合同名称: {contract.hetong_mingcheng}")
            print(f"发现 {len(set(variables))} 个未替换的变量")
            
            try:
                # 获取模板
                template = session.query(HetongMoban).filter(
                    HetongMoban.id == contract.hetong_moban_id
                ).first()
                
                if not template:
                    print("❌ 跳过：找不到模板")
                    skip_count += 1
                    continue
                
                # 获取客户
                customer = session.query(Kehu).filter(
                    Kehu.id == contract.kehu_id
                ).first()
                
                if not customer:
                    print("❌ 跳过：找不到客户")
                    skip_count += 1
                    continue
                
                # 准备变量
                from datetime import datetime, timedelta
                
                # 获取合同金额
                hetong_jine = float(contract.payment_amount) if contract.payment_amount else 0
                
                # 计算服务日期
                fuwu_kaishi_riqi = contract.shengxiao_riqi or datetime.now()
                fuwu_jieshu_riqi = contract.daoqi_riqi or (fuwu_kaishi_riqi + timedelta(days=365))
                
                # 获取乙方主体
                yifang_zhuti = None
                if contract.yifang_zhuti_id:
                    from models.hetong_guanli.hetong_yifang_zhuti import HetongYifangZhuti
                    yifang_zhuti = session.query(HetongYifangZhuti).filter(
                        HetongYifangZhuti.id == contract.yifang_zhuti_id,
                        HetongYifangZhuti.is_deleted == "N"
                    ).first()
                
                variables = {
                    # 基本信息
                    "hetong_bianhao": contract.hetong_bianhao,
                    "jiafang_mingcheng": customer.gongsi_mingcheng or "",
                    "yifang_mingcheng": yifang_zhuti.zhuti_mingcheng if yifang_zhuti else "上海XX财务咨询有限公司",
                    
                    # 服务日期
                    "fuwu_kaishi_riqi": fuwu_kaishi_riqi.strftime("%Y年%m月%d日"),
                    "fuwu_jieshu_riqi": fuwu_jieshu_riqi.strftime("%Y年%m月%d日"),
                    
                    # 服务内容
                    "fuwu_taocan": contract.hetong_mingcheng,
                    
                    # 金额信息
                    "hetong_zongjine": f"{hetong_jine:.2f}",
                    "hetong_jine": f"{hetong_jine:.2f}",
                    "shoufu_jine": f"{hetong_jine:.2f}",
                    
                    # 收款信息
                    "shoukuan_zhanghu_ming": yifang_zhuti.zhuti_mingcheng if yifang_zhuti else "上海XX财务咨询有限公司",
                    "shoukuan_zhanghao": yifang_zhuti.yinhangzhanghu if yifang_zhuti else "1234567890123456789",
                    "shoukuan_kaihuhang": yifang_zhuti.kaihuhang if yifang_zhuti else "中国XX银行上海XX支行",
                    
                    # 签名信息
                    "jiafang_qianming": "",
                    "yifang_qianming": "",
                    "jiafang_qianyue_riqi": "",
                    "yifang_qianyue_riqi": "",
                    
                    # 兼容旧变量名
                    "hetong_mingcheng": contract.hetong_mingcheng,
                    "kehu_mingcheng": customer.gongsi_mingcheng or "",
                    "kehu_lianxiren": customer.faren_xingming or "",
                    "kehu_dianhua": customer.lianxi_dianhua or "",
                    "kehu_dizhi": customer.lianxi_dizhi or "",
                    "qianshu_riqi": datetime.now().strftime("%Y年%m月%d日"),
                    "shengxiao_riqi": fuwu_kaishi_riqi.strftime("%Y年%m月%d日"),
                    "daoqi_riqi": fuwu_jieshu_riqi.strftime("%Y年%m月%d日")
                }
                
                # 重新渲染模板
                service = HetongGenerateService(session)
                new_content = service._render_template(
                    template_content=template.moban_neirong,
                    customer=customer,
                    variables=variables
                )
                
                # 更新合同内容
                contract.hetong_neirong = new_content
                session.commit()
                
                print("✅ 修复成功")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ 修复失败: {e}")
                session.rollback()
                skip_count += 1
                continue
        
        print("\n=== 修复完成 ===")
        print(f"✅ 成功修复: {fixed_count} 个合同")
        print(f"⏭️  跳过: {skip_count} 个合同")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_contracts()

