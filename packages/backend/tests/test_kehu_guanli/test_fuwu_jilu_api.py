"""
服务记录管理 API 测试
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.conftest import create_test_user


client = TestClient(app)


@pytest.fixture
def test_customer_data():
    """测试客户数据"""
    return {
        "gongsi_mingcheng": "测试服务记录公司",
        "tongyi_shehui_xinyong_daima": "91110000123456789Y",
        "faren_xingming": "李四",
        "kehu_zhuangtai": "active"
    }


@pytest.fixture
def test_service_record_data():
    """测试服务记录数据"""
    return {
        "goutong_fangshi": "phone",
        "goutong_neirong": "客户咨询发票开具问题",
        "goutong_shijian": "2024-01-15 10:30:00",
        "wenti_leixing": "zhangwu",
        "wenti_miaoshu": "客户需要开具增值税专用发票",
        "chuli_zhuangtai": "pending"
    }


class TestFuwuJiluAPI:
    """服务记录管理 API 测试类"""
    
    def test_create_service_record_success(self, test_customer_data, test_service_record_data):
        """测试创建服务记录成功"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        # 创建服务记录
        test_service_record_data["kehu_id"] = customer_id
        response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["kehu_id"] == customer_id
        assert data["goutong_fangshi"] == test_service_record_data["goutong_fangshi"]
        assert data["goutong_neirong"] == test_service_record_data["goutong_neirong"]
        assert data["chuli_zhuangtai"] == test_service_record_data["chuli_zhuangtai"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_service_record_customer_not_found(self, test_service_record_data):
        """测试创建服务记录时客户不存在"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 使用不存在的客户ID
        test_service_record_data["kehu_id"] = "nonexistent-customer-id"
        response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        
        assert response.status_code == 404
        assert "客户不存在" in response.json()["detail"]
    
    def test_create_service_record_invalid_data(self):
        """测试创建服务记录时数据验证失败"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 缺少必填字段
        invalid_data = {
            "kehu_id": "some-id",
            "goutong_fangshi": "invalid_method",  # 无效的沟通方式
            "goutong_neirong": "",  # 空内容
            "goutong_shijian": ""  # 空时间
        }
        
        response = client.post(
            "/api/v1/service-records/",
            json=invalid_data,
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_get_service_record_list(self, test_customer_data, test_service_record_data):
        """测试获取服务记录列表"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        
        # 获取服务记录列表
        response = client.get("/api/v1/service-records/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 1
    
    def test_get_service_record_list_with_filters(self, test_customer_data, test_service_record_data):
        """测试带筛选条件的服务记录列表"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        
        # 按客户ID筛选
        response = client.get(
            "/api/v1/service-records/",
            params={"kehu_id": customer_id},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["kehu_id"] == customer_id for item in data["items"])
        
        # 按沟通方式筛选
        response = client.get(
            "/api/v1/service-records/",
            params={"goutong_fangshi": "phone"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["goutong_fangshi"] == "phone" for item in data["items"])
    
    def test_get_service_record_detail(self, test_customer_data, test_service_record_data):
        """测试获取服务记录详情"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        record_response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        record_id = record_response.json()["id"]
        
        # 获取服务记录详情
        response = client.get(f"/api/v1/service-records/{record_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == record_id
        assert data["kehu_id"] == customer_id
    
    def test_update_service_record(self, test_customer_data, test_service_record_data):
        """测试更新服务记录"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        record_response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        record_id = record_response.json()["id"]
        
        # 更新服务记录
        update_data = {
            "goutong_neirong": "更新后的沟通内容",
            "chuli_zhuangtai": "processing",
            "chuli_jieguo": "正在处理中"
        }
        
        response = client.put(
            f"/api/v1/service-records/{record_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["goutong_neirong"] == update_data["goutong_neirong"]
        assert data["chuli_zhuangtai"] == update_data["chuli_zhuangtai"]
        assert data["chuli_jieguo"] == update_data["chuli_jieguo"]
    
    def test_update_service_record_status(self, test_customer_data, test_service_record_data):
        """测试更新服务记录处理状态"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        record_response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        record_id = record_response.json()["id"]
        
        # 更新处理状态
        response = client.patch(
            f"/api/v1/service-records/{record_id}/status",
            params={
                "new_status": "completed",
                "chuli_jieguo": "问题已解决"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["chuli_zhuangtai"] == "completed"
        assert data["chuli_jieguo"] == "问题已解决"
    
    def test_get_customer_service_records(self, test_customer_data, test_service_record_data):
        """测试获取客户的服务记录"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        
        # 获取客户的服务记录
        response = client.get(
            f"/api/v1/service-records/kehu/{customer_id}/records",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["kehu_id"] == customer_id for item in data["items"])
    
    def test_delete_service_record(self, test_customer_data, test_service_record_data):
        """测试删除服务记录"""
        user_data, token = create_test_user()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建客户和服务记录
        customer_response = client.post(
            "/api/v1/customers/",
            json=test_customer_data,
            headers=headers
        )
        customer_id = customer_response.json()["id"]
        
        test_service_record_data["kehu_id"] = customer_id
        record_response = client.post(
            "/api/v1/service-records/",
            json=test_service_record_data,
            headers=headers
        )
        record_id = record_response.json()["id"]
        
        # 删除服务记录
        response = client.delete(f"/api/v1/service-records/{record_id}", headers=headers)
        
        assert response.status_code == 200
        assert "删除成功" in response.json()["message"]
        
        # 验证服务记录已被软删除
        get_response = client.get(f"/api/v1/service-records/{record_id}", headers=headers)
        assert get_response.status_code == 404
