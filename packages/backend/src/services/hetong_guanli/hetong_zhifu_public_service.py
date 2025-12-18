"""
合同支付公共服务（无需登录）
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from datetime import datetime
import uuid

from models.hetong_guanli.hetong import Hetong
from models.zhifu_guanli.hetong_zhifu import HetongZhifu
from models.hetong_guanli.hetong_yifang_zhuti import HetongYifangZhuti
from models.kehu_guanli.kehu import Kehu
from core.exceptions import BusinessException


class HetongZhifuPublicService:
    """合同支付公共服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_contract_payment_info(self, contract_id: str) -> Dict[str, Any]:
        """
        获取合同支付信息
        
        Args:
            contract_id: 合同ID
            
        Returns:
            Dict[str, Any]: 合同支付信息
        """
        # 获取合同信息
        contract = self.db.query(Hetong).filter(
            and_(
                Hetong.id == contract_id,
                Hetong.is_deleted == "N"
            )
        ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        # 检查合同是否已签署
        if contract.hetong_zhuangtai != "signed":
            raise HTTPException(status_code=400, detail="只有已签署的合同才能支付")
        
        # 获取客户信息
        customer = self.db.query(Kehu).filter(
            Kehu.id == contract.kehu_id
        ).first()
        
        # 获取支付记录
        payment_records = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.hetong_id == contract_id,
                HetongZhifu.is_deleted == "N"
            )
        ).all()
        
        # 获取银行信息（从乙方主体获取）
        bank_info = {}
        if contract.yifang_zhuti_id:
            yifang_zhuti = self.db.query(HetongYifangZhuti).filter(
                HetongYifangZhuti.id == contract.yifang_zhuti_id
            ).first()
            
            if yifang_zhuti:
                # 这里应该从乙方主体的支付方式中获取银行信息
                # 暂时使用默认银行信息
                bank_info = {
                    "zhanghu_mingcheng": yifang_zhuti.zhuti_mingcheng,
                    "zhanghu_haoma": "1234567890123456789",  # 应该从支付方式表获取
                    "kaihuhang_mingcheng": "中国工商银行"  # 应该从支付方式表获取
                }
        
        return {
            "contract": {
                "id": contract.id,
                "hetong_bianhao": contract.hetong_bianhao,
                "hetong_mingcheng": contract.hetong_mingcheng,
                "hetong_jine": float(contract.hetong_jine) if contract.hetong_jine else 0,
                "hetong_zhuangtai": contract.hetong_zhuangtai,
                "qianshu_riqi": contract.qianshu_riqi.isoformat() if contract.qianshu_riqi else None,
                "kehu": {
                    "id": customer.id if customer else None,
                    "gongsi_mingcheng": customer.gongsi_mingcheng if customer else None
                }
            },
            "payment_records": [
                {
                    "id": record.id,
                    "zhifu_fangshi": record.zhifu_fangshi,
                    "zhifu_jine": float(record.zhifu_jine),
                    "zhifu_zhuangtai": record.zhifu_zhuangtai,
                    "zhifu_liushui_hao": record.zhifu_liushui_hao,
                    "zhifu_shijian": record.zhifu_shijian.isoformat() if record.zhifu_shijian else None
                }
                for record in payment_records
            ],
            "bank_info": bank_info
        }
    
    def create_payment(self, contract_id: str, payment_method: str, amount: float) -> Dict[str, Any]:
        """
        创建支付记录
        
        Args:
            contract_id: 合同ID
            payment_method: 支付方式
            amount: 支付金额
            
        Returns:
            Dict[str, Any]: 创建的支付记录
        """
        # 验证合同
        contract = self.db.query(Hetong).filter(
            and_(
                Hetong.id == contract_id,
                Hetong.is_deleted == "N"
            )
        ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        if contract.hetong_zhuangtai != "signed":
            raise HTTPException(status_code=400, detail="只有已签署的合同才能支付")
        
        # 验证支付金额
        if amount <= 0:
            raise HTTPException(status_code=400, detail="支付金额必须大于0")
        
        contract_amount = float(contract.hetong_jine) if contract.hetong_jine else 0
        if amount > contract_amount:
            raise HTTPException(status_code=400, detail="支付金额不能超过合同金额")
        
        # 创建支付记录
        payment = HetongZhifu(
            hetong_id=contract_id,
            zhifu_fangshi=payment_method,
            zhifu_jine=amount,
            zhifu_zhuangtai="daizhi",
            created_by="public_user"
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        return {
            "id": payment.id,
            "hetong_id": payment.hetong_id,
            "zhifu_fangshi": payment.zhifu_fangshi,
            "zhifu_jine": float(payment.zhifu_jine),
            "zhifu_zhuangtai": payment.zhifu_zhuangtai
        }
    
    def initiate_alipay_payment(self, payment_id: str, return_url: Optional[str] = None, notify_url: Optional[str] = None) -> Dict[str, Any]:
        """
        发起支付宝支付
        
        Args:
            payment_id: 支付记录ID
            return_url: 支付成功返回URL
            notify_url: 支付通知URL
            
        Returns:
            Dict[str, Any]: 支付宝支付信息
        """
        payment = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.id == payment_id,
                HetongZhifu.is_deleted == "N"
            )
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        if payment.zhifu_zhuangtai != "daizhi":
            raise HTTPException(status_code=400, detail="支付记录状态不正确")
        
        # 这里应该调用支付宝SDK生成支付链接
        # 暂时返回模拟数据
        payment_url = f"https://openapi.alipay.com/gateway.do?payment_id={payment_id}"
        
        # 更新支付状态
        payment.zhifu_zhuangtai = "paying"
        payment.disanfang_dingdan_hao = f"alipay_{payment_id}_{int(datetime.now().timestamp())}"
        self.db.commit()
        
        return {
            "payment_url": payment_url,
            "order_no": payment.disanfang_dingdan_hao
        }
    
    def initiate_wechat_payment(self, payment_id: str, notify_url: Optional[str] = None) -> Dict[str, Any]:
        """
        发起微信支付
        
        Args:
            payment_id: 支付记录ID
            notify_url: 支付通知URL
            
        Returns:
            Dict[str, Any]: 微信支付信息
        """
        payment = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.id == payment_id,
                HetongZhifu.is_deleted == "N"
            )
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        if payment.zhifu_zhuangtai != "daizhi":
            raise HTTPException(status_code=400, detail="支付记录状态不正确")
        
        # 这里应该调用微信支付SDK生成二维码
        # 暂时返回模拟数据
        qr_code = f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        # 更新支付状态
        payment.zhifu_zhuangtai = "paying"
        payment.disanfang_dingdan_hao = f"wechat_{payment_id}_{int(datetime.now().timestamp())}"
        self.db.commit()
        
        return {
            "qr_code": qr_code,
            "order_no": payment.disanfang_dingdan_hao
        }
    
    def select_bank_transfer(self, payment_id: str) -> Dict[str, Any]:
        """
        选择银行转账
        
        Args:
            payment_id: 支付记录ID
            
        Returns:
            Dict[str, Any]: 银行转账信息
        """
        payment = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.id == payment_id,
                HetongZhifu.is_deleted == "N"
            )
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        if payment.zhifu_zhuangtai != "daizhi":
            raise HTTPException(status_code=400, detail="支付记录状态不正确")
        
        # 更新支付状态为待确认
        payment.zhifu_zhuangtai = "pending_confirm"
        self.db.commit()
        
        return {
            "message": "银行转账支付方式已选择，请按照银行信息进行转账",
            "status": "pending_confirm"
        }
    
    def download_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        下载合同PDF
        
        Args:
            contract_id: 合同ID
            
        Returns:
            Dict[str, Any]: 文件信息
        """
        contract = self.db.query(Hetong).filter(
            and_(
                Hetong.id == contract_id,
                Hetong.is_deleted == "N"
            )
        ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        if contract.hetong_zhuangtai != "signed":
            raise HTTPException(status_code=400, detail="只有已签署的合同才能下载")
        
        # 这里应该生成或获取合同PDF文件
        # 暂时返回模拟数据
        filename = f"{contract.hetong_bianhao}.pdf"
        content = b"PDF content placeholder"  # 实际应该是PDF文件内容
        
        return {
            "filename": filename,
            "content": content
        }
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        获取支付状态
        
        Args:
            payment_id: 支付记录ID
            
        Returns:
            Dict[str, Any]: 支付状态信息
        """
        payment = self.db.query(HetongZhifu).filter(
            and_(
                HetongZhifu.id == payment_id,
                HetongZhifu.is_deleted == "N"
            )
        ).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        return {
            "id": payment.id,
            "zhifu_zhuangtai": payment.zhifu_zhuangtai,
            "zhifu_jine": float(payment.zhifu_jine),
            "zhifu_fangshi": payment.zhifu_fangshi,
            "zhifu_shijian": payment.zhifu_shijian.isoformat() if payment.zhifu_shijian else None,
            "zhifu_liushui_hao": payment.zhifu_liushui_hao
        }
    
    def handle_alipay_notify(self, notify_data: Dict[str, Any]) -> bool:
        """
        处理支付宝支付通知
        
        Args:
            notify_data: 通知数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 这里应该验证支付宝通知的签名
            # 暂时简化处理
            
            order_no = notify_data.get("out_trade_no")
            trade_status = notify_data.get("trade_status")
            
            if not order_no or not trade_status:
                return False
            
            # 查找支付记录
            payment = self.db.query(HetongZhifu).filter(
                HetongZhifu.disanfang_dingdan_hao == order_no
            ).first()
            
            if not payment:
                return False
            
            # 更新支付状态
            if trade_status == "TRADE_SUCCESS":
                payment.zhifu_zhuangtai = "yizhi"
                payment.zhifu_shijian = datetime.now()
                payment.zhifu_liushui_hao = notify_data.get("trade_no")
            elif trade_status == "TRADE_CLOSED":
                payment.zhifu_zhuangtai = "shibai"
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"处理支付宝通知失败: {e}")
            return False
    
    @staticmethod
    def handle_wechat_notify(notify_data: bytes) -> bool:
        """
        处理微信支付通知
        
        Args:
            notify_data: 通知数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 这里应该解析和验证微信支付通知
            # 暂时简化处理
            
            # 实际应该解析XML或JSON数据
            # 暂时返回True表示处理成功
            return True
            
        except Exception as e:
            print(f"处理微信支付通知失败: {e}")
            return False
