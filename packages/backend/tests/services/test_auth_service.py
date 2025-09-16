"""
认证服务测试
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from src.models import Base, Yonghu, Jiaose, YonghuJiaose
from src.services.yonghu_guanli import AuthService
from src.schemas.yonghu_guanli import LoginRequest
from src.core.security import get_password_hash


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    # 创建角色
    role = Jiaose(
        jiaose_ming="测试角色",
        jiaose_bianma="test_role",
        miaoshu="测试角色描述"
    )
    db_session.add(role)
    db_session.commit()
    
    # 创建用户
    user = Yonghu(
        yonghu_ming="testuser",
        mima=get_password_hash("testpassword"),
        youxiang="test@example.com",
        xingming="测试用户",
        shouji="13800138000",
        zhuangtai="active",
        denglu_cishu="0"
    )
    db_session.add(user)
    db_session.commit()
    
    # 分配角色
    user_role = YonghuJiaose(
        yonghu_id=user.id,
        jiaose_id=role.id
    )
    db_session.add(user_role)
    db_session.commit()
    
    return user


class TestAuthService:
    """认证服务测试类"""
    
    def test_authenticate_user_success(self, db_session, test_user):
        """测试用户认证成功"""
        auth_service = AuthService(db_session)
        
        authenticated_user = auth_service.authenticate_user("testuser", "testpassword")
        
        assert authenticated_user is not None
        assert authenticated_user.yonghu_ming == "testuser"
        assert authenticated_user.youxiang == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """测试用户认证失败 - 密码错误"""
        auth_service = AuthService(db_session)
        
        authenticated_user = auth_service.authenticate_user("testuser", "wrongpassword")
        
        assert authenticated_user is None
    
    def test_authenticate_user_not_exist(self, db_session):
        """测试用户认证失败 - 用户不存在"""
        auth_service = AuthService(db_session)
        
        authenticated_user = auth_service.authenticate_user("nonexistent", "password")
        
        assert authenticated_user is None
    
    def test_login_success(self, db_session, test_user):
        """测试登录成功"""
        auth_service = AuthService(db_session)
        login_data = LoginRequest(yonghu_ming="testuser", mima="testpassword")

        # 记录登录前的次数
        original_count = int(test_user.denglu_cishu)

        result = auth_service.login(login_data)

        assert result["message"] == "登录成功"
        assert result["user"].yonghu_ming == "testuser"
        assert result["token"].token_type == "bearer"
        assert result["token"].access_token is not None
        assert result["token"].refresh_token is not None

        # 验证登录次数更新
        updated_user = db_session.query(Yonghu).filter(Yonghu.id == test_user.id).first()
        assert int(updated_user.denglu_cishu) == original_count + 1
        assert updated_user.zuihou_denglu is not None
    
    def test_login_wrong_credentials(self, db_session, test_user):
        """测试登录失败 - 错误凭据"""
        auth_service = AuthService(db_session)
        login_data = LoginRequest(yonghu_ming="testuser", mima="wrongpassword")
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login(login_data)
        
        assert exc_info.value.status_code == 401
        assert "用户名或密码错误" in str(exc_info.value.detail)
    
    def test_login_inactive_user(self, db_session, test_user):
        """测试登录失败 - 用户已禁用"""
        # 禁用用户
        test_user.zhuangtai = "inactive"
        db_session.commit()
        
        auth_service = AuthService(db_session)
        login_data = LoginRequest(yonghu_ming="testuser", mima="testpassword")
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login(login_data)
        
        assert exc_info.value.status_code == 401
        assert "用户账户已被禁用" in str(exc_info.value.detail)
    
    def test_get_user_roles(self, db_session, test_user):
        """测试获取用户角色"""
        auth_service = AuthService(db_session)
        
        roles = auth_service.get_user_roles(test_user)
        
        assert len(roles) == 1
        assert "test_role" in roles
    
    def test_change_password_success(self, db_session, test_user):
        """测试修改密码成功"""
        auth_service = AuthService(db_session)
        
        result = auth_service.change_password(test_user, "testpassword", "newpassword")
        
        assert result is True
        
        # 验证新密码可以登录
        authenticated_user = auth_service.authenticate_user("testuser", "newpassword")
        assert authenticated_user is not None
        
        # 验证旧密码不能登录
        authenticated_user = auth_service.authenticate_user("testuser", "testpassword")
        assert authenticated_user is None
    
    def test_change_password_wrong_old_password(self, db_session, test_user):
        """测试修改密码失败 - 旧密码错误"""
        auth_service = AuthService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.change_password(test_user, "wrongpassword", "newpassword")
        
        assert exc_info.value.status_code == 400
        assert "旧密码错误" in str(exc_info.value.detail)
