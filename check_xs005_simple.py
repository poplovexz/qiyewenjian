#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单检查线索XS005的脚本
"""
import sys
sys.path.insert(0, '/var/www/packages/backend/src')

from core.database import get_db
from models.xiansuo_guanli import Xiansuo
from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
from models.hetong_guanli import Hetong

def main():
    # PTC-W0063: 使用 next() 的默认值防止 StopIteration
    db = next(get_db(), None)
    if db is None:
        print("无法获取数据库连接")
        return

    try:
        print("=== 查找线索XS005 ===")
        
        # 查找线索XS005
        xiansuo = db.query(Xiansuo).filter(
            Xiansuo.xiansuo_bianhao == 'XS005',
            Xiansuo.is_deleted == 'N'
        ).first()
        
        if xiansuo:
            print(f"找到线索XS005:")
            print(f"  ID: {xiansuo.id}")
            print(f"  名称: {xiansuo.xiansuo_mingcheng}")
            print(f"  状态: {xiansuo.xiansuo_zhuangtai}")
            print(f"  客户ID: {xiansuo.kehu_id}")
            
            # 查找该线索的报价
            print(f"\n=== 查找线索的报价 ===")
            baojia_list = db.query(XiansuoBaojia).filter(
                XiansuoBaojia.xiansuo_id == xiansuo.id,
                XiansuoBaojia.is_deleted == 'N'
            ).all()
            
            if baojia_list:
                print(f"找到 {len(baojia_list)} 个报价:")
                for i, baojia in enumerate(baojia_list, 1):
                    print(f"\n报价 {i}:")
                    print(f"  ID: {baojia.id}")
                    print(f"  编码: {baojia.baojia_bianma}")
                    print(f"  名称: {baojia.baojia_mingcheng}")
                    print(f"  状态: {baojia.baojia_zhuangtai}")
                    print(f"  总金额: {baojia.zongji_jine}")
                    
                    # 查找该报价关联的合同
                    hetong = db.query(Hetong).filter(
                        Hetong.baojia_id == baojia.id,
                        Hetong.is_deleted == 'N'
                    ).first()
                    
                    if hetong:
                        print(f"  关联合同:")
                        print(f"    合同ID: {hetong.id}")
                        print(f"    合同编号: {hetong.hetong_bianhao}")
                        print(f"    合同名称: {hetong.hetong_mingcheng}")
                        print(f"    合同状态: {hetong.hetong_zhuangtai}")
                        print(f"    创建时间: {hetong.created_at}")
                    else:
                        print(f"  没有关联的合同")
            else:
                print("该线索没有报价")
        else:
            print("未找到线索XS005")
            
            # 列出所有线索编号
            print(f"\n=== 系统中的所有线索编号 ===")
            all_xiansuo = db.query(Xiansuo.xiansuo_bianhao, Xiansuo.xiansuo_mingcheng).filter(
                Xiansuo.is_deleted == 'N'
            ).limit(10).all()
            
            for xs in all_xiansuo:
                print(f"  - {xs.xiansuo_bianhao}: {xs.xiansuo_mingcheng}")
        
        # 查看所有合同
        print(f"\n=== 系统中的所有合同 ===")
        all_hetong = db.query(Hetong).filter(
            Hetong.is_deleted == 'N'
        ).all()
        
        print(f"系统中共有 {len(all_hetong)} 个合同:")
        for hetong in all_hetong:
            print(f"  - {hetong.hetong_bianhao}: {hetong.hetong_mingcheng} ({hetong.hetong_zhuangtai})")
            if hetong.baojia_id:
                print(f"    关联报价ID: {hetong.baojia_id}")

    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
