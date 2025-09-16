"""
用户管理 API 测试
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.models.yonghu_guanli import Yonghu
from src.core.security import get_password_hash
from src.core.database import get_db


class TestYonghuAPI:
    """用户管理 API 测试类"""

    @pytest.fixture
    def client(self, db_session: Session):
        """创建测试客户端"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def auth_headers(self, client: TestClient, test_user: Yonghu):
        """获取认证头"""
        # 登录获取 token
        login_data = {
            "yonghu_ming": test_user.yonghu_ming,
            "mima": "testpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_yonghu_success(self, client: TestClient, auth_headers: dict):
        """测试创建用户成功"""
        yonghu_data = {
            "yonghu_ming": "newuser",
            "mima": "password123",
            "youxiang": "newuser@example.com",
            "xingming": "新用户",
            "shouji": "13800138001",
            "zhuangtai": "正常",
            "remark": "测试用户"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=yonghu_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["yonghu_ming"] == "newuser"
        assert data["xingming"] == "新用户"
        assert "mima" not in data  # 密码不应该返回
    
    def test_create_yonghu_duplicate_username(self, client: TestClient, auth_headers: dict, test_user: Yonghu):
        """测试创建重复用户名的用户"""
        yonghu_data = {
            "yonghu_ming": test_user.yonghu_ming,  # 重复用户名
            "mima": "password123",
            "youxiang": "another@example.com",
            "xingming": "另一个用户"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=yonghu_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]
    
    def test_get_yonghu_by_id_success(self, client: TestClient, auth_headers: dict, test_user: Yonghu):
        """测试根据ID获取用户成功"""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["yonghu_ming"] == test_user.yonghu_ming
        assert "mima" not in data  # 密码不应该返回
    
    def test_get_yonghu_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """测试根据ID获取不存在的用户"""
        response = client.get(
            f"/api/v1/users/{str(uuid.uuid4())}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]
    
    def test_get_yonghu_list(self, client: TestClient, auth_headers: dict, test_user: Yonghu):
        """测试获取用户列表"""
        response = client.get(
            "/api/v1/users/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    def test_get_yonghu_list_with_search(self, client: TestClient, auth_headers: dict, test_user: Yonghu):
        """测试搜索用户列表"""
        response = client.get(
            f"/api/v1/users/?search={test_user.yonghu_ming}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        # 验证搜索结果包含目标用户
        found = any(item["yonghu_ming"] == test_user.yonghu_ming for item in data["items"])
        assert found
    
    def test_update_yonghu_success(self, client: TestClient, auth_headers: dict, test_user: Yonghu):
        """测试更新用户成功"""
        update_data = {
            "xingming": "更新后的姓名",
            "shouji": "13900139000",
            "remark": "更新后的备注"
        }
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["xingming"] == "更新后的姓名"
        assert data["shouji"] == "13900139000"
        assert data["remark"] == "更新后的备注"
    
    def test_update_yonghu_not_found(self, client: TestClient, auth_headers: dict):
        """测试更新不存在的用户"""
        update_data = {"xingming": "新姓名"}
        
        response = client.put(
            f"/api/v1/users/{str(uuid.uuid4())}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]
    
    def test_delete_yonghu_success(self, client: TestClient, auth_headers: dict, db_session: Session):
        """测试删除用户成功"""
        # 创建一个新用户用于删除测试
        new_user = Yonghu(
            yonghu_ming="deleteuser",
            mima=get_password_hash("password123"),
            youxiang="delete@example.com",
            xingming="待删除用户",
            shouji="13800138002",
            zhuangtai="active",
            denglu_cishu=0,
            created_by=str(uuid.uuid4())
        )
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
        response = client.delete(
            f"/api/v1/users/{new_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    def test_delete_yonghu_not_found(self, client: TestClient, auth_headers: dict):
        """测试删除不存在的用户"""
        response = client.delete(
            f"/api/v1/users/{str(uuid.uuid4())}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]
    
    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 403
