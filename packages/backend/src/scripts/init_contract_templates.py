#!/usr/bin/env python3
"""
初始化合同模板示例数据
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.hetong_guanli import HetongMoban


def init_contract_templates():
    """初始化合同模板示例数据"""
    db: Session = SessionLocal()
    
    try:
        # 合同模板示例数据
        template_data = [
            {
                "moban_mingcheng": "代理记账服务合同模板",
                "moban_bianma": "DLJZ_001",
                "hetong_leixing": "daili_jizhang",
                "moban_neirong": """
<h2 style="text-align: center;">代理记账服务合同</h2>

<p><strong>甲方（委托方）：</strong>{{ kehu_mingcheng }}</p>
<p><strong>地址：</strong>{{ kehu_dizhi }}</p>
<p><strong>联系电话：</strong>{{ kehu_lianxi }}</p>

<p><strong>乙方（受托方）：</strong>{{ fuwu_gongsi }}</p>
<p><strong>地址：</strong>{{ fuwu_gongsi_dizhi }}</p>
<p><strong>联系电话：</strong>{{ fuwu_gongsi_lianxi }}</p>

<h3>一、服务内容</h3>
<p>乙方为甲方提供以下代理记账服务：</p>
<ul>
    <li>{{ fuwu_neirong_1 }}</li>
    <li>{{ fuwu_neirong_2 }}</li>
    <li>{{ fuwu_neirong_3 }}</li>
</ul>

<h3>二、服务费用</h3>
<p>服务费用：{{ fuwu_jiage }}元/{{ jiage_danwei }}</p>
<p>付款方式：{{ fukuan_fangshi }}</p>

<h3>三、合同期限</h3>
<p>合同期限：{{ hetong_qixian }}</p>
<p>合同生效日期：{{ shengxiao_riqi }}</p>
<p>合同到期日期：{{ daoqi_riqi }}</p>

<h3>四、双方权利义务</h3>
<p>甲方义务：</p>
<ul>
    <li>按时提供完整、真实的会计资料</li>
    <li>按约定时间支付服务费用</li>
    <li>配合乙方开展代理记账工作</li>
</ul>

<p>乙方义务：</p>
<ul>
    <li>按时完成代理记账工作</li>
    <li>保证会计资料的安全性和保密性</li>
    <li>及时向甲方反馈财务状况</li>
</ul>

<h3>五、违约责任</h3>
<p>{{ weiyue_zeren }}</p>

<h3>六、其他约定</h3>
<p>{{ qita_yueding }}</p>

