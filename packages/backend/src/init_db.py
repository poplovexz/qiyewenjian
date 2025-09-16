#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from src.core.config import settings
from src.core.database import engine
from src.models import Base


def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        # 尝试连接数据库
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ 数据库连接成功")
        return True
    except OperationalError as e:
        if "database" in str(e) and "does not exist" in str(e):
            print("数据库不存在，尝试创建...")
            
            # 从完整的数据库URL中提取数据库名
            db_url = str(settings.DATABASE_URL)
            db_name = db_url.split("/")[-1]
            
            # 连接到postgres默认数据库来创建新数据库
            postgres_url = db_url.replace(f"/{db_name}", "/postgres")
            postgres_engine = create_engine(postgres_url)
            
            try:
                with postgres_engine.connect() as conn:
                    # 设置自动提交模式
                    conn.execute(text("COMMIT"))
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✓ 数据库 {db_name} 创建成功")
                return True
            except Exception as create_error:
                print(f"✗ 创建数据库失败: {create_error}")
                return False
        else:
            print(f"✗ 数据库连接失败: {e}")
            return False


def create_tables():
    """创建所有数据表"""
    try:
        print("开始创建数据表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 数据表创建成功")
        return True
    except Exception as e:
        print(f"✗ 创建数据表失败: {e}")
        return False


def init_basic_data():
    """初始化基础数据"""
    from sqlalchemy.orm import sessionmaker
    from src.models import Jiaose, Quanxian, JiaoseQuanxian
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("开始初始化基础数据...")
            
            # 创建基础角色
            roles_data = [
                {"jiaose_ming": "系统管理员", "jiaose_bianma": "admin", "miaoshu": "系统最高权限管理员"},
                {"jiaose_ming": "会计", "jiaose_bianma": "accountant", "miaoshu": "负责账务处理和税务申报"},
                {"jiaose_ming": "客服", "jiaose_bianma": "customer_service", "miaoshu": "负责客户服务和沟通"},
                {"jiaose_ming": "客户", "jiaose_bianma": "customer", "miaoshu": "系统客户用户"}
            ]
            
            for role_data in roles_data:
                existing_role = db.query(Jiaose).filter(Jiaose.jiaose_bianma == role_data["jiaose_bianma"]).first()
                if not existing_role:
                    role = Jiaose(**role_data)
                    db.add(role)
            
            # 创建基础权限
            permissions_data = [
                {"quanxian_ming": "用户管理", "quanxian_bianma": "user_manage", "ziyuan_leixing": "menu", "miaoshu": "用户管理菜单权限"},
                {"quanxian_ming": "客户管理", "quanxian_bianma": "customer_manage", "ziyuan_leixing": "menu", "miaoshu": "客户管理菜单权限"},
                {"quanxian_ming": "合同管理", "quanxian_bianma": "contract_manage", "ziyuan_leixing": "menu", "miaoshu": "合同管理菜单权限"},
                {"quanxian_ming": "订单管理", "quanxian_bianma": "order_manage", "ziyuan_leixing": "menu", "miaoshu": "订单管理菜单权限"},
                {"quanxian_ming": "任务管理", "quanxian_bianma": "task_manage", "ziyuan_leixing": "menu", "miaoshu": "任务管理菜单权限"},
                {"quanxian_ming": "财务管理", "quanxian_bianma": "finance_manage", "ziyuan_leixing": "menu", "miaoshu": "财务管理菜单权限"},
                {"quanxian_ming": "系统设置", "quanxian_bianma": "system_setting", "ziyuan_leixing": "menu", "miaoshu": "系统设置菜单权限"}
            ]
            
            for perm_data in permissions_data:
                existing_perm = db.query(Quanxian).filter(Quanxian.quanxian_bianma == perm_data["quanxian_bianma"]).first()
                if not existing_perm:
                    permission = Quanxian(**perm_data)
                    db.add(permission)
            
            db.commit()
            print("✓ 基础数据初始化成功")
            return True
            
    except Exception as e:
        print(f"✗ 初始化基础数据失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("代理记账营运内部系统 - 数据库初始化")
    print("=" * 50)
    
    # 步骤1：检查并创建数据库
    if not create_database_if_not_exists():
        print("数据库创建失败，退出初始化")
        return False
    
    # 步骤2：创建数据表
    if not create_tables():
        print("数据表创建失败，退出初始化")
        return False
    
    # 步骤3：初始化基础数据
    if not init_basic_data():
        print("基础数据初始化失败，退出初始化")
        return False
    
    print("=" * 50)
    print("✓ 数据库初始化完成！")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
