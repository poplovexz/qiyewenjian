#!/usr/bin/env python3
"""
报价确认流程测试
测试报价确认/拒绝API和事件钩子机制
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.main import app
from src.core.database import get_db
from src.models.xiansuo_guanli.xiansuo import Xiansuo
from src.models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia, XiansuoBaojiaXiangmu
from src.models.xiansuo_guanli.xiansuo_laiyuan import XiansuoLaiyuan
from src.models.yonghu_guanli.yonghu import Yonghu
from src.models.yonghu_guanli.quanxian import Quanxian
from src.models.yonghu_guanli.jiaose import Jiaose
from src.models.yonghu_guanli.jiaose_quanxian import JiaoseQuanxian
from src.models.yonghu_guanli.yonghu_jiaose import YonghuJiaose
from src.core.events import event_bus, EventNames


class TestBaojiaConfirmFlow:
    """报价确认流程测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, test_user: Yonghu):
        """测试设置"""
        self.db = db_session
        self.user = test_user
        self.client = TestClient(app)

        # 创建测试线索来源
        self.laiyuan = XiansuoLaiyuan(
            laiyuan_mingcheng="测试来源",
            laiyuan_bianma="test_source",
            laiyuan_leixing="online",
            miaoshu="测试线索来源",
            zhuangtai="active",
            created_by=self.user.id
        )
        self.db.add(self.laiyuan)
        self.db.commit()
        self.db.refresh(self.laiyuan)

        # 创建测试权限
        self.permission = Quanxian(
            quanxian_ming="报价状态更新权限",
            quanxian_bianma="xiansuo:baojia_status_update",
            miaoshu="允许更新报价状态",
            ziyuan_leixing="api",
            zhuangtai="active",
            created_by=self.user.id
        )
        self.db.add(self.permission)
        self.db.commit()
        self.db.refresh(self.permission)

        # 创建测试角色
        self.role = Jiaose(
            jiaose_ming="测试角色",
            jiaose_bianma="test_role",
            miaoshu="测试角色",
            zhuangtai="active",
            created_by=self.user.id
        )
        self.db.add(self.role)
        self.db.commit()
        self.db.refresh(self.role)

        # 为角色分配权限
        self.role_permission = JiaoseQuanxian(
            jiaose_id=self.role.id,
            quanxian_id=self.permission.id
        )
        self.db.add(self.role_permission)
        self.db.commit()

        # 为用户分配角色
        self.user_role = YonghuJiaose(
            yonghu_id=self.user.id,
            jiaose_id=self.role.id
        )
        self.db.add(self.user_role)
        self.db.commit()

        # 创建测试线索
        self.xiansuo = Xiansuo(
            xiansuo_bianma="XS202412180001",
            gongsi_mingcheng="测试公司",
            lianxi_ren="张三",
            lianxi_dianhua="13800138000",
            lianxi_youxiang="test@example.com",
            hangye_leixing="technology",
            zhiliang_pinggu="high",
            xiansuo_zhuangtai="interested",
            laiyuan_id=self.laiyuan.id,
            created_by=self.user.id
        )
        self.db.add(self.xiansuo)
        self.db.commit()
        self.db.refresh(self.xiansuo)
        
        # 创建测试报价
        self.baojia = XiansuoBaojia(
            xiansuo_id=self.xiansuo.id,
            baojia_bianma="BJ202412180001",
            baojia_mingcheng="测试报价单",
            zongji_jine=5000.00,
            youxiao_qi=datetime.now() + timedelta(days=15),
            baojia_zhuangtai="sent",
            beizhu="测试报价",
            created_by=self.user.id
        )
        self.db.add(self.baojia)
        self.db.commit()
        self.db.refresh(self.baojia)
        
        # 添加报价项目
        self.baojia_xiangmu = XiansuoBaojiaXiangmu(
            baojia_id=self.baojia.id,
            chanpin_xiangmu_id="test-product-1",
            xiangmu_mingcheng="代理记账服务",
            shuliang=1,
            danjia=5000.00,
            danwei="年",
            xiaoji=5000.00,
            paixu=1,
            beizhu="年度代理记账服务"
        )
        self.db.add(self.baojia_xiangmu)
        self.db.commit()
        
        # 获取认证token
        login_response = self.client.post("/api/v1/auth/login", json={
            "yonghu_ming": "testuser",
            "mima": "testpassword"
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # 清空事件历史
        event_bus._event_history.clear()
    
    def test_confirm_baojia_success(self):
        """测试成功确认报价"""
        # 确认报价
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应数据
        assert data["id"] == self.baojia.id
        assert data["baojia_zhuangtai"] == "accepted"
        assert data["queren_ren_id"] == self.user.id
        assert data["queren_shijian"] is not None
        
        # 验证数据库状态
        self.db.refresh(self.baojia)
        assert self.baojia.baojia_zhuangtai == "accepted"
        assert self.baojia.queren_ren_id == self.user.id
        assert self.baojia.queren_shijian is not None
        
        # 验证事件发布
        event_history = event_bus.get_event_history()
        confirm_events = [e for e in event_history if e["event_name"] == EventNames.BAOJIA_CONFIRMED]
        assert len(confirm_events) > 0
        
        confirm_event = confirm_events[-1]
        assert confirm_event["payload"]["baojia_id"] == self.baojia.id
        assert confirm_event["payload"]["xiansuo_id"] == self.xiansuo.id
        assert confirm_event["payload"]["queren_ren_id"] == self.user.id
        
        # 验证线索状态联动
        self.db.refresh(self.xiansuo)
        assert self.xiansuo.xiansuo_zhuangtai == "quoted"
    
    def test_reject_baojia_success(self):
        """测试成功拒绝报价"""
        # 拒绝报价
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/reject",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应数据
        assert data["id"] == self.baojia.id
        assert data["baojia_zhuangtai"] == "rejected"
        assert data["queren_ren_id"] == self.user.id
        assert data["queren_shijian"] is not None
        
        # 验证数据库状态
        self.db.refresh(self.baojia)
        assert self.baojia.baojia_zhuangtai == "rejected"
        assert self.baojia.queren_ren_id == self.user.id
        assert self.baojia.queren_shijian is not None
        
        # 验证事件发布
        event_history = event_bus.get_event_history()
        reject_events = [e for e in event_history if e["event_name"] == EventNames.BAOJIA_REJECTED]
        assert len(reject_events) > 0
        
        reject_event = reject_events[-1]
        assert reject_event["payload"]["baojia_id"] == self.baojia.id
        assert reject_event["payload"]["xiansuo_id"] == self.xiansuo.id
        assert reject_event["payload"]["queren_ren_id"] == self.user.id
    
    def test_confirm_baojia_invalid_status(self):
        """测试确认已确认的报价（无效状态）"""
        # 先确认报价
        self.baojia.baojia_zhuangtai = "accepted"
        self.db.commit()
        
        # 尝试再次确认
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm",
            headers=self.headers
        )
        
        assert response.status_code == 400
        assert "无法确认" in response.json()["detail"]
    
    def test_confirm_expired_baojia(self):
        """测试确认过期报价"""
        # 设置报价为过期
        self.baojia.youxiao_qi = datetime.now() - timedelta(days=1)
        self.db.commit()
        
        # 尝试确认过期报价
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm",
            headers=self.headers
        )
        
        assert response.status_code == 400
        assert "已过期" in response.json()["detail"]
    
    def test_confirm_nonexistent_baojia(self):
        """测试确认不存在的报价"""
        response = self.client.post(
            "/api/v1/lead-quotes/nonexistent-id/confirm",
            headers=self.headers
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_confirm_without_permission(self):
        """测试无权限确认报价"""
        # 不提供认证头
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm"
        )
        
        assert response.status_code == 401
    
    def test_event_handlers_execution(self):
        """测试事件处理器执行"""
        # 确认报价
        response = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm",
            headers=self.headers
        )
        
        assert response.status_code == 200
        
        # 验证合同草稿触发事件
        event_history = event_bus.get_event_history()
        draft_events = [e for e in event_history if e["event_name"] == EventNames.HETONG_DRAFT_TRIGGERED]
        assert len(draft_events) > 0
        
        draft_event = draft_events[-1]
        assert draft_event["payload"]["baojia_id"] == self.baojia.id
        assert draft_event["payload"]["trigger_reason"] == "baojia_confirmed"
    
    def test_multiple_baojia_status_flow(self):
        """测试多个报价的状态流转"""
        # 创建第二个报价
        baojia2 = XiansuoBaojia(
            xiansuo_id=self.xiansuo.id,
            baojia_bianma="BJ202412180002",
            baojia_mingcheng="测试报价单2",
            zongji_jine=8000.00,
            youxiao_qi=datetime.now() + timedelta(days=20),
            baojia_zhuangtai="draft",
            beizhu="第二个测试报价",
            created_by=self.user.id
        )
        self.db.add(baojia2)
        self.db.commit()
        self.db.refresh(baojia2)
        
        # 确认第一个报价
        response1 = self.client.post(
            f"/api/v1/lead-quotes/{self.baojia.id}/confirm",
            headers=self.headers
        )
        assert response1.status_code == 200
        
        # 拒绝第二个报价
        response2 = self.client.post(
            f"/api/v1/lead-quotes/{baojia2.id}/reject",
            headers=self.headers
        )
        assert response2.status_code == 200
        
        # 验证状态
        self.db.refresh(self.baojia)
        self.db.refresh(baojia2)
        assert self.baojia.baojia_zhuangtai == "accepted"
        assert baojia2.baojia_zhuangtai == "rejected"
        
        # 验证线索状态（应该是quoted，因为有确认的报价）
        self.db.refresh(self.xiansuo)
        assert self.xiansuo.xiansuo_zhuangtai == "quoted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
