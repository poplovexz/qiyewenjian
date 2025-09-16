"""
客户管理 API 测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.models.kehu_guanli import Kehu
from tests.conftest import create_test_user


client = TestClient(app)


@pytest.fixture
def test_customer_data():
    """测试客户数据"""
    return {
        "gongsi_mingcheng": "测试科技有限公司",
        "tongyi_shehui_xinyong_daima": "91110000123456789X",
        "chengli_riqi": "2020-01-01T00:00:00",
        "zhuce_dizhi": "北京市朝阳区测试路123号",
        "faren_xingming": "张三",
        "faren_shenfenzheng": "110101199001011234",
        "faren_lianxi": "13800138000",
        "lianxi_dianhua": "010-12345678",
        "lianxi_youxiang": "test@example.com",
        "lianxi_dizhi": "北京市朝阳区联系地址456号",
        "kehu_zhuangtai": "active",
        "fuwu_kaishi_riqi": "2024-01-01T00:00:00"
    }


class TestKehuAPI:
    """客户管理 API 测试类"""
    
    def test_create_customer_success(self, test_customer_data):
        """测试创建客户成功"""
        # 创建测试用户并获取token
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建客户
        response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["gongsi_mingcheng"] == test_customer_data["gongsi_mingcheng"]
        assert data["tongyi_shehui_xinyong_daima"] == test_customer_data["tongyi_shehui_xinyong_daima"]
        assert data["kehu_zhuangtai"] == test_customer_data["kehu_zhuangtai"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_customer_duplicate_credit_code(self, test_customer_data):
        """测试创建客户时统一社会信用代码重复"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 第一次创建
        response1 = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        assert response1.status_code == 200
        
        # 第二次创建相同信用代码的客户
        response2 = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        assert response2.status_code == 400
        assert "统一社会信用代码已存在" in response2.json()["detail"]
    
    def test_create_customer_invalid_data(self):
        """测试创建客户时数据验证失败"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 缺少必填字段
        invalid_data = {
            "gongsi_mingcheng": "",  # 空字符串
            "tongyi_shehui_xinyong_daima": "invalid",  # 格式错误
            "faren_xingming": ""  # 空字符串
        }
        
        response = client.post(
            "/api/v1/customers/",
            json=invalid_data,
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_get_customer_list(self, test_customer_data):
        """测试获取客户列表"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        
        # 获取客户列表
        response = client.get("/api/v1/customers/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 1
    
    def test_get_customer_list_with_search(self, test_customer_data):
        """测试搜索客户列表"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        
        # 搜索客户
        response = client.get(
            "/api/v1/customers/",
            params={"search": "测试科技"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert "测试科技" in data["items"][0]["gongsi_mingcheng"]
    
    def test_get_customer_detail(self, test_customer_data):
        """测试获取客户详情"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        create_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = create_response.json()["id"]
        
        # 获取客户详情
        response = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["gongsi_mingcheng"] == test_customer_data["gongsi_mingcheng"]
    
    def test_get_customer_detail_not_found(self):
        """测试获取不存在的客户详情"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/customers/nonexistent-id", headers=headers)
        
        assert response.status_code == 404
        assert "客户不存在" in response.json()["detail"]
    
    def test_update_customer(self, test_customer_data):
        """测试更新客户信息"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        create_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = create_response.json()["id"]
        
        # 更新客户信息
        update_data = {
            "gongsi_mingcheng": "更新后的公司名称",
            "lianxi_dianhua": "010-87654321"
        }
        
        response = client.put(
            f"/api/v1/customers/{customer_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["gongsi_mingcheng"] == update_data["gongsi_mingcheng"]
        assert data["lianxi_dianhua"] == update_data["lianxi_dianhua"]
    
    def test_update_customer_status(self, test_customer_data):
        """测试更新客户状态"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        create_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = create_response.json()["id"]
        
        # 更新客户状态
        response = client.patch(
            f"/api/v1/customers/{customer_id}/status",
            params={"new_status": "renewing"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["kehu_zhuangtai"] == "renewing"
    
    def test_delete_customer(self, test_customer_data):
        """测试删除客户"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建一个客户
        create_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = create_response.json()["id"]
        
        # 删除客户
        response = client.delete(f"/api/v1/customers/{customer_id}", headers=headers)
        
        assert response.status_code == 200
        assert "删除成功" in response.json()["message"]
        
        # 验证客户已被软删除
        get_response = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_unauthorized_access(self, test_customer_data):
        """测试未授权访问"""
        # 不提供token
        response = client.post("/api/v1/customers/", json=test_customer_data)
        assert response.status_code == 401
        
        response = client.get("/api/v1/customers/")
        assert response.status_code == 401
