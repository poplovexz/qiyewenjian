"""
API v1 路由聚合
"""
from fastapi import APIRouter

# 创建 API 路由器
api_router = APIRouter()

# 导入各个模块的路由
from .endpoints import auth, yonghu, upload
from .endpoints.kehu_guanli import kehu, fuwu_jilu
from .endpoints.yonghu_guanli import jiaose as role_api, quanxian, user_settings
from .endpoints.xitong_guanli import system_config
from .endpoints.chanpin_guanli import chanpin_fenlei, chanpin_xiangmu, chanpin_buzou
from .endpoints.hetong_guanli import hetong_moban, hetong, hetong_yifang_zhuti, hetong_zhifu_fangshi, hetong_qianshu, hetong_generate, hetong_qianshu_public, hetong_zhifu_public, hetong_sign
from .endpoints.xiansuo_guanli import xiansuo, xiansuo_laiyuan, xiansuo_zhuangtai, xiansuo_genjin, xiansuo_baojia
from .endpoints.zhifu_guanli import zhifu_dingdan, zhifu_liushui, zhifu_tongzhi, hetong_zhifu, yinhang_huikuan_danju, zhifu_peizhi, zhifu_api, zhifu_huidiao, zhifu_tuikuan
from .endpoints.shenhe_guanli import shenhe_guize, rule_test, approval_matrix, payment_audit
from .endpoints.caiwu_guanli import kaipiao, chengben, caiwu_shezhi
from .endpoints.fuwu_guanli import fuwu_gongdan, task_items
from .endpoints.heguishixiang_guanli import heguishixiang_moban
from .endpoints import audit_workflows, audit_records
from .endpoints.bangong_guanli import baoxiao, qingjia, duiwai_fukuan, caigou, gongzuo_jiaojie
from .endpoints.deploy import deploy, deploy_config

# 注册路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(yonghu.router, prefix="/users", tags=["用户管理"])
api_router.include_router(user_settings.router, prefix="/users", tags=["个人设置"])
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

# 用户管理模块路由
api_router.include_router(role_api.router, prefix="/user-management/roles", tags=["角色管理"])
api_router.include_router(quanxian.router, prefix="/user-management/permissions", tags=["权限管理"])

# 客户管理模块路由
api_router.include_router(kehu.router, prefix="/customers", tags=["客户管理"])
api_router.include_router(fuwu_jilu.router, prefix="/service-records", tags=["服务记录管理"])

# 产品管理模块路由
api_router.include_router(chanpin_fenlei.router, prefix="/product-management/categories", tags=["产品分类管理"])
api_router.include_router(chanpin_xiangmu.router, prefix="/product-management/products", tags=["产品项目管理"])
api_router.include_router(chanpin_buzou.router, prefix="/product-management", tags=["产品步骤管理"])

# 合同管理模块路由
api_router.include_router(hetong_moban.router, prefix="/contract-templates", tags=["合同模板管理"])
api_router.include_router(hetong.router, prefix="/contracts", tags=["合同管理"])
api_router.include_router(hetong_yifang_zhuti.router, prefix="/contract-parties", tags=["合同乙方主体管理"])
api_router.include_router(hetong_zhifu_fangshi.router, prefix="/contract-payment-methods", tags=["合同支付方式管理"])
api_router.include_router(hetong_qianshu.router, prefix="/contract-signing", tags=["合同签署管理"])
api_router.include_router(hetong_generate.router, prefix="/contract-generate", tags=["合同生成"])

# 公共API（无需登录）
api_router.include_router(hetong_qianshu_public.router, prefix="/public/contract-signing", tags=["合同签署公共接口"])
api_router.include_router(hetong_zhifu_public.router, prefix="/public/contract-payment", tags=["合同支付公共接口"])
api_router.include_router(hetong_sign.router, prefix="/contract-sign", tags=["合同客户签署"])
api_router.include_router(zhifu_huidiao.router, prefix="/public/payment-callback", tags=["支付回调接口"])

