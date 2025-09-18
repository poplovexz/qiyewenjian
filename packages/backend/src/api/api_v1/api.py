"""
API v1 路由聚合
"""
from fastapi import APIRouter

# 创建 API 路由器
api_router = APIRouter()

# 导入各个模块的路由
from .endpoints import auth, yonghu
from .endpoints.kehu_guanli import kehu, fuwu_jilu
from .endpoints.yonghu_guanli import jiaose as role_api, quanxian
from .endpoints.chanpin_guanli import chanpin_fenlei, chanpin_xiangmu, chanpin_buzou
from .endpoints.hetong_guanli import hetong_moban, hetong, hetong_yifang_zhuti, hetong_zhifu_fangshi, hetong_qianshu
from .endpoints.xiansuo_guanli import xiansuo, xiansuo_laiyuan, xiansuo_zhuangtai, xiansuo_genjin, xiansuo_baojia
from .endpoints.zhifu_guanli import zhifu_dingdan, zhifu_liushui, zhifu_tongzhi, hetong_zhifu, yinhang_huikuan_danju
from .endpoints.shenhe_guanli import shenhe_guize, shenhe_liucheng, shenhe_jilu

# 注册路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(yonghu.router, prefix="/users", tags=["用户管理"])

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

# 线索管理模块路由
api_router.include_router(xiansuo.router, prefix="/leads", tags=["线索管理"])
api_router.include_router(xiansuo_laiyuan.router, prefix="/lead-sources", tags=["线索来源管理"])
api_router.include_router(xiansuo_zhuangtai.router, prefix="/lead-statuses", tags=["线索状态管理"])
api_router.include_router(xiansuo_genjin.router, prefix="/lead-followups", tags=["线索跟进管理"])
api_router.include_router(xiansuo_baojia.router, prefix="/lead-quotes", tags=["线索报价管理"])

# 支付管理模块路由
api_router.include_router(zhifu_dingdan.router, prefix="/payment-orders", tags=["支付订单管理"])
api_router.include_router(zhifu_liushui.router, prefix="/payment-records", tags=["支付流水管理"])
api_router.include_router(zhifu_tongzhi.router, prefix="/notifications", tags=["支付通知管理"])
api_router.include_router(hetong_zhifu.router, prefix="/contract-payments", tags=["合同支付管理"])
api_router.include_router(yinhang_huikuan_danju.router, prefix="/bank-transfers", tags=["银行汇款单据管理"])

# 审核管理模块路由
api_router.include_router(shenhe_guize.router, prefix="/audit-rules", tags=["审核规则管理"])
api_router.include_router(shenhe_liucheng.router, prefix="/audit-workflows", tags=["审核流程管理"])
api_router.include_router(shenhe_jilu.router, prefix="/audit-records", tags=["审核记录管理"])


@api_router.get("/")
async def api_info() -> dict[str, str]:
    """API 信息"""
    return {"message": "代理记账营运内部系统 API v1", "version": "0.1.0"}
