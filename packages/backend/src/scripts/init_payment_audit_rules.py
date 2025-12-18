"""
初始化支付审核规则脚本
"""
import json
from sqlalchemy.orm import Session
from core.database import get_db
from models.shenhe_guanli import ShenheGuize


def create_payment_audit_rules(db: Session):
    """创建支付审核规则"""
    
    # 大额支付审核规则
    large_payment_rule = ShenheGuize(
        guize_mingcheng="大额支付审核",
        guize_leixing="zhifu_shenhe",
        guize_miaoshu="金额超过10万元的支付需要审核",
        chufa_tiaojian=json.dumps({
            "amount_threshold": {
                "value": 100000,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "财务经理审核",
                    "role": "finance_manager",
                    "required": True,
                    "condition": "",
                    "expected_time": 24
                },
                {
                    "step": 2,
                    "name": "财务总监审核",
                    "role": "cfo",
                    "required": True,
                    "condition": "amount >= 500000",
                    "expected_time": 48
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["email", "system"],
            "escalation_hours": 72
        }),
        paixu=1,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )
    
    # 银行转账审核规则
    bank_transfer_rule = ShenheGuize(
        guize_mingcheng="银行转账审核",
        guize_leixing="zhifu_shenhe",
        guize_miaoshu="所有银行转账支付需要审核",
        chufa_tiaojian=json.dumps({
            "payment_types": ["yinhangzhuanzhang"]
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "财务专员审核",
                    "role": "finance_specialist",
                    "required": True,
                    "condition": "",
                    "expected_time": 12
                },
                {
                    "step": 2,
                    "name": "财务经理审核",
                    "role": "finance_manager",
                    "required": True,
                    "condition": "amount >= 50000",
                    "expected_time": 24
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["system"],
            "escalation_hours": 48
        }),
        paixu=2,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )
    
    # 现金支付审核规则
    cash_payment_rule = ShenheGuize(
        guize_mingcheng="现金支付审核",
        guize_leixing="zhifu_shenhe",
        guize_miaoshu="现金支付超过1万元需要审核",
        chufa_tiaojian=json.dumps({
            "payment_types": ["xianjin"],
            "amount_threshold": {
                "value": 10000,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "部门主管审核",
                    "role": "supervisor",
                    "required": True,
                    "condition": "",
                    "expected_time": 8
                },
                {
                    "step": 2,
                    "name": "财务经理审核",
                    "role": "finance_manager",
                    "required": True,
                    "condition": "amount >= 50000",
                    "expected_time": 24
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["system"],
            "escalation_hours": 24
        }),
        paixu=3,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )
    
    # 特殊客户支付审核规则
    special_customer_rule = ShenheGuize(
        guize_mingcheng="特殊客户支付审核",
        guize_leixing="zhifu_shenhe",
        guize_miaoshu="特殊客户的所有支付需要额外审核",
        chufa_tiaojian=json.dumps({
            "customer_types": ["vip", "high_risk"],
            "amount_threshold": {
                "value": 1000,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "客户经理审核",
                    "role": "account_manager",
                    "required": True,
                    "condition": "",
                    "expected_time": 12
                },
                {
                    "step": 2,
                    "name": "风控专员审核",
                    "role": "risk_control",
                    "required": True,
                    "condition": "",
                    "expected_time": 24
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["email", "system", "sms"],
            "escalation_hours": 36
        }),
        paixu=4,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )
    
    # 检查规则是否已存在
    existing_rules = db.query(ShenheGuize).filter(
        ShenheGuize.guize_leixing == "zhifu_shenhe",
        ShenheGuize.is_deleted == "N"
    ).all()
    
    if existing_rules:
        print("支付审核规则已存在，跳过创建")
        return
    
    # 添加规则到数据库
    rules = [large_payment_rule, bank_transfer_rule, cash_payment_rule, special_customer_rule]
    
    for rule in rules:
        db.add(rule)
    
    db.commit()
    
    print(f"成功创建 {len(rules)} 个支付审核规则")
    for rule in rules:
        print(f"- {rule.guize_mingcheng}")


def create_flow_audit_rules(db: Session):
    """创建支付流水审核规则"""

    # 大额流水审核规则
    large_flow_rule = ShenheGuize(
        guize_mingcheng="大额流水审核",
        guize_leixing="liushui_shenhe",
        guize_miaoshu="交易金额超过5万元的流水需要审核",
        chufa_tiaojian=json.dumps({
            "amount_threshold": {
                "value": 50000,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "财务专员审核",
                    "role": "finance_specialist",
                    "required": True,
                    "condition": "",
                    "expected_time": 12
                },
                {
                    "step": 2,
                    "name": "财务经理审核",
                    "role": "finance_manager",
                    "required": True,
                    "condition": "amount >= 200000",
                    "expected_time": 24
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["system"],
            "escalation_hours": 48
        }),
        paixu=1,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )

    # 退款流水审核规则
    refund_flow_rule = ShenheGuize(
        guize_mingcheng="退款流水审核",
        guize_leixing="liushui_shenhe",
        guize_miaoshu="所有退款流水需要审核",
        chufa_tiaojian=json.dumps({
            "flow_types": ["refund"]
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "客服主管审核",
                    "role": "customer_service_manager",
                    "required": True,
                    "condition": "",
                    "expected_time": 8
                },
                {
                    "step": 2,
                    "name": "财务经理审核",
                    "role": "finance_manager",
                    "required": True,
                    "condition": "",
                    "expected_time": 24
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["email", "system"],
            "escalation_hours": 36
        }),
        paixu=2,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )

    # 银行转账流水审核规则
    bank_flow_rule = ShenheGuize(
        guize_mingcheng="银行转账流水审核",
        guize_leixing="liushui_shenhe",
        guize_miaoshu="银行转账流水超过1万元需要审核",
        chufa_tiaojian=json.dumps({
            "payment_methods": ["yinhangzhuanzhang"],
            "amount_threshold": {
                "value": 10000,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "财务专员审核",
                    "role": "finance_specialist",
                    "required": True,
                    "condition": "",
                    "expected_time": 12
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["system"],
            "escalation_hours": 24
        }),
        paixu=3,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )

    # 手续费流水审核规则
    fee_flow_rule = ShenheGuize(
        guize_mingcheng="手续费流水审核",
        guize_leixing="liushui_shenhe",
        guize_miaoshu="手续费流水超过500元需要审核",
        chufa_tiaojian=json.dumps({
            "flow_types": ["fee"],
            "amount_threshold": {
                "value": 500,
                "operator": ">="
            }
        }),
        shenhe_liucheng_peizhi=json.dumps({
            "steps": [
                {
                    "step": 1,
                    "name": "财务专员审核",
                    "role": "finance_specialist",
                    "required": True,
                    "condition": "",
                    "expected_time": 8
                }
            ]
        }),
        dongzuo_peizhi=json.dumps({
            "auto_assign": True,
            "notification_methods": ["system"],
            "escalation_hours": 24
        }),
        paixu=4,
        shi_qiyong="Y",
        chuangjian_ren="system",
        is_deleted="N"
    )

    # 检查规则是否已存在
    existing_rules = db.query(ShenheGuize).filter(
        ShenheGuize.guize_leixing == "liushui_shenhe",
        ShenheGuize.is_deleted == "N"
    ).all()

    if existing_rules:
        print("支付流水审核规则已存在，跳过创建")
        return

    # 添加规则到数据库
    rules = [large_flow_rule, refund_flow_rule, bank_flow_rule, fee_flow_rule]

    for rule in rules:
        db.add(rule)

    db.commit()

    print(f"成功创建 {len(rules)} 个支付流水审核规则")
    for rule in rules:
        print(f"- {rule.guize_mingcheng}")


def main():
    """主函数"""
    # PTC-W0063: 使用 next() 的默认值防止 StopIteration
    db = next(get_db(), None)
    if db is None:
        print("无法获取数据库连接")
        return
    try:
        create_payment_audit_rules(db)
        create_flow_audit_rules(db)
        print("支付审核规则初始化完成")
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