<p style="margin-top: 50px;">
<strong>甲方（盖章）：</strong>_________________ &nbsp;&nbsp;&nbsp;&nbsp; <strong>乙方（盖章）：</strong>_________________
</p>
<p>
<strong>签约日期：</strong>{{ qianyue_riqi }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>签约日期：</strong>{{ qianyue_riqi }}
</p>
                """,
                "bianliang_peizhi": json.dumps({
                    "kehu_mingcheng": {"label": "客户名称", "type": "string", "default": ""},
                    "kehu_dizhi": {"label": "客户地址", "type": "string", "default": ""},
                    "kehu_lianxi": {"label": "客户联系电话", "type": "string", "default": ""},
                    "fuwu_gongsi": {"label": "服务公司名称", "type": "string", "default": "代理记账有限公司"},
                    "fuwu_gongsi_dizhi": {"label": "服务公司地址", "type": "string", "default": ""},
                    "fuwu_gongsi_lianxi": {"label": "服务公司联系电话", "type": "string", "default": ""},
                    "fuwu_neirong_1": {"label": "服务内容1", "type": "string", "default": "建账建制，代理记账"},
                    "fuwu_neirong_2": {"label": "服务内容2", "type": "string", "default": "编制财务报表"},
                    "fuwu_neirong_3": {"label": "服务内容3", "type": "string", "default": "税务申报"},
                    "fuwu_jiage": {"label": "服务价格", "type": "number", "default": 2000},
                    "jiage_danwei": {"label": "价格单位", "type": "string", "default": "月"},
                    "fukuan_fangshi": {"label": "付款方式", "type": "string", "default": "按月支付"},
                    "hetong_qixian": {"label": "合同期限", "type": "string", "default": "12个月"},
                    "shengxiao_riqi": {"label": "生效日期", "type": "date", "default": ""},
                    "daoqi_riqi": {"label": "到期日期", "type": "date", "default": ""},
                    "weiyue_zeren": {"label": "违约责任", "type": "string", "default": "按照相关法律法规执行"},
                    "qita_yueding": {"label": "其他约定", "type": "string", "default": ""},
                    "qianyue_riqi": {"label": "签约日期", "type": "date", "default": ""}
                }, ensure_ascii=False),
                "banben_hao": "1.0",
                "shi_dangqian_banben": "Y",
                "moban_fenlei": "biaozhun",
                "moban_zhuangtai": "active",
                "beizhu": "标准代理记账服务合同模板",
                "paixu": 1
            },
            {
                "moban_mingcheng": "增值服务合同模板",
                "moban_bianma": "ZZFW_001",
                "hetong_leixing": "zengzhi_fuwu",
                "moban_neirong": """
<h2 style="text-align: center;">增值服务合同</h2>

<p><strong>甲方（委托方）：</strong>{{ kehu_mingcheng }}</p>
<p><strong>地址：</strong>{{ kehu_dizhi }}</p>
<p><strong>联系电话：</strong>{{ kehu_lianxi }}</p>

<p><strong>乙方（服务方）：</strong>{{ fuwu_gongsi }}</p>
<p><strong>地址：</strong>{{ fuwu_gongsi_dizhi }}</p>
<p><strong>联系电话：</strong>{{ fuwu_gongsi_lianxi }}</p>

<h3>一、服务项目</h3>
<p>乙方为甲方提供以下增值服务：</p>
<p><strong>服务名称：</strong>{{ fuwu_mingcheng }}</p>
<p><strong>服务内容：</strong>{{ fuwu_neirong }}</p>
<p><strong>服务标准：</strong>{{ fuwu_biaozhun }}</p>

<h3>二、服务费用</h3>
<p>服务费用：{{ fuwu_jiage }}元</p>
<p>付款方式：{{ fukuan_fangshi }}</p>
<p>付款时间：{{ fukuan_shijian }}</p>

<h3>三、服务期限</h3>
<p>服务开始时间：{{ kaishi_shijian }}</p>
<p>服务完成时间：{{ wancheng_shijian }}</p>
<p>服务期限：{{ fuwu_qixian }}</p>

<h3>四、服务要求</h3>
<p>{{ fuwu_yaoqiu }}</p>

<h3>五、验收标准</h3>
<p>{{ yanshou_biaozhun }}</p>

<h3>六、违约责任</h3>
<p>{{ weiyue_zeren }}</p>

<p style="margin-top: 50px;">
<strong>甲方（盖章）：</strong>_________________ &nbsp;&nbsp;&nbsp;&nbsp; <strong>乙方（盖章）：</strong>_________________
</p>
<p>
<strong>签约日期：</strong>{{ qianyue_riqi }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>签约日期：</strong>{{ qianyue_riqi }}
</p>
                """,
                "bianliang_peizhi": json.dumps({
                    "kehu_mingcheng": {"label": "客户名称", "type": "string", "default": ""},
                    "kehu_dizhi": {"label": "客户地址", "type": "string", "default": ""},
                    "kehu_lianxi": {"label": "客户联系电话", "type": "string", "default": ""},
                    "fuwu_gongsi": {"label": "服务公司名称", "type": "string", "default": "代理记账有限公司"},
                    "fuwu_gongsi_dizhi": {"label": "服务公司地址", "type": "string", "default": ""},
                    "fuwu_gongsi_lianxi": {"label": "服务公司联系电话", "type": "string", "default": ""},
                    "fuwu_mingcheng": {"label": "服务名称", "type": "string", "default": ""},
                    "fuwu_neirong": {"label": "服务内容", "type": "string", "default": ""},
                    "fuwu_biaozhun": {"label": "服务标准", "type": "string", "default": ""},
                    "fuwu_jiage": {"label": "服务价格", "type": "number", "default": 0},
                    "fukuan_fangshi": {"label": "付款方式", "type": "string", "default": "一次性付款"},
                    "fukuan_shijian": {"label": "付款时间", "type": "string", "default": "签约后3个工作日内"},
                    "kaishi_shijian": {"label": "开始时间", "type": "date", "default": ""},
                    "wancheng_shijian": {"label": "完成时间", "type": "date", "default": ""},
                    "fuwu_qixian": {"label": "服务期限", "type": "string", "default": ""},
                    "fuwu_yaoqiu": {"label": "服务要求", "type": "string", "default": ""},
                    "yanshou_biaozhun": {"label": "验收标准", "type": "string", "default": ""},
                    "weiyue_zeren": {"label": "违约责任", "type": "string", "default": "按照相关法律法规执行"},
                    "qianyue_riqi": {"label": "签约日期", "type": "date", "default": ""}
                }, ensure_ascii=False),
                "banben_hao": "1.0",
                "shi_dangqian_banben": "Y",
                "moban_fenlei": "biaozhun",
                "moban_zhuangtai": "active",
                "beizhu": "标准增值服务合同模板",
                "paixu": 2
            },
            {
                "moban_mingcheng": "咨询服务合同模板",
                "moban_bianma": "ZXFW_001",
                "hetong_leixing": "zixun_fuwu",
                "moban_neirong": """
<h2 style="text-align: center;">咨询服务合同</h2>

<p><strong>甲方（委托方）：</strong>{{ kehu_mingcheng }}</p>
<p><strong>地址：</strong>{{ kehu_dizhi }}</p>
<p><strong>联系电话：</strong>{{ kehu_lianxi }}</p>

<p><strong>乙方（咨询方）：</strong>{{ fuwu_gongsi }}</p>
<p><strong>地址：</strong>{{ fuwu_gongsi_dizhi }}</p>
<p><strong>联系电话：</strong>{{ fuwu_gongsi_lianxi }}</p>

<h3>一、咨询项目</h3>
<p><strong>项目名称：</strong>{{ xiangmu_mingcheng }}</p>
<p><strong>咨询内容：</strong>{{ zixun_neirong }}</p>
<p><strong>咨询目标：</strong>{{ zixun_mubiao }}</p>

<h3>二、咨询费用</h3>
<p>咨询费用：{{ zixun_feiyong }}元</p>
<p>付款方式：{{ fukuan_fangshi }}</p>

<h3>三、咨询期限</h3>
<p>咨询开始时间：{{ kaishi_shijian }}</p>
<p>咨询结束时间：{{ jieshu_shijian }}</p>

<h3>四、工作方式</h3>
<p>{{ gongzuo_fangshi }}</p>

<h3>五、交付成果</h3>
<p>{{ jiaofù_chengguo }}</p>

<h3>六、保密条款</h3>
<p>{{ baomi_tiaokuan }}</p>

<h3>七、违约责任</h3>
<p>{{ weiyue_zeren }}</p>

<p style="margin-top: 50px;">
<strong>甲方（盖章）：</strong>_________________ &nbsp;&nbsp;&nbsp;&nbsp; <strong>乙方（盖章）：</strong>_________________
</p>
<p>
<strong>签约日期：</strong>{{ qianyue_riqi }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>签约日期：</strong>{{ qianyue_riqi }}
</p>
                """,
                "bianliang_peizhi": json.dumps({
                    "kehu_mingcheng": {"label": "客户名称", "type": "string", "default": ""},
                    "kehu_dizhi": {"label": "客户地址", "type": "string", "default": ""},
                    "kehu_lianxi": {"label": "客户联系电话", "type": "string", "default": ""},
                    "fuwu_gongsi": {"label": "服务公司名称", "type": "string", "default": "代理记账有限公司"},
                    "fuwu_gongsi_dizhi": {"label": "服务公司地址", "type": "string", "default": ""},
                    "fuwu_gongsi_lianxi": {"label": "服务公司联系电话", "type": "string", "default": ""},
                    "xiangmu_mingcheng": {"label": "项目名称", "type": "string", "default": ""},
                    "zixun_neirong": {"label": "咨询内容", "type": "string", "default": ""},
                    "zixun_mubiao": {"label": "咨询目标", "type": "string", "default": ""},
                    "zixun_feiyong": {"label": "咨询费用", "type": "number", "default": 0},
                    "fukuan_fangshi": {"label": "付款方式", "type": "string", "default": "一次性付款"},
                    "kaishi_shijian": {"label": "开始时间", "type": "date", "default": ""},
                    "jieshu_shijian": {"label": "结束时间", "type": "date", "default": ""},
                    "gongzuo_fangshi": {"label": "工作方式", "type": "string", "default": ""},
                    "jiaofù_chengguo": {"label": "交付成果", "type": "string", "default": ""},
                    "baomi_tiaokuan": {"label": "保密条款", "type": "string", "default": "双方应对涉及的商业秘密承担保密义务"},
                    "weiyue_zeren": {"label": "违约责任", "type": "string", "default": "按照相关法律法规执行"},
                    "qianyue_riqi": {"label": "签约日期", "type": "date", "default": ""}
                }, ensure_ascii=False),
                "banben_hao": "1.0",
                "shi_dangqian_banben": "Y",
                "moban_fenlei": "biaozhun",
                "moban_zhuangtai": "active",
                "beizhu": "标准咨询服务合同模板",
                "paixu": 3
            }
        ]
        
        print("开始初始化合同模板示例数据...")
        
        # 创建合同模板
        created_count = 0
        for template_info in template_data:
            # 检查模板是否已存在
            existing_template = db.query(HetongMoban).filter(
                HetongMoban.moban_bianma == template_info["moban_bianma"],
                HetongMoban.is_deleted == "N"
            ).first()
            
            if not existing_template:
                template = HetongMoban(**template_info)
                db.add(template)
                created_count += 1
                print(f"创建合同模板: {template_info['moban_mingcheng']} ({template_info['moban_bianma']})")
            else:
                print(f"合同模板已存在: {template_info['moban_mingcheng']} ({template_info['moban_bianma']})")
        
        db.commit()
        
        print(f"\n合同模板示例数据初始化完成!")
        print(f"新创建模板数量: {created_count}")
        print(f"总模板数量: {len(template_data)}")
        
    except Exception as e:
        print(f"初始化合同模板时发生错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_contract_templates()
