"""
合同签署和支付服务
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.hetong_guanli.hetong import Hetong
from models.zhifu_guanli.hetong_zhifu import HetongZhifu
from models.zhifu_guanli.yinhang_huikuan_danju import YinhangHuikuanDanju
from models.zhifu_guanli.zhifu_tongzhi import ZhifuTongzhi
from models.xiansuo_guanli.xiansuo import Xiansuo
from schemas.hetong_guanli.hetong_schemas import (
    GenerateSignLinkResponse,
    ContractSignInfoResponse,
    CustomerSignRequest,
    CustomerPaymentRequest,
    PaymentCallbackRequest,
    BankPaymentInfoRequest,
    BankPaymentInfoResponse
)

logger = logging.getLogger(__name__)

class HetongSignService:
    """合同签署服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_sign_link(
        self,
        hetong_id: str,
        base_url: str = "http://localhost:5174"
    ) -> GenerateSignLinkResponse:
        """
        生成客户签署链接
        
        Args:
            hetong_id: 合同ID
            base_url: 前端基础URL
            
        Returns:
            GenerateSignLinkResponse: 签署链接信息
        """
        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.id == hetong_id,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        # 检查合同状态（允许draft、approved、active、signed状态生成链接）
        # active状态：审核通过后的合同，可以生成签署链接
        # signed状态：允许重新生成链接，用于客户查看或补充支付
        if hetong.hetong_zhuangtai not in ['draft', 'approved', 'active', 'signed']:
            raise HTTPException(
                status_code=400,
                detail=f"合同状态为{hetong.hetong_zhuangtai}，无法生成签署链接。只有草稿、已审批、已生效或已签署的合同可以生成签署链接。"
            )
        
        # 生成唯一令牌
        sign_token = str(uuid.uuid4())
        
        # 设置过期时间（30天）
        expires_at = datetime.now() + timedelta(days=30)
        
        # 更新合同
        hetong.sign_token = sign_token
        hetong.sign_token_expires_at = expires_at
        hetong.updated_at = datetime.now()
        
        self.db.commit()
        
        # 生成签署链接
        sign_link = f"{base_url}/contract-sign/{sign_token}"
        
        logger.info(f"为合同 {hetong.hetong_bianhao} 生成签署链接: {sign_link}")
        
        return GenerateSignLinkResponse(
            sign_link=sign_link,
            sign_token=sign_token,
            expires_at=expires_at
        )
    
    def get_contract_by_token(self, sign_token: str) -> ContractSignInfoResponse:
        """
        通过签署令牌获取合同信息（无需认证）
        
        Args:
            sign_token: 签署令牌
            
        Returns:
            ContractSignInfoResponse: 合同签署信息
        """
        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")
        
        # 检查链接是否过期
        if hetong.sign_token_expires_at and hetong.sign_token_expires_at < datetime.now():
            raise HTTPException(status_code=400, detail="签署链接已过期")
        
        logger.info(f"获取合同签署信息: {hetong.hetong_bianhao}")
        
        return ContractSignInfoResponse.model_validate(hetong)
    
    def customer_sign_contract(
        self,
        sign_token: str,
        sign_request: CustomerSignRequest,
        client_ip: str
    ) -> ContractSignInfoResponse:
        """
        客户签署合同
        
        Args:
            sign_token: 签署令牌
            sign_request: 签署请求
            client_ip: 客户端IP
            
        Returns:
            ContractSignInfoResponse: 更新后的合同信息
        """
        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")
        
        # 检查链接是否过期
        if hetong.sign_token_expires_at and hetong.sign_token_expires_at < datetime.now():
            raise HTTPException(status_code=400, detail="签署链接已过期")
        
        # 检查是否已签署
        if hetong.signed_at:
            raise HTTPException(status_code=400, detail="合同已签署，无需重复签署")
        
        # 保存签名信息
        hetong.customer_signature = sign_request.signature_data
        hetong.signed_at = datetime.now()
        hetong.qianming_ip = client_ip
        hetong.qianming_beizhu = f"签署人：{sign_request.signer_name}"
        
        if sign_request.signer_phone:
            hetong.qianming_beizhu += f"，电话：{sign_request.signer_phone}"
        if sign_request.signer_email:
            hetong.qianming_beizhu += f"，邮箱：{sign_request.signer_email}"
        
        # 更新合同状态为已签署
        hetong.hetong_zhuangtai = "signed"
        hetong.qianshu_riqi = datetime.now()
        hetong.updated_at = datetime.now()

        # ✅ 自动更新线索状态为"已成交"（通过报价关联）
        if hetong.baojia_id:
            try:
                from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia

                # 通过报价找到线索
                baojia = self.db.query(XiansuoBaojia).filter(
                    XiansuoBaojia.id == hetong.baojia_id,
                    XiansuoBaojia.is_deleted == "N"
                ).first()

                if baojia and baojia.xiansuo_id:
                    xiansuo = self.db.query(Xiansuo).filter(
                        Xiansuo.id == baojia.xiansuo_id,
                        Xiansuo.is_deleted == "N"
                    ).first()

                    if xiansuo and xiansuo.xiansuo_zhuangtai not in ["won", "lost"]:
                        old_status = xiansuo.xiansuo_zhuangtai
                        xiansuo.xiansuo_zhuangtai = "won"  # 已成交
                        xiansuo.shi_zhuanhua = "Y"  # 标记为已转化
                        xiansuo.zhuanhua_shijian = datetime.now()
                        xiansuo.zhuanhua_jine = hetong.payment_amount or 0
                        xiansuo.updated_by = "system"
                        xiansuo.updated_at = datetime.now()

                        # 更新来源的转化统计
                        from models.xiansuo_guanli.xiansuo_laiyuan import XiansuoLaiyuan
                        laiyuan = self.db.query(XiansuoLaiyuan).filter(
                            XiansuoLaiyuan.id == xiansuo.laiyuan_id
                        ).first()

                        if laiyuan:
                            laiyuan.zhuanhua_shuliang = (laiyuan.zhuanhua_shuliang or 0) + 1
                            if laiyuan.xiansuo_shuliang > 0:
                                laiyuan.zhuanhua_lv = (laiyuan.zhuanhua_shuliang / laiyuan.xiansuo_shuliang) * 100

                        logger.info(f"线索状态自动更新：{old_status} → won（合同签署触发）")
            except Exception as e:
                logger.error(f"自动更新线索状态失败: {str(e)}")
                # 不影响主流程

        self.db.commit()
        self.db.refresh(hetong)

        logger.info(f"合同 {hetong.hetong_bianhao} 已被客户签署")

        return ContractSignInfoResponse.model_validate(hetong)
    
    def initiate_payment(
        self,
        sign_token: str,
        payment_request: CustomerPaymentRequest
    ) -> dict:
        """
        发起支付 - 使用支付配置管理模块

        Args:
            sign_token: 签署令牌
            payment_request: 支付请求

        Returns:
            dict: 支付信息（包含支付URL或二维码）
        """
        from models.zhifu_guanli import ZhifuPeizhi, ZhifuDingdan
        from models.hetong_guanli import HetongZhifuFangshi
        from services.zhifu_guanli.zhifu_api_service import ZhifuApiService
        from decimal import Decimal

        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")

        # 检查是否已签署
        if not hetong.signed_at:
            raise HTTPException(status_code=400, detail="请先签署合同")

        # 检查是否已支付
        if hetong.payment_status == "paid":
            raise HTTPException(status_code=400, detail="合同已支付")

        # 检查合同是否有乙方主体
        if not hetong.yifang_zhuti_id:
            raise HTTPException(status_code=400, detail="合同未设置乙方主体，无法支付，请联系业务员")

        # 银行转账不需要调用支付接口
        if payment_request.payment_method == "bank":
            hetong.payment_amount = payment_request.payment_amount
            hetong.payment_method = payment_request.payment_method
            hetong.payment_status = "pending"
            hetong.updated_at = datetime.now()
            self.db.commit()

            logger.info(f"合同 {hetong.hetong_bianhao} 选择银行转账支付")
            return {
                "message": "已确认使用银行转账，我们的业务员会尽快联系您",
                "payment_method": "bank"
            }

        # 规范化与校验支付金额（在线支付场景）
        def sanitize_amount(raw) -> Decimal:
            if raw is None:
                return None
            s = str(raw).strip()
            # 去除中文货币符号与逗号分隔符
            for ch in ["￥", "¥", ",", " "]:
                s = s.replace(ch, "")
            # 仅保留数字和小数点
            import re
            s = "".join(re.findall(r"[0-9.]", s)) or s
            try:
                val = Decimal(s)
                return val
            except Exception:
                return None

        # 优先使用请求中的金额，其次使用合同金额
        normalized_amount = sanitize_amount(payment_request.payment_amount) or sanitize_amount(hetong.payment_amount)
        if not normalized_amount or normalized_amount <= Decimal("0"):
            raise HTTPException(status_code=400, detail="合同金额缺失或不合法，请联系业务员或稍后再试")

        # 根据支付方式查找对应的支付配置
        payment_type_map = {
            "wechat": "weixin",
            "alipay": "zhifubao"
        }

        peizhi_leixing = payment_type_map.get(payment_request.payment_method)
        if not peizhi_leixing:
            raise HTTPException(status_code=400, detail=f"不支持的支付方式: {payment_request.payment_method}")

        # 优先查找该乙方主体关联的支付配置
        logger.info(f"查找乙方主体 {hetong.yifang_zhuti_id} 的支付配置: peizhi_leixing={peizhi_leixing}")
        zhifu_fangshi = self.db.query(HetongZhifuFangshi).join(
            ZhifuPeizhi, HetongZhifuFangshi.zhifu_peizhi_id == ZhifuPeizhi.id
        ).filter(
            HetongZhifuFangshi.yifang_zhuti_id == hetong.yifang_zhuti_id,
            HetongZhifuFangshi.zhifu_zhuangtai == "active",
            HetongZhifuFangshi.is_deleted == "N",
            ZhifuPeizhi.peizhi_leixing == peizhi_leixing,
            ZhifuPeizhi.zhuangtai == "qiyong",
            ZhifuPeizhi.is_deleted == "N"
        ).order_by(
            HetongZhifuFangshi.shi_moren.desc(),  # 优先使用默认支付方式
            HetongZhifuFangshi.paixu.asc()
        ).first()

        zhifu_peizhi = None
        zhifu_fangshi_id = None

        if zhifu_fangshi:
            # 找到了该乙方主体关联的支付配置
            zhifu_peizhi = zhifu_fangshi.zhifu_peizhi
            zhifu_fangshi_id = zhifu_fangshi.id
            logger.info(f"找到乙方主体关联的支付配置: {zhifu_peizhi.peizhi_mingcheng}")
        else:
            # 如果没有找到乙方主体关联的支付配置，则查找全局启用的支付配置
            logger.info("未找到乙方主体关联的支付配置，查找全局启用的支付配置")
            zhifu_peizhi = self.db.query(ZhifuPeizhi).filter(
                ZhifuPeizhi.peizhi_leixing == peizhi_leixing,
                ZhifuPeizhi.zhuangtai == "qiyong",
                ZhifuPeizhi.is_deleted == "N"
            ).order_by(
                # 优先使用生产环境配置
                ZhifuPeizhi.huanjing.desc()
            ).first()

        if not zhifu_peizhi:
            raise HTTPException(
                status_code=400,
                detail=f"未找到可用的{peizhi_leixing}支付配置，请联系管理员配置支付方式"
            )

        logger.info(f"找到支付配置: {zhifu_peizhi.peizhi_mingcheng}, APPID原始值={zhifu_peizhi.zhifubao_appid if peizhi_leixing == 'zhifubao' else zhifu_peizhi.weixin_appid}")
        logger.info(f"私钥原始值前50字符: {(zhifu_peizhi.zhifubao_shanghu_siyao if peizhi_leixing == 'zhifubao' else zhifu_peizhi.weixin_shanghu_siyao)[:50] if (zhifu_peizhi.zhifubao_shanghu_siyao if peizhi_leixing == 'zhifubao' else zhifu_peizhi.weixin_shanghu_siyao) else 'None'}")

        # 解密支付配置中的敏感字段(如果已加密)
        from core.security.encryption import encryption

        def safe_decrypt(value: str) -> str:
            """安全解密,如果解密失败则返回原值(可能是明文)"""
            if not value:
                return value
            try:
                return encryption.decrypt(value)
            except Exception:
                # 解密失败,可能是明文数据,直接返回
                return value

        # 解密支付宝配置
        if peizhi_leixing == "zhifubao":
            if zhifu_peizhi.zhifubao_appid:
                zhifu_peizhi.zhifubao_appid = safe_decrypt(zhifu_peizhi.zhifubao_appid)
                logger.info(f"解密后APPID: {zhifu_peizhi.zhifubao_appid}")
            if zhifu_peizhi.zhifubao_shanghu_siyao:
                zhifu_peizhi.zhifubao_shanghu_siyao = safe_decrypt(zhifu_peizhi.zhifubao_shanghu_siyao)
                logger.info(f"解密后私钥长度: {len(zhifu_peizhi.zhifubao_shanghu_siyao) if zhifu_peizhi.zhifubao_shanghu_siyao else 0}")
                logger.info(f"解密后私钥是否为None: {zhifu_peizhi.zhifubao_shanghu_siyao is None}")
            if zhifu_peizhi.zhifubao_zhifubao_gongyao:
                zhifu_peizhi.zhifubao_zhifubao_gongyao = safe_decrypt(zhifu_peizhi.zhifubao_zhifubao_gongyao)
                logger.info(f"解密后公钥长度: {len(zhifu_peizhi.zhifubao_zhifubao_gongyao) if zhifu_peizhi.zhifubao_zhifubao_gongyao else 0}")

        # 解密微信配置
        elif peizhi_leixing == "weixin":
            if zhifu_peizhi.weixin_appid:
                zhifu_peizhi.weixin_appid = safe_decrypt(zhifu_peizhi.weixin_appid)
            if zhifu_peizhi.weixin_shanghu_hao:
                zhifu_peizhi.weixin_shanghu_hao = safe_decrypt(zhifu_peizhi.weixin_shanghu_hao)
            if zhifu_peizhi.weixin_shanghu_siyao:
                zhifu_peizhi.weixin_shanghu_siyao = safe_decrypt(zhifu_peizhi.weixin_shanghu_siyao)
            if zhifu_peizhi.weixin_zhengshu_xuliehao:
                zhifu_peizhi.weixin_zhengshu_xuliehao = safe_decrypt(zhifu_peizhi.weixin_zhengshu_xuliehao)
            if zhifu_peizhi.weixin_api_v3_miyao:
                zhifu_peizhi.weixin_api_v3_miyao = safe_decrypt(zhifu_peizhi.weixin_api_v3_miyao)

        logger.info(f"支付配置准备完成: {zhifu_peizhi.peizhi_mingcheng}")

        # 创建支付订单，关联乙方主体和支付方式
        zhifu_dingdan = ZhifuDingdan(
            hetong_id=hetong.id,
            kehu_id=hetong.kehu_id,
            yifang_zhuti_id=hetong.yifang_zhuti_id,  # 关联乙方主体
            zhifu_fangshi_id=zhifu_fangshi_id,  # 关联支付方式（如果有）
            dingdan_bianhao=f"HT{hetong.hetong_bianhao}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dingdan_mingcheng=f"合同支付-{hetong.hetong_mingcheng}",
            dingdan_miaoshu=f"合同编号：{hetong.hetong_bianhao}",
            dingdan_jine=normalized_amount,
            yingfu_jine=normalized_amount,
            shifu_jine=Decimal("0"),
            zhifu_leixing=peizhi_leixing,
            zhifu_zhuangtai="pending",
            zhifu_peizhi_id=zhifu_peizhi.id,
            chuangjian_shijian=datetime.now(),
            created_by=hetong.created_by or "system"
        )

        self.db.add(zhifu_dingdan)
        self.db.flush()

        # 使用支付API服务创建支付
        zhifu_api_service = ZhifuApiService(self.db)

        try:
            # 根据支付方式调用不同的支付接口
            # 合同签署页面使用扫码支付（native）
            zhifu_fangshi = "native"

            payment_result = zhifu_api_service.create_payment(
                dingdan_id=zhifu_dingdan.id,
                zhifu_pingtai=peizhi_leixing,
                zhifu_fangshi=zhifu_fangshi
            )

            # 更新合同支付信息 - 存储支付订单ID而不是订单编号
            hetong.payment_amount = str(normalized_amount)
            hetong.payment_method = payment_request.payment_method
            hetong.payment_status = "pending"
            hetong.payment_transaction_id = zhifu_dingdan.id  # 存储支付订单ID，用于后续查询
            hetong.updated_at = datetime.now()

            self.db.commit()

            logger.info(f"为合同 {hetong.hetong_bianhao} 创建支付订单成功，订单号：{zhifu_dingdan.dingdan_bianhao}, 订单ID: {zhifu_dingdan.id}")

            # 提取二维码URL
            qr_code_url = None
            if payment_result.get("payment_data"):
                qr_code_url = payment_result["payment_data"].get("qr_code") or payment_result["payment_data"].get("code_url")

            # 返回支付信息
            return {
                "qr_code": qr_code_url,
                "order_id": zhifu_dingdan.id,
                "order_no": zhifu_dingdan.dingdan_bianhao,
                "amount": str(payment_request.payment_amount),
                "payment_method": payment_request.payment_method,
                "payment_config": zhifu_peizhi.peizhi_mingcheng
            }

        except Exception as e:
            self.db.rollback()
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"创建支付订单失败：{str(e)}")
            logger.error(f"详细错误堆栈：\n{error_detail}")
            raise HTTPException(status_code=500, detail=f"创建支付订单失败：{str(e)}")
    
    def handle_payment_callback(
        self,
        sign_token: str,
        callback_data: PaymentCallbackRequest
    ) -> bool:
        """
        处理支付回调
        
        Args:
            sign_token: 签署令牌
            callback_data: 回调数据
            
        Returns:
            bool: 处理是否成功
        """
        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()
        
        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")
        
        # 更新支付状态
        if callback_data.payment_status == "success":
            hetong.payment_status = "paid"
            hetong.paid_at = callback_data.paid_at
            hetong.payment_transaction_id = callback_data.transaction_id
            hetong.payment_amount = callback_data.paid_amount
            hetong.updated_at = datetime.now()

            # ✅ 自动更新线索状态为"已成交"（如果还未更新）
            if hetong.xiansuo_id:
                try:
                    xiansuo = self.db.query(Xiansuo).filter(
                        Xiansuo.id == hetong.xiansuo_id,
                        Xiansuo.is_deleted == "N"
                    ).first()

                    if xiansuo and xiansuo.xiansuo_zhuangtai != "won":
                        old_status = xiansuo.xiansuo_zhuangtai
                        xiansuo.xiansuo_zhuangtai = "won"  # 已成交
                        xiansuo.shi_zhuanhua = "Y"  # 标记为已转化
                        xiansuo.zhuanhua_shijian = datetime.now()
                        xiansuo.zhuanhua_jine = callback_data.paid_amount
                        xiansuo.updated_by = "system"
                        xiansuo.updated_at = datetime.now()

                        # 更新来源的转化统计（如果还未更新）
                        if old_status != "won":
                            from models.xiansuo_guanli.xiansuo_laiyuan import XiansuoLaiyuan
                            laiyuan = self.db.query(XiansuoLaiyuan).filter(
                                XiansuoLaiyuan.id == xiansuo.laiyuan_id
                            ).first()

                            if laiyuan:
                                laiyuan.zhuanhua_shuliang = (laiyuan.zhuanhua_shuliang or 0) + 1
                                if laiyuan.xiansuo_shuliang > 0:
                                    laiyuan.zhuanhua_lv = (laiyuan.zhuanhua_shuliang / laiyuan.xiansuo_shuliang) * 100

                        logger.info(f"线索状态自动更新：{old_status} → won（支付成功触发）")
                except Exception as e:
                    logger.error(f"自动更新线索状态失败: {str(e)}")
                    # 不影响主流程

            logger.info(f"合同 {hetong.hetong_bianhao} 支付成功，交易号：{callback_data.transaction_id}")
        else:
            hetong.payment_status = "failed"
            hetong.updated_at = datetime.now()

            logger.warning(f"合同 {hetong.hetong_bianhao} 支付失败")

        self.db.commit()

        return True

    def get_payment_status(self, sign_token: str) -> dict:
        """
        查询支付状态 - 主动向支付宝查询最新状态

        Args:
            sign_token: 签署令牌

        Returns:
            dict: 支付状态信息
        """
        from models.zhifu_guanli import ZhifuDingdan
        from services.zhifu_guanli.zhifu_api_service import ZhifuApiService

        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")

        # 如果已经支付成功，直接返回
        if hetong.payment_status == "paid":
            return {
                "payment_status": "paid",
                "payment_method": hetong.payment_method,
                "payment_amount": str(hetong.payment_amount) if hetong.payment_amount else None,
                "paid_at": hetong.paid_at.isoformat() if hetong.paid_at else None,
                "payment_transaction_id": hetong.payment_transaction_id
            }

        # 如果有支付订单ID，主动查询支付宝
        if hetong.payment_transaction_id:
            try:

                # 使用支付订单ID直接查询（payment_transaction_id现在存储的是订单ID）
                zhifu_dingdan = self.db.query(ZhifuDingdan).filter(
                    ZhifuDingdan.id == hetong.payment_transaction_id,
                    ZhifuDingdan.is_deleted == "N"
                ).first()

                if zhifu_dingdan:

                    # 如果订单已经是成功状态，直接更新合同
                    if zhifu_dingdan.zhifu_zhuangtai == "success":
                        hetong.payment_status = "paid"
                        hetong.paid_at = zhifu_dingdan.zhifu_shijian or datetime.now()
                        hetong.updated_at = datetime.now()
                        self.db.commit()

                        return {
                            "payment_status": "paid",
                            "payment_method": hetong.payment_method,
                            "payment_amount": str(hetong.payment_amount) if hetong.payment_amount else None,
                            "paid_at": hetong.paid_at.isoformat() if hetong.paid_at else None,
                            "payment_transaction_id": hetong.payment_transaction_id
                        }

                    # 如果订单不是成功状态（pending、paying等），主动查询支付宝
                    else:
                        zhifu_api_service = ZhifuApiService(self.db)
                        query_result = zhifu_api_service.query_payment(zhifu_dingdan.id)

                        # 从返回结果中提取 trade_status
                        # 支付宝返回格式: {'success': True, 'data': {'trade_status': 'TRADE_SUCCESS'}}
                        trade_status = None
                        if query_result.get("success") and query_result.get("data"):
                            trade_status = query_result["data"].get("trade_status")

                        # 如果查询到支付成功，更新合同状态和支付订单状态
                        if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:

                            # 更新合同状态
                            hetong.payment_status = "paid"
                            hetong.paid_at = datetime.now()
                            hetong.updated_at = datetime.now()

                            # 更新支付订单状态
                            zhifu_dingdan.zhifu_zhuangtai = "paid"
                            zhifu_dingdan.zhifu_shijian = datetime.now()
                            zhifu_dingdan.shifu_jine = zhifu_dingdan.yingfu_jine  # 更新实付金额
                            zhifu_dingdan.updated_at = datetime.now()

                            # 从支付宝返回结果中提取交易号
                            if query_result.get("data"):
                                trade_no = query_result["data"].get("trade_no")
                                if trade_no:
                                    zhifu_dingdan.disanfang_liushui_hao = trade_no

                            self.db.commit()

                            return {
                                "payment_status": "paid",
                                "payment_method": hetong.payment_method,
                                "payment_amount": str(hetong.payment_amount) if hetong.payment_amount else None,
                                "paid_at": hetong.paid_at.isoformat() if hetong.paid_at else None,
                                "payment_transaction_id": hetong.payment_transaction_id
                            }
                        else:
                else:
            except Exception as e:
                logger.error(f"❌ 查询支付状态失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # 查询失败不影响返回当前状态

        # 返回当前数据库中的状态
        result = {
            "payment_status": hetong.payment_status or "pending",
            "payment_method": hetong.payment_method,
            "payment_amount": str(hetong.payment_amount) if hetong.payment_amount else None,
            "paid_at": hetong.paid_at.isoformat() if hetong.paid_at else None,
            "payment_transaction_id": hetong.payment_transaction_id
        }
        return result

    def submit_bank_payment_info(
        self,
        sign_token: str,
        payment_info: BankPaymentInfoRequest
    ) -> BankPaymentInfoResponse:
        """
        客户确认使用银行转账

        客户只需要确认使用银行转账，不需要填写汇款信息
        汇款信息由业务员后续跟踪获取

        Args:
            sign_token: 签署令牌
            payment_info: 空请求（客户只需确认）

        Returns:
            BankPaymentInfoResponse: 提交结果
        """
        # 查询合同
        hetong = self.db.query(Hetong).filter(
            Hetong.sign_token == sign_token,
            Hetong.is_deleted == "N"
        ).first()

        if not hetong:
            raise HTTPException(status_code=404, detail="签署链接无效")

        # 检查链接是否过期
        if hetong.sign_token_expires_at and hetong.sign_token_expires_at < datetime.now():
            raise HTTPException(status_code=400, detail="签署链接已过期")

        # 检查是否已签署
        if not hetong.signed_at:
            raise HTTPException(status_code=400, detail="请先签署合同")

        # 检查是否已有支付记录
        existing_payment = self.db.query(HetongZhifu).filter(
            HetongZhifu.hetong_id == hetong.id,
            HetongZhifu.is_deleted == "N"
        ).first()

        if existing_payment:
            raise HTTPException(status_code=400, detail="该合同已有支付记录")

        # 生成单据编号
        danju_bianhao = f"HK{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"

        # 创建合同支付记录（金额从合同中获取）
        hetong_zhifu = HetongZhifu(
            id=str(uuid.uuid4()),
            hetong_id=hetong.id,
            zhifu_fangshi="bank_transfer",
            zhifu_jine=hetong.payment_amount,  # 从合同获取金额
            zhifu_zhuangtai="pending",
            created_by="customer",
            updated_by="customer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        self.db.add(hetong_zhifu)
        self.db.flush()

        # 查询线索被分配人（业务员）作为上传人
        # 合同 -> 报价 -> 线索
        shangchuan_ren_id = None  # 初始值为 None

        # 优先级1：从线索分配人获取
        if hetong.baojia_id:
            from models.xiansuo_guanli.xiansuo_baojia import XiansuoBaojia
            baojia = self.db.query(XiansuoBaojia).filter(
                XiansuoBaojia.id == hetong.baojia_id,
                XiansuoBaojia.is_deleted == "N"
            ).first()

            if baojia and baojia.xiansuo_id:
                xiansuo = self.db.query(Xiansuo).filter(
                    Xiansuo.id == baojia.xiansuo_id,
                    Xiansuo.is_deleted == "N"
                ).first()

                if xiansuo and xiansuo.fenpei_ren_id:
                    shangchuan_ren_id = xiansuo.fenpei_ren_id
                    logger.info(f"汇款单据分配给线索分配人: {shangchuan_ren_id}")
                elif xiansuo:
                    # 优先级2：线索存在但没有分配人，使用线索创建人
                    shangchuan_ren_id = xiansuo.created_by
                    logger.info(f"线索没有分配人，汇款单据分配给线索创建人: {shangchuan_ren_id}")

        # 优先级3：如果还是没有，使用合同创建人
        if not shangchuan_ren_id:
            shangchuan_ren_id = hetong.created_by
            logger.info(f"未找到线索信息，汇款单据分配给合同创建人: {shangchuan_ren_id}")

        # 创建银行汇款单据记录（客户确认时不填写汇款信息）
        huikuan_danju = YinhangHuikuanDanju(
            id=str(uuid.uuid4()),
            hetong_zhifu_id=hetong_zhifu.id,
            danju_bianhao=danju_bianhao,
            danju_lujing="",  # 等待业务员上传凭证
            huikuan_jine=hetong.payment_amount,  # 从合同获取金额
            huikuan_riqi=datetime.now(),  # 使用当前时间作为默认值
            huikuan_ren="待确认",  # 等待业务员填写
            huikuan_yinhang="待确认",  # 等待业务员填写
            huikuan_zhanghu="待确认",  # 等待业务员填写
            shangchuan_ren_id=shangchuan_ren_id,  # 分配给业务员
            shangchuan_shijian=None,
            shenhe_zhuangtai="waiting_voucher",  # 等待业务员上传凭证
            beizhu="客户已确认使用银行转账",
            created_by="customer",
            updated_by="customer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted="N"
        )
        self.db.add(huikuan_danju)

        # 更新合同支付信息（与可用支付方式标识保持一致）
        hetong.payment_method = "bank"
        hetong.payment_status = "pending"
        hetong.updated_at = datetime.now()

        # 发送通知给业务员
        if shangchuan_ren_id:
            try:
                # 获取客户名称
                kehu_mingcheng = "客户"
                if hetong.kehu_id:
                    from models.kehu_guanli.kehu import Kehu
                    kehu = self.db.query(Kehu).filter(
                        Kehu.id == hetong.kehu_id,
                        Kehu.is_deleted == "N"
                    ).first()
                    if kehu:
                        kehu_mingcheng = kehu.gongsi_mingcheng

                # 创建通知
                tongzhi = ZhifuTongzhi(
                    id=str(uuid.uuid4()),
                    hetong_id=hetong.id,
                    jieshou_ren_id=shangchuan_ren_id,
                    tongzhi_leixing="task_assigned",
                    tongzhi_biaoti="新的银行汇款单据待处理",
                    tongzhi_neirong=f"{kehu_mingcheng}已确认使用银行转账支付，单据编号：{danju_bianhao}，金额：¥{hetong.payment_amount}，请及时上传汇款凭证并填写汇款信息。",
                    tongzhi_zhuangtai="unread",
                    youxian_ji="high",
                    fasong_shijian=datetime.now(),
                    lianjie_url="/payment/bank-transfer-manage",
                    kuozhan_shuju=f'{{"danju_id": "{huikuan_danju.id}", "danju_bianhao": "{danju_bianhao}", "hetong_bianhao": "{hetong.hetong_bianhao}"}}',
                    created_by="system",
                    updated_by="system",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    is_deleted="N"
                )
                self.db.add(tongzhi)
                logger.info(f"已发送通知给业务员 {shangchuan_ren_id}，单据：{danju_bianhao}")
            except Exception as e:
                logger.error(f"发送通知失败: {str(e)}")
                # 通知发送失败不影响主流程
        else:
            logger.warning(f"汇款单据 {danju_bianhao} 无法确定负责人，未发送通知")

        self.db.commit()

        logger.info(f"客户确认使用银行转账，合同：{hetong.hetong_bianhao}，单据：{danju_bianhao}")

        return BankPaymentInfoResponse(
            success=True,
            message="已确认使用银行转账，我们的业务员会尽快联系您获取汇款凭证",
            danju_id=huikuan_danju.id,
            danju_bianhao=danju_bianhao
        )
