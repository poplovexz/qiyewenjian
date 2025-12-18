#!/usr/bin/env python3
"""
分析所有合同模板中使用的变量，检查是否都有对应的代码支持
"""
import sys
import os
import re
from collections import defaultdict

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/backend/src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hetong_guanli.hetong_moban import HetongMoban
from core.config import settings

def analyze_templates():
    """分析所有模板中的变量"""
    
    # 创建数据库连接
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 查询所有模板
        templates = session.query(HetongMoban).filter(
            HetongMoban.is_deleted == "N"
        ).all()
        
        print(f"\n{'='*80}")
        print("分析所有合同模板中的变量")
        print(f"{'='*80}\n")
        
        all_variables = set()
        template_variables = {}
        
        for template in templates:
            print(f"\n【模板】{template.moban_mingcheng}")
            print(f"模板ID: {template.id}")
            
            content = template.moban_neirong or ""
            
            # 查找所有变量（支持多种格式）
            # 格式1: {{key}}
            vars1 = re.findall(r'\{\{([^}\s]+)\}\}', content)
            # 格式2: {{ key }}
            vars2 = re.findall(r'\{\{\s+([^}]+?)\s+\}\}', content)
            # 格式3: 任意空格
            vars3 = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', content)
            
            # 合并所有变量
            variables = set(vars1 + vars2 + vars3)
            variables = {v.strip() for v in variables}  # 去除空格
            
            template_variables[template.moban_mingcheng] = variables
            all_variables.update(variables)
            
            print(f"发现 {len(variables)} 个变量:")
            for var in sorted(variables):
                print(f"  - {var}")
        
        print(f"\n{'='*80}")
        print(f"所有模板中使用的变量汇总（共 {len(all_variables)} 个）")
        print(f"{'='*80}\n")
        
        # 代码中定义的变量（从 _generate_contract_content 和 _render_template）
        code_variables = {
            # _generate_contract_content 中定义的变量
            "hetong_bianhao", "jiafang_mingcheng", "yifang_mingcheng",
            "fuwu_kaishi_riqi", "fuwu_jieshu_riqi", "fuwu_taocan",
            "hetong_zongjine", "hetong_zongjine_daxie", "shoufu_jine",
            "shoukuan_zhanghu_ming", "shoukuan_zhanghao", "shoukuan_kaihuhang",
            "jiafang_qianming", "yifang_qianming", "jiafang_qianyue_riqi", "yifang_qianyue_riqi",
            "hetong_mingcheng", "hetong_jine",
            "kehu_mingcheng", "kehu_lianxiren", "kehu_dianhua", "kehu_dizhi",
            "qianshu_riqi", "shengxiao_riqi", "daoqi_riqi",

            # 增值服务合同和税务咨询合同专用变量
            "kaishi_riqi", "jieshu_riqi", "fuwu_feiyong", "zhifu_fangshi",

            # _render_template 中定义的客户变量
            "kehu_youxiang", "kehu_tongyi_shehui_xinyong_daima",
            "faren_daibiao", "lianxi_dizhi", "lianxi_dianhua",
            "gongsi_mingcheng", "zhuce_dizhi", "faren_xingming",
            "faren_shenfenzheng", "faren_lianxi", "chengli_riqi",
        }
        
        # 检查哪些变量在模板中使用但代码中没有定义
        missing_in_code = all_variables - code_variables
        
        # 检查哪些变量在代码中定义但模板中没有使用
        unused_in_templates = code_variables - all_variables
        
        print("\n【分析结果】\n")
        
        if missing_in_code:
            print(f"⚠️  警告：以下 {len(missing_in_code)} 个变量在模板中使用，但代码中没有定义：")
            for var in sorted(missing_in_code):
                print(f"  ❌ {var}")
                # 显示哪些模板使用了这个变量
                using_templates = [name for name, vars in template_variables.items() if var in vars]
                print(f"     使用该变量的模板: {', '.join(using_templates)}")
        else:
            print("✅ 所有模板中的变量都在代码中有定义")
        
        print()
        
        if unused_in_templates:
            print(f"ℹ️  信息：以下 {len(unused_in_templates)} 个变量在代码中定义，但模板中没有使用：")
            for var in sorted(unused_in_templates):
                print(f"  - {var}")
        else:
            print("✅ 代码中定义的所有变量都在模板中使用")
        
        # 检查变量格式
        print(f"\n{'='*80}")
        print("检查变量格式")
        print(f"{'='*80}\n")
        
        format_issues = []
        for template in templates:
            content = template.moban_neirong or ""
            
            # 查找所有变量占位符（包括空格）
            all_placeholders = re.findall(r'\{\{[^}]+\}\}', content)
            
            for placeholder in all_placeholders:
                # 检查是否有多个空格
                if '  ' in placeholder:  # 两个或更多空格
                    format_issues.append({
                        'template': template.moban_mingcheng,
                        'placeholder': placeholder,
                        'issue': '包含多个连续空格'
                    })
                
                # 检查是否有不对称的空格（例如 {{ key}} 或 {{key }}）
                if placeholder.startswith('{{ ') and not placeholder.endswith(' }}'):
                    format_issues.append({
                        'template': template.moban_mingcheng,
                        'placeholder': placeholder,
                        'issue': '左侧有空格但右侧没有'
                    })
                elif not placeholder.startswith('{{ ') and placeholder.endswith(' }}'):
                    format_issues.append({
                        'template': template.moban_mingcheng,
                        'placeholder': placeholder,
                        'issue': '右侧有空格但左侧没有'
                    })
        
        if format_issues:
            print(f"⚠️  发现 {len(format_issues)} 个格式问题：\n")
            for issue in format_issues:
                print(f"  模板: {issue['template']}")
                print(f"  占位符: {issue['placeholder']}")
                print(f"  问题: {issue['issue']}\n")
        else:
            print("✅ 所有变量格式都正常（只有 {{key}} 或 {{ key }} 两种格式）")
        
        # 总结
        print(f"\n{'='*80}")
        print("总结")
        print(f"{'='*80}\n")
        
        print("✅ 代码支持的变量格式:")
        print("  - {{{{key}}}} (没有空格)")
        print("  - {{{{ key }}}} (两侧各一个空格)")
        print()
        
        if missing_in_code:
            print(f"❌ 存在风险：{len(missing_in_code)} 个变量在模板中使用但代码中没有定义")
            print("   这些变量在生成合同时不会被替换！")
        else:
            print("✅ 无风险：所有模板变量都有代码支持")
        
        print()
        
        if format_issues:
            print(f"⚠️  存在格式问题：{len(format_issues)} 个变量占位符格式不规范")
            print("   建议统一使用 {{{{key}}}} 或 {{{{ key }}}} 格式")
        else:
            print("✅ 无格式问题：所有变量占位符格式规范")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    analyze_templates()

