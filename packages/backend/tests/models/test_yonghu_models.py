"""
用户管理模块数据模型测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Yonghu, Jiaose, Quanxian, YonghuJiaose


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestYonghuModel:
    """用户模型测试"""
    
    def test_create_yonghu(self, db_session):
        """测试创建用户"""
        yonghu = Yonghu(
            yonghu_ming="test_user",
            mima="hashed_password",
            youxiang="test@example.com",
            xingming="测试用户",
            shouji="13800138000"
        )
        
        db_session.add(yonghu)
        db_session.commit()
        
        # 验证用户创建成功
        saved_yonghu = db_session.query(Yonghu).filter(Yonghu.yonghu_ming == "test_user").first()
        assert saved_yonghu is not None
        assert saved_yonghu.youxiang == "test@example.com"
        assert saved_yonghu.xingming == "测试用户"
        assert saved_yonghu.zhuangtai == "active"
    
    def test_yonghu_repr(self, db_session):
        """测试用户字符串表示"""
        yonghu = Yonghu(
            yonghu_ming="test_user",
            mima="hashed_password",
            youxiang="test@example.com",
            xingming="测试用户"
        )
        
        expected = "<Yonghu(yonghu_ming='test_user', xingming='测试用户')>"
        assert repr(yonghu) == expected


class TestJiaoseModel:
    """角色模型测试"""
    
    def test_create_jiaose(self, db_session):
        """测试创建角色"""
        jiaose = Jiaose(
            jiaose_ming="管理员",
            jiaose_bianma="admin",
            miaoshu="系统管理员角色"
        )
        
        db_session.add(jiaose)
        db_session.commit()
        
        # 验证角色创建成功
        saved_jiaose = db_session.query(Jiaose).filter(Jiaose.jiaose_bianma == "admin").first()
        assert saved_jiaose is not None
        assert saved_jiaose.jiaose_ming == "管理员"
        assert saved_jiaose.zhuangtai == "active"


class TestQuanxianModel:
    """权限模型测试"""
    
    def test_create_quanxian(self, db_session):
        """测试创建权限"""
        quanxian = Quanxian(
            quanxian_ming="用户管理",
            quanxian_bianma="user_manage",
            ziyuan_leixing="menu",
            ziyuan_lujing="/user/manage"
        )
        
        db_session.add(quanxian)
        db_session.commit()
        
        # 验证权限创建成功
        saved_quanxian = db_session.query(Quanxian).filter(Quanxian.quanxian_bianma == "user_manage").first()
        assert saved_quanxian is not None
        assert saved_quanxian.quanxian_ming == "用户管理"
        assert saved_quanxian.ziyuan_leixing == "menu"


class TestYonghuJiaoseRelation:
    """用户角色关联测试"""
    
    def test_yonghu_jiaose_relation(self, db_session):
        """测试用户角色关联关系"""
        # 创建用户
        yonghu = Yonghu(
            yonghu_ming="test_user",
            mima="hashed_password",
            youxiang="test@example.com",
            xingming="测试用户"
        )
        db_session.add(yonghu)
        
        # 创建角色
        jiaose = Jiaose(
            jiaose_ming="管理员",
            jiaose_bianma="admin"
        )
        db_session.add(jiaose)
        db_session.commit()
        
        # 创建用户角色关联
        yonghu_jiaose = YonghuJiaose(
            yonghu_id=yonghu.id,
            jiaose_id=jiaose.id
        )
        db_session.add(yonghu_jiaose)
        db_session.commit()
        
        # 验证关联关系
        saved_relation = db_session.query(YonghuJiaose).first()
        assert saved_relation is not None
        assert saved_relation.yonghu_id == yonghu.id
        assert saved_relation.jiaose_id == jiaose.id
