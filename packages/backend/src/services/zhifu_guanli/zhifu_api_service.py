"""
第三方支付API服务
集成微信支付和支付宝
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

from models.zhifu_guanli import ZhifuDingdan, ZhifuPeizhi, ZhifuHuidiaoRizhi
from services.zhifu_guanli.zhifu_peizhi_service import ZhifuPeizhiService
from utils.payment.weixin_pay import WeixinPayUtil
from utils.payment.alipay import AlipayUtil
from core.events import publish, EventNames


class ZhifuApiService:
    """第三方支付API服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.peizhi_service = ZhifuPeizhiService(db)
    
    def create_payment(
        self,
        dingdan_id: str,
        zhifu_pingtai: str,
        zhifu_fangshi: str,
        openid: Optional[str] = None,
        return_url: Optional[str] = None,
        quit_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建第三方支付订单
        
        Args:
            dingdan_id: 支付订单ID
            zhifu_pingtai: 支付平台（weixin/zhifubao）
            zhifu_fangshi: 支付方式（jsapi/app/h5/native/page/wap）
            openid: 微信用户openid（JSAPI支付必填）
            return_url: 支付成功返回URL（支付宝必填）
            quit_url: 支付取消返回URL（支付宝可选）
        
        Returns:
            支付参数字典
        """
        # 获取支付订单
        dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        # 检查订单状态
        if dingdan.zhifu_zhuangtai not in ["pending", "failed"]:
            raise HTTPException(
                status_code=400,
                detail=f"订单状态为{dingdan.zhifu_zhuangtai}，无法发起支付"
            )
        
        # 获取支付配置
        peizhi = self.peizhi_service.get_active_config_by_type(zhifu_pingtai)
        if not peizhi:
            raise HTTPException(
                status_code=404,
                detail=f"未找到启用的{zhifu_pingtai}支付配置"
            )
        
        # 更新订单信息
        dingdan.zhifu_peizhi_id = peizhi.id
        dingdan.zhifu_pingtai = zhifu_pingtai
        dingdan.zhifu_fangshi_mingxi = zhifu_fangshi
        dingdan.zhifu_zhuangtai = "paying"
        dingdan.guoqi_shijian = datetime.now() + timedelta(hours=2)  # 2小时后过期
        
        try:
            # 根据支付平台调用不同的支付接口
            if zhifu_pingtai == "weixin":
                result = self._create_weixin_payment(dingdan, peizhi, zhifu_fangshi, openid)
            elif zhifu_pingtai == "zhifubao":
                result = self._create_alipay_payment(dingdan, peizhi, zhifu_fangshi, return_url, quit_url)
            else:
                raise HTTPException(status_code=400, detail="不支持的支付平台")
            
            # 保存第三方订单号
            if "out_trade_no" in result:
                dingdan.disanfang_dingdan_hao = result["out_trade_no"]
            
            # 保存二维码内容（如果有）
            if "code_url" in result:
                dingdan.erweima_neirong = result["code_url"]
            elif "qr_code" in result:
                dingdan.erweima_neirong = result["qr_code"]
            
            self.db.commit()
            self.db.refresh(dingdan)
            
            # 发布支付创建事件
            publish(EventNames.PAYMENT_CREATED, {
                "dingdan_id": dingdan.id,
                "zhifu_pingtai": zhifu_pingtai,
                "zhifu_fangshi": zhifu_fangshi,
                "dingdan_jine": float(dingdan.dingdan_jine)
            })
            
            return {
                "dingdan_id": dingdan.id,
                "dingdan_bianhao": dingdan.dingdan_bianhao,
                "zhifu_pingtai": zhifu_pingtai,
                "zhifu_fangshi": zhifu_fangshi,
                "payment_data": result
            }
            
        except Exception as e:
            # 支付创建失败，恢复订单状态
            dingdan.zhifu_zhuangtai = "failed"
            self.db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"创建支付订单失败: {str(e)}"
            )
    
    def _create_weixin_payment(
        self,
        dingdan: ZhifuDingdan,
        peizhi: Any,
        zhifu_fangshi: str,
        openid: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建微信支付订单"""
        # 初始化微信支付工具
        weixin_pay = WeixinPayUtil(
            appid=peizhi.weixin_appid,
            mchid=peizhi.weixin_shanghu_hao,
            private_key=peizhi.weixin_shanghu_siyao,
            cert_serial_no=peizhi.weixin_zhengshu_xuliehao,
            apiv3_key=peizhi.weixin_api_v3_miyao,
            notify_url=peizhi.tongzhi_url
        )
        
        # 订单参数
        out_trade_no = dingdan.dingdan_bianhao
        description = dingdan.dingdan_mingcheng
        amount = int(float(dingdan.yingfu_jine) * 100)  # 转换为分
        
        # 根据支付方式调用不同的接口
        if zhifu_fangshi == "jsapi":
            if not openid:
                raise HTTPException(status_code=400, detail="JSAPI支付需要提供openid")
            return weixin_pay.create_jsapi_order(out_trade_no, description, amount, openid)
        
        elif zhifu_fangshi == "app":
            return weixin_pay.create_app_order(out_trade_no, description, amount)
        
        elif zhifu_fangshi == "h5":
            return weixin_pay.create_h5_order(out_trade_no, description, amount)
        
        elif zhifu_fangshi == "native":
            return weixin_pay.create_native_order(out_trade_no, description, amount)
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的微信支付方式: {zhifu_fangshi}")
    
    def _create_alipay_payment(
        self,
        dingdan: ZhifuDingdan,
        peizhi: Any,
        zhifu_fangshi: str,
        return_url: Optional[str] = None,
        quit_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建支付宝订单"""
        # 初始化支付宝工具
        alipay = AlipayUtil(
            appid=peizhi.zhifubao_appid,
            app_private_key=peizhi.zhifubao_shanghu_siyao,
            alipay_public_key=peizhi.zhifubao_zhifubao_gongyao,
            notify_url=peizhi.tongzhi_url,
            return_url=return_url
        )
        
        # 订单参数
        out_trade_no = dingdan.dingdan_bianhao
        subject = dingdan.dingdan_mingcheng
        total_amount = float(dingdan.yingfu_jine)
        body = dingdan.dingdan_miaoshu or ""
        
        # 根据支付方式调用不同的接口
        if zhifu_fangshi == "page":
            if not return_url:
                raise HTTPException(status_code=400, detail="网页支付需要提供return_url")
            return alipay.create_page_pay(out_trade_no, subject, total_amount, body)
        
        elif zhifu_fangshi == "wap":
            if not return_url:
                raise HTTPException(status_code=400, detail="手机网页支付需要提供return_url")
            return alipay.create_wap_pay(out_trade_no, subject, total_amount, body, quit_url)
        
        elif zhifu_fangshi == "app":
            return alipay.create_app_pay(out_trade_no, subject, total_amount, body)
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的支付宝支付方式: {zhifu_fangshi}")
    
    def query_payment(self, dingdan_id: str) -> Dict[str, Any]:
        """查询支付订单状态"""
        # 获取支付订单
        dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        if not dingdan.zhifu_peizhi_id or not dingdan.zhifu_pingtai:
            raise HTTPException(status_code=400, detail="订单未发起第三方支付")
        
        # 获取支付配置
        peizhi = self.peizhi_service.get_zhifu_peizhi_detail(dingdan.zhifu_peizhi_id)
        
        try:
            # 根据支付平台查询订单
            if dingdan.zhifu_pingtai == "weixin":
                result = self._query_weixin_payment(dingdan, peizhi)
            elif dingdan.zhifu_pingtai == "zhifubao":
                result = self._query_alipay_payment(dingdan, peizhi)
            else:
                raise HTTPException(status_code=400, detail="不支持的支付平台")
            
            # 更新订单状态
            if result.get("trade_state") == "SUCCESS" or result.get("trade_status") == "TRADE_SUCCESS":
                dingdan.zhifu_zhuangtai = "paid"
                dingdan.shifu_jine = dingdan.yingfu_jine
                dingdan.zhifu_shijian = datetime.now()
                if "transaction_id" in result:
                    dingdan.disanfang_liushui_hao = result["transaction_id"]
                elif "trade_no" in result:
                    dingdan.disanfang_liushui_hao = result["trade_no"]
                self.db.commit()
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"查询支付订单失败: {str(e)}"
            )
    
    def _query_weixin_payment(self, dingdan: ZhifuDingdan, peizhi: Any) -> Dict[str, Any]:
        """查询微信支付订单"""
        weixin_pay = WeixinPayUtil(
            appid=peizhi.weixin_appid,
            mchid=peizhi.weixin_shanghu_hao,
            private_key=peizhi.weixin_shanghu_siyao,
            cert_serial_no=peizhi.weixin_zhengshu_xuliehao,
            apiv3_key=peizhi.weixin_api_v3_miyao,
            notify_url=peizhi.tongzhi_url
        )
        
        return weixin_pay.query_order(dingdan.dingdan_bianhao)
    
    def _query_alipay_payment(self, dingdan: ZhifuDingdan, peizhi: Any) -> Dict[str, Any]:
        """查询支付宝订单"""
        alipay = AlipayUtil(
            appid=peizhi.zhifubao_appid,
            app_private_key=peizhi.zhifubao_shanghu_siyao,
            alipay_public_key=peizhi.zhifubao_zhifubao_gongyao,
            notify_url=peizhi.tongzhi_url
        )
        
        return alipay.query_order(dingdan.dingdan_bianhao)
    
    def close_payment(self, dingdan_id: str) -> Dict[str, Any]:
        """关闭支付订单"""
        # 获取支付订单
        dingdan = self.db.query(ZhifuDingdan).filter(
            ZhifuDingdan.id == dingdan_id,
            ZhifuDingdan.is_deleted == "N"
        ).first()
        
        if not dingdan:
            raise HTTPException(status_code=404, detail="支付订单不存在")
        
        if dingdan.zhifu_zhuangtai == "paid":
            raise HTTPException(status_code=400, detail="订单已支付，无法关闭")
        
        if dingdan.zhifu_zhuangtai == "cancelled":
            raise HTTPException(status_code=400, detail="订单已关闭")
        
        if not dingdan.zhifu_peizhi_id or not dingdan.zhifu_pingtai:
            # 未发起第三方支付，直接关闭
            dingdan.zhifu_zhuangtai = "cancelled"
            self.db.commit()
            return {"message": "订单已关闭"}
        
        # 获取支付配置
        peizhi = self.peizhi_service.get_zhifu_peizhi_detail(dingdan.zhifu_peizhi_id)
        
        try:
            # 根据支付平台关闭订单
            if dingdan.zhifu_pingtai == "weixin":
                result = self._close_weixin_payment(dingdan, peizhi)
            elif dingdan.zhifu_pingtai == "zhifubao":
                result = self._close_alipay_payment(dingdan, peizhi)
            else:
                raise HTTPException(status_code=400, detail="不支持的支付平台")
            
            # 更新订单状态
            dingdan.zhifu_zhuangtai = "cancelled"
            self.db.commit()
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"关闭支付订单失败: {str(e)}"
            )
    
    def _close_weixin_payment(self, dingdan: ZhifuDingdan, peizhi: Any) -> Dict[str, Any]:
        """关闭微信支付订单"""
        weixin_pay = WeixinPayUtil(
            appid=peizhi.weixin_appid,
            mchid=peizhi.weixin_shanghu_hao,
            private_key=peizhi.weixin_shanghu_siyao,
            cert_serial_no=peizhi.weixin_zhengshu_xuliehao,
            apiv3_key=peizhi.weixin_api_v3_miyao,
            notify_url=peizhi.tongzhi_url
        )
        
        return weixin_pay.close_order(dingdan.dingdan_bianhao)
    
    def _close_alipay_payment(self, dingdan: ZhifuDingdan, peizhi: Any) -> Dict[str, Any]:
        """关闭支付宝订单"""
        alipay = AlipayUtil(
            appid=peizhi.zhifubao_appid,
            app_private_key=peizhi.zhifubao_shanghu_siyao,
            alipay_public_key=peizhi.zhifubao_zhifubao_gongyao,
            notify_url=peizhi.tongzhi_url
        )
        
        return alipay.close_order(dingdan.dingdan_bianhao)

