"""
认证 API 测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models import Base, Yonghu, Jiaose, YonghuJiaose
from src.core.database import get_db
from src.core.security import get_password_hash


# 创建测试数据库
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user():
    """创建测试用户"""
    db = TestingSessionLocal()
    
    # 创建角色
    role = Jiaose(
        jiaose_ming="测试角色",
        jiaose_bianma="test_role",
        miaoshu="测试角色描述"
    )
    db.add(role)
    db.commit()
    
    # 创建用户
    user = Yonghu(
        yonghu_ming="testuser",
        mima=get_password_hash("testpassword"),
        youxiang="test@example.com",
        xingming="测试用户",
        shouji="13800138000",
        zhuangtai="active"
    )
    db.add(user)
    db.commit()
    
    # 分配角色
    user_role = YonghuJiaose(
        yonghu_id=user.id,
        jiaose_id=role.id
    )
    db.add(user_role)
    db.commit()
    
    yield user
    
    # 清理
    db.delete(user_role)
    db.delete(user)
    db.delete(role)
    db.commit()
    db.close()


class TestAuthAPI:
    """认证 API 测试类"""
    
    def test_login_success(self, client, test_user):
        """测试登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "登录成功"
        assert data["user"]["yonghu_ming"] == "testuser"
        assert data["user"]["youxiang"] == "test@example.com"
        assert data["token"]["token_type"] == "bearer"
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
    
    def test_login_wrong_credentials(self, client, test_user):
        """测试登录失败 - 错误凭据"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]
    
    def test_login_missing_fields(self, client):
        """测试登录失败 - 缺少字段"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser"
                # 缺少 mima 字段
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_current_user_success(self, client, test_user):
        """测试获取当前用户信息成功"""
        # 先登录获取令牌
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "testpassword"
            }
        )
        
        token = login_response.json()["token"]["access_token"]
        
        # 使用令牌获取用户信息
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["yonghu_ming"] == "testuser"
        assert data["youxiang"] == "test@example.com"
        assert data["xingming"] == "测试用户"
        assert isinstance(data["roles"], list)
        assert isinstance(data["permissions"], list)
    
    def test_get_current_user_no_token(self, client):
        """测试获取当前用户信息失败 - 无令牌"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden
    
    def test_get_current_user_invalid_token(self, client):
        """测试获取当前用户信息失败 - 无效令牌"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_change_password_success(self, client, test_user):
        """测试修改密码成功"""
        # 先登录获取令牌
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "testpassword"
            }
        )
        
        token = login_response.json()["token"]["access_token"]
        
        # 修改密码
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "testpassword",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "密码修改成功"
    
    def test_change_password_mismatch(self, client, test_user):
        """测试修改密码失败 - 密码不匹配"""
        # 先登录获取令牌
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "testpassword"
            }
        )
        
        token = login_response.json()["token"]["access_token"]
        
        # 修改密码
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "testpassword",
                "new_password": "newpassword123",
                "confirm_password": "differentpassword"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "新密码与确认密码不匹配" in response.json()["detail"]
    
    def test_logout(self, client, test_user):
        """测试登出"""
        # 先登录获取令牌
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "yonghu_ming": "testuser",
                "mima": "testpassword"
            }
        )
        
        token = login_response.json()["token"]["access_token"]
        
        # 登出
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"
