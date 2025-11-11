"""
合同签署和支付服务
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

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
from schemas.zhifu_guanli import ZhifuTongzhiCreate

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
                from models.xiansuo_guanli.xiansuo import Xiansuo

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
        发起支付
        
        Args:
            sign_token: 签署令牌
            payment_request: 支付请求
            
        Returns:
            dict: 支付信息（包含支付URL或二维码）
        """
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
        
        # 更新支付信息
        hetong.payment_amount = payment_request.payment_amount
        hetong.payment_method = payment_request.payment_method
        hetong.payment_status = "pending"
        hetong.updated_at = datetime.now()
        
        self.db.commit()
        
        # TODO: 集成实际的支付网关
        # 这里返回模拟的支付信息
        payment_info = {
            "payment_url": f"https://pay.example.com/pay/{hetong.id}",
            "qr_code": f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "order_id": hetong.id,
            "amount": payment_request.payment_amount,
            "payment_method": payment_request.payment_method
        }
        
        logger.info(f"为合同 {hetong.hetong_bianhao} 发起支付，金额：{payment_request.payment_amount}")
        
        return payment_info
    
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
                    from models.xiansuo_guanli.xiansuo import Xiansuo
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

        # 更新合同支付信息
        hetong.payment_method = "bank_transfer"
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

