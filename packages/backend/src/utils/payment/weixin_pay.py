"""
微信支付工具类
封装微信支付API v3的常用功能
"""
from typing import Dict, Any, Optional
from wechatpayv3 import WeChatPay, WeChatPayType
import logging

logger = logging.getLogger(__name__)


class WeixinPayUtil:
    """微信支付工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化微信支付工具
        
        Args:
            config: 支付配置字典，包含以下字段：
                - weixin_appid: 微信APPID
                - weixin_shanghu_hao: 微信商户号
                - weixin_shanghu_siyao: 微信商户私钥
                - weixin_zhengshu_xuliehao: 微信证书序列号
                - weixin_api_v3_miyao: 微信API v3密钥
                - tongzhi_url: 支付回调通知URL
        """
        self.config = config
        self.appid = config.get('weixin_appid')
        self.mchid = config.get('weixin_shanghu_hao')
        self.private_key = config.get('weixin_shanghu_siyao')
        self.cert_serial_no = config.get('weixin_zhengshu_xuliehao')
        self.apiv3_key = config.get('weixin_api_v3_miyao')
        self.notify_url = config.get('tongzhi_url')
        
        # 初始化微信支付客户端
        self.wxpay = None
        self._init_client()
    
    def _init_client(self, pay_type: WeChatPayType = WeChatPayType.JSAPI):
        """
        初始化微信支付客户端
        
        Args:
            pay_type: 支付类型
        """
        try:
            self.wxpay = WeChatPay(
                wechatpay_type=pay_type,
                mchid=self.mchid,
                private_key=self.private_key,
                cert_serial_no=self.cert_serial_no,
                apiv3_key=self.apiv3_key,
                appid=self.appid,
                notify_url=self.notify_url
            )
            logger.info(f"微信支付客户端初始化成功，商户号：{self.mchid}")
        except Exception as e:
            logger.error(f"微信支付客户端初始化失败：{str(e)}")
            raise
    
    def create_jsapi_order(
        self,
        out_trade_no: str,
        description: str,
        amount: int,
        payer_openid: str,
        attach: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建JSAPI支付订单（公众号/小程序支付）
        
        Args:
            out_trade_no: 商户订单号
            description: 商品描述
            amount: 订单金额（单位：分）
            payer_openid: 用户OpenID
            attach: 附加数据
            
        Returns:
            支付参数字典
        """
        try:
            self._init_client(WeChatPayType.JSAPI)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount={'total': amount, 'currency': 'CNY'},
                payer={'openid': payer_openid},
                attach=attach
            )
            
            if code == 200:
                logger.info(f"JSAPI订单创建成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '订单创建成功'
                }
            else:
                logger.error(f"JSAPI订单创建失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"JSAPI订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def create_app_order(
        self,
        out_trade_no: str,
        description: str,
        amount: int,
        attach: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建APP支付订单
        
        Args:
            out_trade_no: 商户订单号
            description: 商品描述
            amount: 订单金额（单位：分）
            attach: 附加数据
            
        Returns:
            支付参数字典
        """
        try:
            self._init_client(WeChatPayType.APP)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount={'total': amount, 'currency': 'CNY'},
                attach=attach
            )
            
            if code == 200:
                logger.info(f"APP订单创建成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '订单创建成功'
                }
            else:
                logger.error(f"APP订单创建失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"APP订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def create_h5_order(
        self,
        out_trade_no: str,
        description: str,
        amount: int,
        payer_client_ip: str,
        attach: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建H5支付订单
        
        Args:
            out_trade_no: 商户订单号
            description: 商品描述
            amount: 订单金额（单位：分）
            payer_client_ip: 用户终端IP
            attach: 附加数据
            
        Returns:
            支付参数字典
        """
        try:
            self._init_client(WeChatPayType.H5)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount={'total': amount, 'currency': 'CNY'},
                scene_info={'payer_client_ip': payer_client_ip, 'h5_info': {'type': 'Wap'}},
                attach=attach
            )
            
            if code == 200:
                logger.info(f"H5订单创建成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '订单创建成功'
                }
            else:
                logger.error(f"H5订单创建失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"H5订单创建异常：{str(e)}")
            return {
                'success': False,
                'message': f'订单创建异常：{str(e)}'
            }
    
    def create_native_order(
        self,
        out_trade_no: str,
        description: str,
        amount: int,
        attach: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建Native支付订单（扫码支付）
        
        Args:
            out_trade_no: 商户订单号
            description: 商品描述
            amount: 订单金额（单位：分）
            attach: 附加数据
            
        Returns:
            支付参数字典（包含二维码链接）
        """
        try:
            self._init_client(WeChatPayType.NATIVE)
            
            code, message = self.wxpay.pay(
                description=description,
                out_trade_no=out_trade_no,
                amount={'total': amount, 'currency': 'CNY'},
                attach=attach
            )
            
            if code == 200:
                logger.info(f"Native订单创建成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '订单创建成功'
                }
            else:
                logger.error(f"Native订单创建失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"Native订单创建异常：{str(e)}")
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
            code, message = self.wxpay.query(out_trade_no=out_trade_no)
            
            if code == 200:
                logger.info(f"订单查询成功：{out_trade_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '查询成功'
                }
            else:
                logger.error(f"订单查询失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
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
            code, message = self.wxpay.close(out_trade_no=out_trade_no)

            if code == 204:
                logger.info(f"订单关闭成功：{out_trade_no}")
                return {
                    'success': True,
                    'message': '订单关闭成功'
                }
            else:
                logger.error(f"订单关闭失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
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
        out_refund_no: str,
        refund_amount: int,
        total_amount: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        申请退款

        Args:
            out_trade_no: 商户订单号
            out_refund_no: 商户退款单号
            refund_amount: 退款金额（单位：分）
            total_amount: 原订单金额（单位：分）
            reason: 退款原因

        Returns:
            退款结果字典
        """
        try:
            code, message = self.wxpay.refund(
                out_trade_no=out_trade_no,
                out_refund_no=out_refund_no,
                amount={
                    'refund': refund_amount,
                    'total': total_amount,
                    'currency': 'CNY'
                },
                reason=reason
            )

            if code == 200:
                logger.info(f"退款申请成功：{out_refund_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '退款申请成功'
                }
            else:
                logger.error(f"退款申请失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"退款申请异常：{str(e)}")
            return {
                'success': False,
                'message': f'退款申请异常：{str(e)}'
            }

    def query_refund(self, out_refund_no: str) -> Dict[str, Any]:
        """
        查询退款

        Args:
            out_refund_no: 商户退款单号

        Returns:
            退款信息字典
        """
        try:
            code, message = self.wxpay.query_refund(out_refund_no=out_refund_no)

            if code == 200:
                logger.info(f"退款查询成功：{out_refund_no}")
                return {
                    'success': True,
                    'data': message,
                    'message': '查询成功'
                }
            else:
                logger.error(f"退款查询失败：{code} - {message}")
                return {
                    'success': False,
                    'error_code': code,
                    'message': message
                }
        except Exception as e:
            logger.error(f"退款查询异常：{str(e)}")
            return {
                'success': False,
                'message': f'查询异常：{str(e)}'
            }

    def callback(self, headers: dict, body: str) -> Dict[str, Any]:
        """
        处理支付回调

        Args:
            headers: 请求头
            body: 请求体

        Returns:
            回调数据字典
        """
        try:
            result = self.wxpay.callback(headers, body)
            logger.info(f"支付回调处理成功")
            return {
                'success': True,
                'data': result,
                'message': '回调处理成功'
            }
        except Exception as e:
            logger.error(f"支付回调处理失败：{str(e)}")
            return {
                'success': False,
                'message': f'回调处理失败：{str(e)}'
            }

