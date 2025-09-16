"""
测试配置文件
"""
import pytest
import uuid
from typing import Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.models.yonghu_guanli import Yonghu, Jiaose, Quanxian
from src.core.security import get_password_hash, create_access_token
from src.core.database import Base, get_db
from src.main import app
# 导入所有模型以确保表被创建
from src.models import *


# 创建测试数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    """获取测试数据库会话"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def create_test_user() -> Tuple[dict, str]:
    """创建测试用户并返回用户数据和token"""
    # 创建测试数据库会话
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        # 创建测试用户
        user_data = {
            "yonghu_ming": f"testuser_{uuid.uuid4().hex[:8]}",
            "mima": get_password_hash("testpassword"),
            "youxiang": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "xingming": "测试用户",
            "shouji": "13800138000",
            "zhuangtai": "active",
            "denglu_cishu": 1,
            "created_by": str(uuid.uuid4())
        }

        user = Yonghu(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)

        # 创建访问token
        token = create_access_token(data={"sub": user.yonghu_ming})

        return user_data, token
    finally:
        db.close()


# 覆盖应用的数据库依赖
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 删除所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = Yonghu(
        yonghu_ming="testuser",
        mima=get_password_hash("testpassword"),
        youxiang="test@example.com",
        xingming="测试用户",
        shouji="13800138000",
        zhuangtai="active",
        denglu_cishu=1,
        created_by=str(uuid.uuid4())
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_role(db_session):
    """创建测试角色"""
    role = Jiaose(
        jiaose_ming="测试角色",
        jiaose_bianma="test_role",
        miaoshu="这是一个测试角色",
        zhuangtai="active",
        created_by=str(uuid.uuid4())
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_permission(db_session):
    """创建测试权限"""
    permission = Quanxian(
        quanxian_ming="测试权限",
        quanxian_bianma="test_permission",
        miaoshu="这是一个测试权限",
        ziyuan_leixing="api",
        zhuangtai="active",
        created_by=str(uuid.uuid4())
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission
