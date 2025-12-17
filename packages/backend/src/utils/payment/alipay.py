"""
支付宝支付工具类
封装支付宝支付API的常用功能
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 导入支付宝SDK
try:
    from alipay import AliPay
    from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
    from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
    ALIPAY_SDK_AVAILABLE = True
except ImportError:
    logger.warning("支付宝SDK未正确安装，支付宝支付功能将不可用")
    ALIPAY_SDK_AVAILABLE = False
    AliPay = None  # 占位符，避免NameError


class AlipayUtil:
    """支付宝支付工具类"""

    def __init__(
        self,
        appid: str,
        app_private_key: str,
        alipay_public_key: str,
        notify_url: str,
        return_url: Optional[str] = None,
        debug: bool = False,
        gateway_url: Optional[str] = None
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
            gateway_url: 支付宝网关地址(可选,如果不提供则根据debug自动选择)
        """
        self.appid = appid
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key
        self.notify_url = notify_url
        self.return_url = return_url
        self.debug = debug

        # 设置网关地址
        # 沙箱环境下强制使用官方沙箱网关，避免误用生产网关
        if debug:
            # 使用支付宝官方沙箱网关
            self.gateway_url = "https://openapi.alipaydev.com/gateway.do"
        else:
            # 生产环境优先使用配置的网关，否则使用默认官方网关
            self.gateway_url = gateway_url or "https://openapi.alipay.com/gateway.do"

        logger.info(f"初始化支付宝网关: {self.gateway_url} (debug={self.debug})")

        # 初始化支付宝客户端
        self.alipay = None
        if ALIPAY_SDK_AVAILABLE:
            self._init_client()
        else:
            logger.warning("支付宝SDK不可用，支付功能将受限")
    
    def _format_private_key(self, key: str) -> str:
        """
        格式化私钥为PEM格式

        Args:
            key: 私钥字符串(可能是纯Base64或PEM格式)

        Returns:
            PEM格式的私钥
        """
        if not key:
            raise ValueError("私钥不能为空")

        # 移除所有空白字符
        key = key.strip().replace('\n', '').replace('\r', '').replace(' ', '')

        # 如果已经是PEM格式,直接返回
        if '-----BEGIN' in key:
            return key

        # 添加PEM头尾
        pem_key = f"-----BEGIN RSA PRIVATE KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(key), 64):
            pem_key += key[i:i+64] + "\n"
        pem_key += "-----END RSA PRIVATE KEY-----"

        return pem_key

    def _format_public_key(self, key: str) -> str:
        """
        格式化公钥为PEM格式

        Args:
            key: 公钥字符串(可能是纯Base64或PEM格式)

        Returns:
            PEM格式的公钥
        """
        if not key:
            raise ValueError("公钥不能为空")

        # 移除所有空白字符
        key = key.strip().replace('\n', '').replace('\r', '').replace(' ', '')

        # 如果已经是PEM格式,直接返回
        if '-----BEGIN' in key:
            return key

        # 添加PEM头尾
        pem_key = f"-----BEGIN PUBLIC KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(key), 64):
            pem_key += key[i:i+64] + "\n"
        pem_key += "-----END PUBLIC KEY-----"

        return pem_key

    def _init_client(self):
        """初始化支付宝客户端"""
        if not ALIPAY_SDK_AVAILABLE:
            return

        try:
            # 格式化密钥为PEM格式
            formatted_private_key = self._format_private_key(self.app_private_key)
            formatted_public_key = self._format_public_key(self.alipay_public_key)

            self.alipay = AliPay(
                appid=self.appid,
                app_notify_url=self.notify_url,
                app_private_key_string=formatted_private_key,
                alipay_public_key_string=formatted_public_key,
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

            # 构建完整的支付URL,使用配置的网关地址
            pay_url = f"{self.gateway_url}?{order_string}"
            
            logger.info(f"网页支付订单创建成功：{out_trade_no}")
            return {
                'success': True,
                'qr_code': pay_url,  # 用于扫码支付的URL
                'pay_url': pay_url,
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
            
            # 构建完整的支付URL，统一使用初始化时选择的网关地址
            pay_url = f"{self.gateway_url}?{order_string}"
            
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

    def create_precreate_pay(
        self,
        out_trade_no: str,
        subject: str,
        total_amount: float,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建扫码支付订单（当面付-扫码支付）
        返回二维码字符串，前端可以直接生成二维码图片

        Args:
            out_trade_no: 商户订单号
            subject: 订单标题
            total_amount: 订单金额（单位：元）
            body: 订单描述

        Returns:
            包含二维码字符串的字典
        """
        try:
            result = self.alipay.api_alipay_trade_precreate(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                body=body
            )

            # precreate 返回的是一个字典，包含 code 和 qr_code
            if result.get('code') == '10000':
                qr_code = result.get('qr_code')
                logger.info(f"扫码支付订单创建成功：{out_trade_no}, 二维码：{qr_code[:50]}...")
                return {
                    'success': True,
                    'qr_code': qr_code,  # 这是一个字符串，前端需要转换成二维码图片
                    'code_url': qr_code,  # 兼容微信的字段名
                    'data': {
                        'qr_code': qr_code,
                        'code_url': qr_code
                    },
                    'message': '订单创建成功'
                }
            else:
                error_msg = result.get('msg', '订单创建失败')
                logger.error(f"扫码支付订单创建失败：{result}")
                return {
                    'success': False,
                    'error_code': result.get('code'),
                    'message': error_msg
                }
        except Exception as e:
            logger.error(f"扫码支付订单创建异常：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
