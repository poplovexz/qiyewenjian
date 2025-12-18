"""线索管理权限相关 API 测试"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.redis_client import redis_client
from src.core.security import get_password_hash
from src.main import app
from src.models import (
    Jiaose,
    JiaoseQuanxian,
    Quanxian,
    Yonghu,
    YonghuJiaose,
)


class TestXiansuoPermissionsAPI:
    """线索管理权限校验"""

    @pytest.fixture
    def client(self, db_session: Session, monkeypatch) -> TestClient:
        """组合测试客户端并禁用 Redis"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        monkeypatch.setattr(redis_client, "_connected", False)
        monkeypatch.setattr(redis_client, "redis", None)
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @staticmethod
    def _create_user(db_session: Session, username: str) -> Yonghu:
        user = Yonghu(
            yonghu_ming=username,
            mima=get_password_hash("testpassword"),
            youxiang=f"{username}@example.com",
            xingming="测试用户",
            shouji="13800138000",
            zhuangtai="active",
            denglu_cishu="0",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def _attach_permission(db_session: Session, user: Yonghu, permission_code: str) -> None:
        role = Jiaose(
            jiaose_ming=f"角色-{permission_code}",
            jiaose_bianma=f"role_{uuid.uuid4().hex[:6]}",
            zhuangtai="active",
        )
        permission = Quanxian(
            quanxian_ming=permission_code,
            quanxian_bianma=permission_code,
            ziyuan_leixing="api",
            zhuangtai="active",
        )
        db_session.add(role)
        db_session.add(permission)
        db_session.commit()

        user_role = YonghuJiaose(yonghu_id=user.id, jiaose_id=role.id)
        role_permission = JiaoseQuanxian(jiaose_id=role.id, quanxian_id=permission.id)
        db_session.add(user_role)
        db_session.add(role_permission)
        db_session.commit()

    @staticmethod
    def _login(client: TestClient, username: str) -> dict:
        response = client.post(
            "/api/v1/auth/login",
            json={"yonghu_ming": username, "mima": "testpassword"},
        )
        assert response.status_code == 200
        token = response.json()["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_leads_without_permission_forbidden(self, client: TestClient, db_session: Session):
        user = self._create_user(db_session, "noperm")
        headers = self._login(client, user.yonghu_ming)

        response = client.get("/api/v1/leads/", headers=headers)
        assert response.status_code == 403
        assert "权限不足" in response.json()["detail"]

    def test_get_leads_with_permission_success(self, client: TestClient, db_session: Session):
        user = self._create_user(db_session, "withperm")
        self._attach_permission(db_session, user, "xiansuo:read")
        headers = self._login(client, user.yonghu_ming)

        response = client.get("/api/v1/leads/", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["page"] == 1
        assert payload["items"] == []
