"""
客户管理模块数据模型测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Kehu, FuwuJilu


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestKehuModel:
    """客户模型测试"""
    
    @staticmethod
    def test_create_kehu(db_session):
        """测试创建客户"""
        kehu = Kehu(
            gongsi_mingcheng="测试科技有限公司",
            tongyi_shehui_xinyong_daima="91110000123456789X",
            faren_xingming="张三",
            lianxi_dianhua="010-12345678",
            lianxi_youxiang="contact@test.com"
        )
        
        db_session.add(kehu)
        db_session.commit()
        
        # 验证客户创建成功
        saved_kehu = db_session.query(Kehu).filter(
            Kehu.tongyi_shehui_xinyong_daima == "91110000123456789X"
        ).first()
        assert saved_kehu is not None
        assert saved_kehu.gongsi_mingcheng == "测试科技有限公司"
        assert saved_kehu.faren_xingming == "张三"
        assert saved_kehu.kehu_zhuangtai == "active"
    
    @staticmethod
    def test_kehu_repr(db_session):
        """测试客户字符串表示"""
        kehu = Kehu(
            gongsi_mingcheng="测试科技有限公司",
            tongyi_shehui_xinyong_daima="91110000123456789X",
            faren_xingming="张三",
            kehu_zhuangtai="active"
        )
        
        expected = "<Kehu(gongsi_mingcheng='测试科技有限公司', kehu_zhuangtai='active')>"
        assert repr(kehu) == expected


class TestFuwuJiluModel:
    """服务记录模型测试"""
    
    @staticmethod
    def test_create_fuwu_jilu(db_session):
        """测试创建服务记录"""
        # 先创建客户
        kehu = Kehu(
            gongsi_mingcheng="测试科技有限公司",
            tongyi_shehui_xinyong_daima="91110000123456789X",
            faren_xingming="张三"
        )
        db_session.add(kehu)
        db_session.commit()
        
        # 创建服务记录
        fuwu_jilu = FuwuJilu(
            kehu_id=kehu.id,
            goutong_fangshi="phone",
            goutong_neirong="客户咨询账务处理问题",
            goutong_shijian="2024-03-15 10:00:00",
            wenti_leixing="zhangwu",
            wenti_miaoshu="询问月度账务处理流程"
        )
        
        db_session.add(fuwu_jilu)
        db_session.commit()
        
        # 验证服务记录创建成功
        saved_jilu = db_session.query(FuwuJilu).filter(FuwuJilu.kehu_id == kehu.id).first()
        assert saved_jilu is not None
        assert saved_jilu.goutong_fangshi == "phone"
        assert saved_jilu.wenti_leixing == "zhangwu"
        assert saved_jilu.chuli_zhuangtai == "pending"


class TestKehuFuwuJiluRelation:
    """客户服务记录关联测试"""
    
    @staticmethod
    def test_kehu_fuwu_jilu_relation(db_session):
        """测试客户与服务记录的关联关系"""
        # 创建客户
        kehu = Kehu(
            gongsi_mingcheng="测试科技有限公司",
            tongyi_shehui_xinyong_daima="91110000123456789X",
            faren_xingming="张三"
        )
        db_session.add(kehu)
        db_session.commit()
        
        # 创建多条服务记录
        jilu1 = FuwuJilu(
            kehu_id=kehu.id,
            goutong_fangshi="phone",
            goutong_neirong="第一次沟通",
            goutong_shijian="2024-03-15 10:00:00"
        )
        
        jilu2 = FuwuJilu(
            kehu_id=kehu.id,
            goutong_fangshi="email",
            goutong_neirong="第二次沟通",
            goutong_shijian="2024-03-16 14:00:00"
        )
        
        db_session.add_all([jilu1, jilu2])
        db_session.commit()
        
        # 验证关联关系
        saved_kehu = db_session.query(Kehu).filter(Kehu.id == kehu.id).first()
        assert len(saved_kehu.fuwu_jilu_list) == 2
        
        # 验证反向关联
        saved_jilu = db_session.query(FuwuJilu).filter(FuwuJilu.id == jilu1.id).first()
        assert saved_jilu.kehu.gongsi_mingcheng == "测试科技有限公司"
