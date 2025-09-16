"""
用户管理服务测试
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.services.yonghu_guanli.yonghu_service import YonghuService
from src.schemas.yonghu_guanli import YonghuCreate, YonghuUpdate
from src.models.yonghu_guanli import Yonghu, Jiaose, YonghuJiaose
from src.models.yonghu_guanli import Yonghu, Jiaose, YonghuJiaose
from src.core.security import get_password_hash


class TestYonghuService:
    """用户管理服务测试类"""
    
    def test_create_yonghu_success(self, db_session: Session):
        """测试创建用户成功"""
        yonghu_service = YonghuService(db_session)
        
        yonghu_data = YonghuCreate(
            yonghu_ming="newuser",
            mima="password123",
            youxiang="newuser@example.com",
            xingming="新用户",
            shouji="13800138001",
            zhuangtai="正常",
            remark="测试用户"
        )
        
        result = yonghu_service.create_yonghu(yonghu_data, str(uuid.uuid4()))
        
        assert result.yonghu_ming == "newuser"
        assert result.youxiang == "newuser@example.com"
        assert result.xingming == "新用户"
        assert result.shouji == "13800138001"
        assert result.zhuangtai == "正常"
        
        # 验证密码已加密
        db_user = db_session.query(Yonghu).filter(Yonghu.id == result.id).first()
        assert db_user.mima != "password123"
    
    def test_create_yonghu_duplicate_username(self, db_session: Session, test_user: Yonghu):
        """测试创建用户时用户名重复"""
        yonghu_service = YonghuService(db_session)
        
        yonghu_data = YonghuCreate(
            yonghu_ming="testuser",  # 与测试用户重复
            mima="password123",
            youxiang="another@example.com",
            xingming="另一个用户"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            yonghu_service.create_yonghu(yonghu_data, str(uuid.uuid4()))
        
        assert exc_info.value.status_code == 400
        assert "用户名已存在" in str(exc_info.value.detail)
    
    def test_create_yonghu_duplicate_email(self, db_session: Session, test_user: Yonghu):
        """测试创建用户时邮箱重复"""
        yonghu_service = YonghuService(db_session)
        
        yonghu_data = YonghuCreate(
            yonghu_ming="newuser",
            mima="password123",
            youxiang="test@example.com",  # 与测试用户重复
            xingming="新用户"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            yonghu_service.create_yonghu(yonghu_data, str(uuid.uuid4()))
        
        assert exc_info.value.status_code == 400
        assert "邮箱已存在" in str(exc_info.value.detail)
    
    def test_get_yonghu_by_id_success(self, db_session: Session, test_user: Yonghu):
        """测试根据ID获取用户成功"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.get_yonghu_by_id(test_user.id)
        
        assert result is not None
        assert result.id == test_user.id
        assert result.yonghu_ming == test_user.yonghu_ming
        assert result.xingming == test_user.xingming
    
    def test_get_yonghu_by_id_not_found(self, db_session: Session):
        """测试根据ID获取用户不存在"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.get_yonghu_by_id(str(uuid.uuid4()))
        
        assert result is None
    
    def test_get_yonghu_list(self, db_session: Session, test_user: Yonghu):
        """测试获取用户列表"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.get_yonghu_list(skip=0, limit=10)
        
        assert result.total >= 1
        assert len(result.items) >= 1
        assert result.page == 1
        assert result.size == 10
        
        # 验证包含测试用户
        user_ids = [item.id for item in result.items]
        assert test_user.id in user_ids
    
    def test_get_yonghu_list_with_search(self, db_session: Session, test_user: Yonghu):
        """测试搜索用户列表"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.get_yonghu_list(skip=0, limit=10, search="testuser")
        
        assert result.total >= 1
        assert len(result.items) >= 1
        
        # 验证搜索结果包含测试用户
        user_names = [item.yonghu_ming for item in result.items]
        assert "testuser" in user_names
    
    def test_get_yonghu_list_with_status_filter(self, db_session: Session, test_user: Yonghu):
        """测试按状态筛选用户列表"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.get_yonghu_list(skip=0, limit=10, zhuangtai="正常")
        
        # 验证所有返回的用户状态都是"正常"
        for item in result.items:
            assert item.zhuangtai == "正常"
    
    def test_update_yonghu_success(self, db_session: Session, test_user: Yonghu):
        """测试更新用户成功"""
        yonghu_service = YonghuService(db_session)
        
        update_data = YonghuUpdate(
            xingming="更新后的姓名",
            shouji="13900139000",
            remark="更新后的备注"
        )
        
        result = yonghu_service.update_yonghu(test_user.id, update_data, str(uuid.uuid4()))
        
        assert result.xingming == "更新后的姓名"
        assert result.shouji == "13900139000"
        assert result.remark == "更新后的备注"
        assert result.yonghu_ming == test_user.yonghu_ming  # 未更新的字段保持不变
    
    def test_update_yonghu_not_found(self, db_session: Session):
        """测试更新不存在的用户"""
        yonghu_service = YonghuService(db_session)
        
        update_data = YonghuUpdate(xingming="新姓名")
        
        with pytest.raises(HTTPException) as exc_info:
            yonghu_service.update_yonghu(str(uuid.uuid4()), update_data, str(uuid.uuid4()))
        
        assert exc_info.value.status_code == 404
        assert "用户不存在" in str(exc_info.value.detail)
    
    def test_delete_yonghu_success(self, db_session: Session, test_user: Yonghu):
        """测试删除用户成功"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.delete_yonghu(test_user.id, str(uuid.uuid4()))
        
        assert result is True
        
        # 验证用户已被软删除
        db_user = db_session.query(Yonghu).filter(Yonghu.id == test_user.id).first()
        assert db_user.is_deleted == 'Y'
    
    def test_delete_yonghu_not_found(self, db_session: Session):
        """测试删除不存在的用户"""
        yonghu_service = YonghuService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            yonghu_service.delete_yonghu(str(uuid.uuid4()), str(uuid.uuid4()))
        
        assert exc_info.value.status_code == 404
        assert "用户不存在" in str(exc_info.value.detail)
    
    def test_assign_roles_success(self, db_session: Session, test_user: Yonghu, test_role: Jiaose):
        """测试分配角色成功"""
        yonghu_service = YonghuService(db_session)
        
        result = yonghu_service.assign_roles(test_user.id, [test_role.id], str(uuid.uuid4()))
        
        assert result is True
        
        # 验证角色关联已创建
        user_role = db_session.query(YonghuJiaose).filter(
            YonghuJiaose.yonghu_id == test_user.id,
            YonghuJiaose.jiaose_id == test_role.id
        ).first()
        assert user_role is not None
    
    def test_get_yonghu_roles(self, db_session: Session, test_user: Yonghu, test_role: Jiaose):
        """测试获取用户角色列表"""
        yonghu_service = YonghuService(db_session)
        
        # 先分配角色
        yonghu_service.assign_roles(test_user.id, [test_role.id], str(uuid.uuid4()))
        
        # 获取角色列表
        result = yonghu_service.get_yonghu_roles(test_user.id)
        
        assert len(result) == 1
        assert result[0].id == test_role.id
        assert result[0].jiaose_ming == test_role.jiaose_ming
