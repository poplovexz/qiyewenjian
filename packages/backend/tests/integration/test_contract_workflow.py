"""
合同工作流集成测试
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.xiansuo_guanli.xiansuo_service import XiansuoService
from src.services.xiansuo_guanli.xiansuo_baojia_service import XiansuoBaojiaService
from src.services.hetong_guanli.hetong_service import HetongService
from src.services.shenhe_guanli.shenhe_workflow_engine import ShenheWorkflowEngine
from src.services.hetong_guanli.hetong_qianshu_service import HetongQianshuService
from src.services.zhifu_guanli.hetong_zhifu_service import HetongZhifuService
from src.models.shenhe_guanli import ShenheLiucheng
from src.schemas.xiansuo_guanli import XiansuoCreate, XiansuoBaojiaCreate
from src.schemas.hetong_guanli import HetongCreate
from src.schemas.shenhe_guanli import ShenheGuizeCreate


class TestContractWorkflow:
    """合同工作流集成测试"""

    @pytest.fixture
    def db_session(self):
        """获取数据库会话"""
        # PTC-W0063: 添加默认值防止 StopIteration
        db = next(get_db(), None)
        if db is None:
            pytest.skip("无法获取数据库连接")
        yield db
        db.close()

    @pytest.fixture
    def test_user_id(self):
        """测试用户ID"""
        return "test-user-001"

    @pytest.fixture
    def xiansuo_service(self, db_session):
        """线索服务"""
        return XiansuoService(db_session)

    @pytest.fixture
    def baojia_service(self, db_session):
        """报价服务"""
        return XiansuoBaojiaService(db_session)

    @pytest.fixture
    def hetong_service(self, db_session):
        """合同服务"""
        return HetongService(db_session)

    @pytest.fixture
    def workflow_engine(self, db_session):
        """审核工作流引擎"""
        return ShenheWorkflowEngine(db_session)

    @pytest.fixture
    def qianshu_service(self, db_session):
        """合同签署服务"""
        return HetongQianshuService(db_session)

    @pytest.fixture
    def zhifu_service(self, db_session):
        """合同支付服务"""
        return HetongZhifuService(db_session)

    @staticmethod
    async def test_complete_contract_workflow(
        db_session: Session,
        test_user_id: str,
        xiansuo_service: XiansuoService,
        baojia_service: XiansuoBaojiaService,
        hetong_service: HetongService,
        workflow_engine: ShenheWorkflowEngine,
        qianshu_service: HetongQianshuService,
        zhifu_service: HetongZhifuService
    ):
        """测试完整的合同工作流程"""
        
        # 1. 创建线索
        xiansuo_data = XiansuoCreate(
            xiansuo_bianma="TEST-XS-001",
            gongsi_mingcheng="测试公司",
            lianxi_ren="张三",
            lianxi_dianhua="13800138000",
            lianxi_youxiang="zhangsan@test.com",
            hangye_leixing="IT服务",
            gongsi_guimo="50-100人",
            yewu_xuqiu="代理记账服务",
            yuqi_yusuan=Decimal("10000.00"),
            xiansuo_laiyuan_id="test-source-001",
            xiansuo_zhuangtai_id="test-status-001"
        )
        
        xiansuo = xiansuo_service.create_xiansuo(xiansuo_data, test_user_id)
        assert xiansuo is not None
        print(f"✓ 线索创建成功: {xiansuo.xiansuo_bianma}")

        # 2. 创建报价
        baojia_data = XiansuoBaojiaCreate(
            xiansuo_id=xiansuo.id,
            baojia_mingcheng="代理记账服务报价",
            baojia_jine=Decimal("8000.00"),
            youxiao_tianshu=30,
            baojia_neirong="提供专业的代理记账服务",
            chanpin_xiangmu_ids=["test-product-001"]
        )
        
        baojia = baojia_service.create_baojia(baojia_data, test_user_id)
        assert baojia is not None
        print(f"✓ 报价创建成功: {baojia.baojia_mingcheng}")

        # 3. 确认报价
        baojia_service.update_baojia_status(baojia.id, "accepted", test_user_id)
        print("✓ 报价确认成功")

        # 4. 创建审核规则
        audit_rule_data = ShenheGuizeCreate(
            guize_mingcheng="合同金额修改审核规则",
            guize_leixing="hetong_jine_xiuzheng",
            chufa_tiaojian={
                "amount_decrease_percentage": 10,
                "amount_decrease_amount": 1000
            },
            shenhe_liucheng_peizhi={
                "steps": [
                    {
                        "step_name": "主管审核",
                        "approver_role": "supervisor",
                        "required": True
                    }
                ]
            },
            shi_qiyong="Y"
        )
        
        workflow_engine.create_audit_rule(audit_rule_data, test_user_id)
        print("✓ 审核规则创建成功")

        # 5. 生成合同（修改金额触发审核）
        hetong_data = HetongCreate(
            hetong_mingcheng="代理记账服务合同",
            hetong_leixing="service",
            baojia_id=baojia.id,
            hetong_jine=Decimal("7000.00"),  # 低于报价金额，触发审核
            hetong_neirong="代理记账服务合同内容",
            qianding_riqi=datetime.now().date(),
            shengxiao_riqi=datetime.now().date(),
            jieshu_riqi=(datetime.now() + timedelta(days=365)).date()
        )
        
        hetong = hetong_service.create_hetong_from_quote_direct(baojia.id, hetong_data, test_user_id)
        assert hetong is not None
        print(f"✓ 合同创建成功: {hetong.hetong_bianhao}")

        # 6. 检查审核流程是否触发
        audit_workflows = db_session.query(ShenheLiucheng).filter(
            ShenheLiucheng.guanlian_id == hetong.id,
            ShenheLiucheng.shenhe_leixing == "hetong_jine_xiuzheng"
        ).all()
        
        assert len(audit_workflows) > 0
        print("✓ 审核流程触发成功")

        # 7. 模拟审核通过
        for workflow in audit_workflows:
            workflow_engine.process_audit_action(
                workflow.id,
                workflow.dangqian_buzhou_id,
                {
                    "shenhe_jieguo": "tongguo",
                    "shenhe_yijian": "金额调整合理，同意通过"
                },
                test_user_id
            )
        print("✓ 审核流程完成")

        # 8. 创建签署链接
        signing_link = qianshu_service.create_qianshu_lianjie(hetong.id, 7)
        assert signing_link is not None
        print(f"✓ 签署链接创建成功: {signing_link['qianshu_token']}")

        # 9. 模拟签署
        qianshu_data = {
            "qianshu_ren_mingcheng": "张三",
            "qianshu_ren_dianhua": "13800138000",
            "qianshu_ren_youxiang": "zhangsan@test.com",
            "qianming_tupian": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "qianshu_ip": "127.0.0.1",
            "qianshu_shebei": "Test Browser"
        }
        
        success = qianshu_service.process_qianshu(signing_link['qianshu_token'], qianshu_data)
        assert success is True
        print("✓ 合同签署成功")

        # 10. 创建支付订单
        zhifu_data = {
            "hetong_id": hetong.id,
            "zhifu_fangshi": "alipay",
            "zhifu_jine": hetong.hetong_jine,
            "zhifu_beizhu": "代理记账服务费用"
        }
        
        payment = zhifu_service.create_hetong_zhifu(zhifu_data, test_user_id)
        assert payment is not None
        print(f"✓ 支付订单创建成功: {payment.id}")

        # 11. 模拟支付成功
        zhifu_service.update_hetong_zhifu(
            payment.id,
            {
                "zhifu_zhuangtai": "yizhifu",
                "zhifu_liushui_hao": "TEST-PAY-001",
                "zhifu_shijian": datetime.now(),
                "disanfang_dingdan_hao": "ALI-ORDER-001"
            },
            test_user_id
        )
        print("✓ 支付完成")

        # 12. 验证最终状态
        final_hetong = hetong_service.get_hetong_by_id(hetong.id)
        assert final_hetong.hetong_zhuangtai == "yiqianshu"
        
        final_payment = zhifu_service.get_hetong_zhifu_by_id(payment.id)
        assert final_payment.zhifu_zhuangtai == "yizhifu"
        
        print("✓ 完整工作流程测试通过")

    async def test_audit_workflow_rejection(
        self,
        db_session: Session,
        test_user_id: str,
        workflow_engine: ShenheWorkflowEngine
    ):
        """测试审核流程拒绝场景"""
        # TODO: 实现审核拒绝测试
        pass

    async def test_payment_failure_handling(
        self,
        db_session: Session,
        test_user_id: str,
        zhifu_service: HetongZhifuService
    ):
        """测试支付失败处理"""
        # TODO: 实现支付失败测试
        pass

    async def test_signing_expiration(
        self,
        db_session: Session,
        test_user_id: str,
        qianshu_service: HetongQianshuService
    ):
        """测试签署链接过期处理"""
        # TODO: 实现签署过期测试
        pass


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
