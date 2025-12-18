#!/usr/bin/env python3
import sys
import os
sys.path.append('/var/www/packages/backend/src')

from sqlalchemy.orm import Session
from core.database import get_db
from models.xiansuo_guanli import XiansuoBaojia, Xiansuo
from models.kehu_guanli import Kehu

def check_quotes():
    """检查数据库中的报价记录"""
    # PTC-W0063: 添加默认值防止 StopIteration
    db = next(get_db(), None)
    if db is None:
        print("无法获取数据库连接")
        return

    try:
        # 查询所有报价记录
        quotes = db.query(XiansuoBaojia).all()
        print(f"数据库中共有 {len(quotes)} 条报价记录:")
        
        for quote in quotes:
            print(f"\n报价ID: {quote.id}")
            print(f"线索ID: {quote.xiansuo_id}")
            print(f"报价状态: {quote.baojia_zhuangtai}")
            print(f"有效期: {quote.youxiao_qi}")
            print(f"创建时间: {quote.created_at}")
            
            # 获取关联的线索信息
            xiansuo = db.query(Xiansuo).filter(Xiansuo.id == quote.xiansuo_id).first()
            if xiansuo:
                print(f"线索公司名称: {xiansuo.gongsi_mingcheng}")
                print(f"线索客户ID: {xiansuo.kehu_id}")
                
                # 获取客户信息
                kehu = db.query(Kehu).filter(Kehu.id == xiansuo.kehu_id).first()
                if kehu:
                    print(f"客户公司名称: {kehu.gongsi_mingcheng}")
            
            print("-" * 50)
            
    except Exception as e:
        print(f"查询报价记录时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_quotes()