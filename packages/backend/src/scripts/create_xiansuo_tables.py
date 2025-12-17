#!/usr/bin/env python3
"""
创建线索管理相关数据表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.config import settings
from models.base import Base
from models.xiansuo_guanli import (
    Xiansuo,
    XiansuoLaiyuan,
    XiansuoZhuangtai,
    XiansuoGenjin
)


def create_xiansuo_tables():
    """创建线索管理相关数据表"""
    print("开始创建线索管理数据表...")
    
    # 创建数据库引擎
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            XiansuoLaiyuan.__table__,
            XiansuoZhuangtai.__table__,
            Xiansuo.__table__,
            XiansuoGenjin.__table__
        ])
        
        print("✅ 线索管理数据表创建成功！")
        print("已创建的表：")
        print("  - xiansuo_laiyuan (线索来源表)")
        print("  - xiansuo_zhuangtai (线索状态表)")
        print("  - xiansuo (线索主表)")
        print("  - xiansuo_genjin (线索跟进记录表)")
        
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False
    
    return True


def insert_sample_data():
    """插入示例数据"""
    print("\n开始插入示例数据...")
    
    engine = create_engine(str(settings.DATABASE_URL))
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 插入线索来源示例数据
        laiyuan_data = [
            {
                "laiyuan_mingcheng": "官网咨询",
                "laiyuan_bianma": "website",
                "laiyuan_leixing": "online",
                "huoqu_chengben": 50.00,
                "miaoshu": "通过官网在线咨询表单获取的线索"
            },
            {
                "laiyuan_mingcheng": "百度推广",
                "laiyuan_bianma": "baidu_ads",
                "laiyuan_leixing": "online",
                "huoqu_chengben": 200.00,
                "miaoshu": "百度搜索推广获取的线索"
            },
            {
                "laiyuan_mingcheng": "朋友推荐",
                "laiyuan_bianma": "referral",
                "laiyuan_leixing": "referral",
                "huoqu_chengben": 0.00,
                "miaoshu": "客户朋友推荐的线索"
            },
            {
                "laiyuan_mingcheng": "电话营销",
                "laiyuan_bianma": "telemarketing",
                "laiyuan_leixing": "offline",
                "huoqu_chengben": 100.00,
                "miaoshu": "电话营销获取的线索"
            }
        ]
        
        for data in laiyuan_data:
            existing = db.query(XiansuoLaiyuan).filter(
                XiansuoLaiyuan.laiyuan_bianma == data["laiyuan_bianma"]
            ).first()
            
            if not existing:
                laiyuan = XiansuoLaiyuan(**data)
                db.add(laiyuan)
        
        # 插入线索状态示例数据
        zhuangtai_data = [
            {
                "zhuangtai_mingcheng": "新线索",
                "zhuangtai_bianma": "new",
                "zhuangtai_leixing": "initial",
                "yanse_bianma": "#909399",
                "tubiao_mingcheng": "el-icon-plus",
                "paixu": 1,
                "miaoshu": "刚录入系统的新线索"
            },
            {
                "zhuangtai_mingcheng": "跟进中",
                "zhuangtai_bianma": "following",
                "zhuangtai_leixing": "processing",
                "shangyige_zhuangtai": "new",
                "xiayige_zhuangtai": "interested,no_response",
                "yanse_bianma": "#409EFF",
                "tubiao_mingcheng": "el-icon-phone",
                "paixu": 2,
                "miaoshu": "销售人员正在跟进的线索"
            },
            {
                "zhuangtai_mingcheng": "有意向",
                "zhuangtai_bianma": "interested",
                "zhuangtai_leixing": "processing",
                "shangyige_zhuangtai": "following",
                "xiayige_zhuangtai": "quoted,lost",
                "yanse_bianma": "#E6A23C",
                "tubiao_mingcheng": "el-icon-star-on",
                "paixu": 3,
                "miaoshu": "客户表现出购买意向"
            },
            {
                "zhuangtai_mingcheng": "已报价",
                "zhuangtai_bianma": "quoted",
                "zhuangtai_leixing": "processing",
                "shangyige_zhuangtai": "interested",
                "xiayige_zhuangtai": "won,lost",
                "yanse_bianma": "#F56C6C",
                "tubiao_mingcheng": "el-icon-document",
                "paixu": 4,
                "miaoshu": "已向客户提供报价"
            },
            {
                "zhuangtai_mingcheng": "成交",
                "zhuangtai_bianma": "won",
                "zhuangtai_leixing": "success",
                "shangyige_zhuangtai": "quoted",
                "yanse_bianma": "#67C23A",
                "tubiao_mingcheng": "el-icon-success",
                "shi_zhongzhong_zhuangtai": "Y",
                "shi_chenggong_zhuangtai": "Y",
                "paixu": 5,
                "miaoshu": "线索成功转化为客户"
            },
            {
                "zhuangtai_mingcheng": "无效",
                "zhuangtai_bianma": "lost",
                "zhuangtai_leixing": "failed",
                "yanse_bianma": "#909399",
                "tubiao_mingcheng": "el-icon-close",
                "shi_zhongzhong_zhuangtai": "Y",
                "paixu": 6,
                "miaoshu": "无购买意向或不符合条件的线索"
            },
            {
                "zhuangtai_mingcheng": "无回应",
                "zhuangtai_bianma": "no_response",
                "zhuangtai_leixing": "failed",
                "shangyige_zhuangtai": "following",
                "xiayige_zhuangtai": "lost",
                "yanse_bianma": "#C0C4CC",
                "tubiao_mingcheng": "el-icon-warning",
                "paixu": 7,
                "miaoshu": "多次跟进无回应的线索"
            }
        ]
        
        for data in zhuangtai_data:
            existing = db.query(XiansuoZhuangtai).filter(
                XiansuoZhuangtai.zhuangtai_bianma == data["zhuangtai_bianma"]
            ).first()
            
            if not existing:
                zhuangtai = XiansuoZhuangtai(**data)
                db.add(zhuangtai)
        
        db.commit()
        print("✅ 示例数据插入成功！")
        
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("线索管理模块 - 数据库初始化")
    print("=" * 50)
    
    # 步骤1：创建数据表
    if not create_xiansuo_tables():
        print("数据表创建失败，退出初始化")
        return False
    
    # 步骤2：插入示例数据
    if not insert_sample_data():
        print("示例数据插入失败，退出初始化")
        return False
    
    print("=" * 50)
    print("✓ 线索管理模块数据库初始化完成！")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