# 线索管理模块路由
api_router.include_router(xiansuo.router, prefix="/leads", tags=["线索管理"])
api_router.include_router(xiansuo_laiyuan.router, prefix="/lead-sources", tags=["线索来源管理"])
api_router.include_router(xiansuo_zhuangtai.router, prefix="/lead-statuses", tags=["线索状态管理"])
api_router.include_router(xiansuo_genjin.router, prefix="/lead-followups", tags=["线索跟进管理"])
api_router.include_router(xiansuo_baojia.router, prefix="/lead-quotes", tags=["线索报价管理"])

# 支付管理模块路由
api_router.include_router(zhifu_peizhi.router, prefix="/payment-configs", tags=["支付配置管理"])
api_router.include_router(zhifu_api.router, prefix="/payment-api", tags=["第三方支付API"])
api_router.include_router(zhifu_dingdan.router, prefix="/payment-orders", tags=["支付订单管理"])
api_router.include_router(zhifu_tuikuan.router, prefix="/payment-refunds", tags=["退款管理"])
api_router.include_router(zhifu_liushui.router, prefix="/payment-records", tags=["支付流水管理"])
api_router.include_router(zhifu_tongzhi.router, prefix="/notifications", tags=["支付通知管理"])
api_router.include_router(hetong_zhifu.router, prefix="/contract-payments", tags=["合同支付管理"])
api_router.include_router(yinhang_huikuan_danju.router, prefix="/bank-transfers", tags=["银行汇款单据管理"])

# 审核管理模块路由 - 重新启用审核规则API
api_router.include_router(shenhe_guize.router, prefix="/audit-rules", tags=["审核规则管理"])
# api_router.include_router(shenhe_liucheng.router, prefix="/audit-workflows-old", tags=["审核流程管理(旧)"])
# api_router.include_router(shenhe_jilu.router, prefix="/audit-records-old", tags=["审核记录管理(旧)"])

# 新的审核管理API
api_router.include_router(audit_workflows.router, prefix="/audit-workflows", tags=["审核工作流"])
api_router.include_router(audit_records.router, prefix="/audit-records", tags=["审核记录"])
api_router.include_router(rule_test.router, prefix="/audit-rules/test", tags=["规则测试"])
api_router.include_router(approval_matrix.router, prefix="/approval-matrix", tags=["审批权责矩阵"])
api_router.include_router(payment_audit.router, prefix="/payment-audit", tags=["支付订单审核"])

# 财务管理模块
api_router.include_router(kaipiao.router, prefix="/invoices", tags=["开票申请"])
api_router.include_router(chengben.router, prefix="/costs", tags=["成本记录"])
api_router.include_router(caiwu_shezhi.router, prefix="/finance-settings", tags=["财务设置"])

# 服务管理模块
api_router.include_router(fuwu_gongdan.router, prefix="/service-orders", tags=["服务工单管理"])
api_router.include_router(task_items.router, prefix="/task-items", tags=["任务项管理"])

# 合规事项管理
api_router.include_router(heguishixiang_moban.router, prefix="/compliance/templates", tags=["合规事项模板管理"])

# 办公管理模块
api_router.include_router(baoxiao.router, prefix="/office/reimbursement", tags=["报销申请管理"])
api_router.include_router(qingjia.router, prefix="/office/leave", tags=["请假申请管理"])
api_router.include_router(duiwai_fukuan.router, prefix="/office/payment", tags=["对外付款申请管理"])
api_router.include_router(caigou.router, prefix="/office/procurement", tags=["采购申请管理"])
api_router.include_router(gongzuo_jiaojie.router, prefix="/office/handover", tags=["工作交接单管理"])

# 系统管理模块
api_router.include_router(system_config.router, prefix="/system", tags=["系统配置管理"])

# 部署管理模块
api_router.include_router(deploy.router, prefix="/deploy", tags=["部署管理"])
api_router.include_router(deploy_config.router, prefix="/deploy", tags=["部署配置"])


@api_router.get("/")
async def api_info() -> dict[str, str]:
    """API 信息"""
    return {"message": "代理记账营运内部系统 API v1", "version": "0.1.0"}
