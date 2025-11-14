"""
支付宝支付工具类
封装支付宝支付API的常用功能
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 由于alipay-sdk-python的导入问题，暂时使用占位实现
# 实际使用时需要根据SDK文档正确导入
try:
    from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
    from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
    ALIPAY_SDK_AVAILABLE = True
except ImportError:
    logger.warning("支付宝SDK未正确安装，支付宝支付功能将不可用")
    ALIPAY_SDK_AVAILABLE = False


class AlipayUtil:
    """支付宝支付工具类"""

    def __init__(
        self,
        appid: str,
        app_private_key: str,
        alipay_public_key: str,
        notify_url: str,
        return_url: Optional[str] = None,
        debug: bool = False
    ):
        """
        初始化支付宝支付工具

        Args:
            appid: 支付宝APPID
            app_private_key: 支付宝商户私钥
            alipay_public_key: 支付宝公钥
            notify_url: 支付回调通知URL
            return_url: 支付成功返回URL
            debug: 是否为沙箱环境
        """
        self.appid = appid
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key
        self.notify_url = notify_url
        self.return_url = return_url
        self.debug = debug

        # 初始化支付宝客户端
        self.alipay = None
        if ALIPAY_SDK_AVAILABLE:
            self._init_client()
        else:
            logger.warning("支付宝SDK不可用，支付功能将受限")
    
    def _init_client(self):
        """初始化支付宝客户端"""
        if not ALIPAY_SDK_AVAILABLE:
            return

        try:
            self.alipay = AliPay(
                appid=self.appid,
                app_notify_url=self.notify_url,
                app_private_key_string=self.app_private_key,
                alipay_public_key_string=self.alipay_public_key,
                sign_type="RSA2",
                debug=self.debug
            )
            logger.info(f"支付宝客户端初始化成功，APPID：{self.appid}")
        except Exception as e:
            logger.error(f"支付宝客户端初始化失败：{str(e)}")
            raise
    
    def create_page_pay(
        self,
        out_trade_no: str,
        subject: str,
        total_amount: float,
        body: Optional[str] = None,
        return_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建网页支付订单（电脑网站支付）
        
        Args:
            out_trade_no: 商户订单号
            subject: 订单标题
            total_amount: 订单金额（单位：元）
            body: 订单描述
            return_url: 同步回调地址
            
        Returns:
            支付URL字符串
        """
        try:
            order_string = self.alipay.api_alipay_trade_page_pay(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                body=body,
                return_url=return_url
            )
            
            # 构建完整的支付URL
            if self.debug:
                pay_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}"
            else:
                pay_url = f"https://openapi.alipay.com/gateway.do?{order_string}"
            
            logger.info(f"网页支付订单创建成功：{out_trade_no}")
            return {
                'success': True,
                'data': {
                    'pay_url': pay_url,
                    'order_string': order_string
                },
                'message': '订单创建成功'
            }
        except Exception as e:
            logger.error(f"网页支付订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def create_wap_pay(
        self,
        out_trade_no: str,
        subject: str,
        total_amount: float,
        body: Optional[str] = None,
        return_url: Optional[str] = None,
        quit_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建手机网站支付订单
        
        Args:
            out_trade_no: 商户订单号
            subject: 订单标题
            total_amount: 订单金额（单位：元）
            body: 订单描述
            return_url: 同步回调地址
            quit_url: 用户付款中途退出返回商户网站的地址
            
        Returns:
            支付URL字符串
        """
        try:
            order_string = self.alipay.api_alipay_trade_wap_pay(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                body=body,
                return_url=return_url,
                quit_url=quit_url
            )
            
            # 构建完整的支付URL
            if self.debug:
                pay_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}"
            else:
                pay_url = f"https://openapi.alipay.com/gateway.do?{order_string}"
            
            logger.info(f"手机网站支付订单创建成功：{out_trade_no}")
            return {
                'success': True,
                'data': {
                    'pay_url': pay_url,
                    'order_string': order_string
                },
                'message': '订单创建成功'
            }
        except Exception as e:
            logger.error(f"手机网站支付订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def create_app_pay(
        self,
        out_trade_no: str,
        subject: str,
        total_amount: float,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建APP支付订单
        
        Args:
            out_trade_no: 商户订单号
            subject: 订单标题
            total_amount: 订单金额（单位：元）
            body: 订单描述
            
        Returns:
            支付订单字符串
        """
        try:
            order_string = self.alipay.api_alipay_trade_app_pay(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                body=body
            )
            
            logger.info(f"APP支付订单创建成功：{out_trade_no}")
            return {
                'success': True,
                'data': {
                    'order_string': order_string
                },
                'message': '订单创建成功'
            }
        except Exception as e:
            logger.error(f"APP支付订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def query_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        查询订单
        
        Args:
            out_trade_no: 商户订单号
            
        Returns:
            订单信息字典
        """
        try:
            result = self.alipay.api_alipay_trade_query(
                out_trade_no=out_trade_no
            )
            
            if result.get('code') == '10000':
                logger.info(f"订单查询成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': result,
                    'message': '查询成功'
                }
            else:
                logger.error(f"订单查询失败：{result}")
                return {
                    'success': False,
                    'error_code': result.get('code'),
                    'message': result.get('msg', '查询失败')
                }
        except Exception as e:
            logger.error(f"订单查询异常：{str(e)}")
            return {
                'success': False,
                'message': f'查询异常：{str(e)}'
            }
    
    def close_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        关闭订单
        
        Args:
            out_trade_no: 商户订单号
            
        Returns:
            操作结果字典
        """
        try:
            result = self.alipay.api_alipay_trade_close(
                out_trade_no=out_trade_no
            )
            
            if result.get('code') == '10000':
                logger.info(f"订单关闭成功：{out_trade_no}")
                return {
                    'success': True,
                    'message': '订单关闭成功'
                }
            else:
                logger.error(f"订单关闭失败：{result}")
                return {
                    'success': False,
                    'error_code': result.get('code'),
                    'message': result.get('msg', '关闭失败')
                }
        except Exception as e:
            logger.error(f"订单关闭异常：{str(e)}")
            return {
                'success': False,
                'message': f'关闭异常：{str(e)}'
            }
    
    def refund(
        self,
        out_trade_no: str,
        refund_amount: float,
        refund_reason: Optional[str] = None,
        out_request_no: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        申请退款

        Args:
            out_trade_no: 商户订单号
            refund_amount: 退款金额（单位：元）
            refund_reason: 退款原因
            out_request_no: 退款请求号（商户退款单号）

        Returns:
            退款结果字典
        """
        try:
            result = self.alipay.api_alipay_trade_refund(
                out_trade_no=out_trade_no,
                refund_amount=str(refund_amount),
                refund_reason=refund_reason,
                out_request_no=out_request_no
            )

            if result.get('code') == '10000':
                logger.info(f"退款申请成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': result,
                    'message': '退款申请成功'
                }
            else:
                logger.error(f"退款申请失败：{result}")
                return {
                    'success': False,
                    'error_code': result.get('code'),
                    'message': result.get('msg', '退款失败')
                }
        except Exception as e:
            logger.error(f"退款申请异常：{str(e)}")
            return {
                'success': False,
                'message': f'退款申请异常：{str(e)}'
            }

    def query_refund(
        self,
        out_trade_no: str,
        out_request_no: str
    ) -> Dict[str, Any]:
        """
        查询退款

        Args:
            out_trade_no: 商户订单号
            out_request_no: 退款请求号（商户退款单号）

        Returns:
            退款信息字典
        """
        try:
            result = self.alipay.api_alipay_trade_fastpay_refund_query(
                out_trade_no=out_trade_no,
                out_request_no=out_request_no
            )

            if result.get('code') == '10000':
                logger.info(f"退款查询成功：{out_request_no}")
                return {
                    'success': True,
                    'data': result,
                    'message': '查询成功'
                }
            else:
                logger.error(f"退款查询失败：{result}")
                return {
                    'success': False,
                    'error_code': result.get('code'),
                    'message': result.get('msg', '查询失败')
                }
        except Exception as e:
            logger.error(f"退款查询异常：{str(e)}")
            return {
                'success': False,
                'message': f'查询异常：{str(e)}'
            }

    def verify_notify(self, data: dict, sign: str) -> bool:
        """
        验证支付宝异步通知签名

        Args:
            data: 通知数据
            sign: 签名

        Returns:
            验证结果
        """
        try:
            result = self.alipay.verify(data, sign)
            if result:
                logger.info("支付宝通知签名验证成功")
            else:
                logger.warning("支付宝通知签名验证失败")
            return result
        except Exception as e:
            logger.error(f"支付宝通知签名验证异常：{str(e)}")
            return False

    def verify_sync_response(self, params: dict) -> bool:
        """
        验证支付宝同步返回签名

        Args:
            params: 返回参数

        Returns:
            验证结果
        """
        try:
            sign = params.pop('sign', None)
            if not sign:
                logger.warning("支付宝同步返回缺少签名")
                return False

            result = self.alipay.verify(params, sign)
            if result:
                logger.info("支付宝同步返回签名验证成功")
            else:
                logger.warning("支付宝同步返回签名验证失败")
            return result
        except Exception as e:
            logger.error(f"支付宝同步返回签名验证异常：{str(e)}")
            return False

