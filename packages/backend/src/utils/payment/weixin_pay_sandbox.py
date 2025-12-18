"""
微信支付沙箱环境工具类 (API v2)
用于微信支付沙箱环境的测试
"""
import hashlib
import random
import string
import time
import warnings
from typing import Dict, Any, Optional
import requests
import logging

# 安全修复：使用 defusedxml 防止 XXE 攻击
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    warnings.warn(
        "defusedxml 未安装，使用标准库 xml.etree.ElementTree。"
        "建议安装 defusedxml 以防止 XXE 攻击：pip install defusedxml",
        SecurityWarning
    )

logger = logging.getLogger(__name__)


class WeixinPaySandboxUtil:
    """微信支付沙箱环境工具类 (API v2)"""
    
    # 沙箱环境API基础URL
    SANDBOX_BASE_URL = "https://api.mch.weixin.qq.com/xdc/apiv2sandbox"
    # 获取沙箱密钥URL
    SANDBOX_KEY_URL = "https://api.mch.weixin.qq.com/xdc/apiv2getsignkey/sign/getsignkey"
    
    def __init__(
        self,
        appid: str,
        mch_id: str,
        api_key: str,
        notify_url: str = ""
    ):
        """
        初始化微信支付沙箱工具
        
        Args:
            appid: 微信公众号/小程序AppID
            mch_id: 商户号
            api_key: API密钥(用于获取沙箱密钥)
            notify_url: 支付结果通知URL
        """
        self.appid = appid
        self.mch_id = mch_id
        self.api_key = api_key
        self.notify_url = notify_url
        self.sandbox_signkey: Optional[str] = None
        
    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_sign(self, params: Dict[str, Any], key: str) -> str:
        """
        生成签名
        
        Args:
            params: 参数字典
            key: 签名密钥
            
        Returns:
            签名字符串
        """
        # 过滤空值和sign字段
        filtered_params = {k: v for k, v in params.items() if v != "" and v is not None and k != "sign"}
        
        # 按key排序
        sorted_params = sorted(filtered_params.items(), key=lambda x: x[0])
        
        # 拼接字符串
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={key}"

        # MD5加密并转大写
        # 安全修复：MD5 用于微信支付签名，是协议要求，非安全敏感
        md5 = hashlib.md5(sign_str.encode('utf-8'), usedforsecurity=False)
        return md5.hexdigest().upper()
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """将字典转换为XML"""
        xml_str = "<xml>"
        for k, v in data.items():
            if isinstance(v, (int, float)):
                xml_str += f"<{k}>{v}</{k}>"
            else:
                xml_str += f"<{k}><![CDATA[{v}]]></{k}>"
        xml_str += "</xml>"
        return xml_str
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """将XML转换为字典"""
        try:
            root = ET.fromstring(xml_str)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except Exception as e:
            logger.error(f"XML解析失败: {e}")
            return {}
    
    def get_sandbox_signkey(self) -> Dict[str, Any]:
        """
        获取沙箱密钥
        
        Returns:
            包含success, data, message的字典
        """
        try:
            # 构建请求参数
            params = {
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str()
            }
            
            # 生成签名(使用正式环境的API密钥)
            params["sign"] = self._generate_sign(params, self.api_key)
            
            # 转换为XML
            xml_data = self._dict_to_xml(params)
            
            # 发送请求
            response = requests.post(
                self.SANDBOX_KEY_URL,
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS":
                self.sandbox_signkey = result.get("sandbox_signkey")
                logger.info(f"获取沙箱密钥成功: {self.sandbox_signkey}")
                return {
                    "success": True,
                    "data": {"sandbox_signkey": self.sandbox_signkey},
                    "message": "获取沙箱密钥成功"
                }
            else:
                error_msg = result.get("return_msg", "获取沙箱密钥失败")
                logger.error(f"获取沙箱密钥失败: {error_msg}")
                return {
                    "success": False,
                    "data": None,
                    "message": error_msg
                }
                
        except Exception as e:
            logger.error(f"获取沙箱密钥异常: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"获取沙箱密钥异常: {str(e)}"
            }

    def create_native_order(
        self,
        out_trade_no: str,
        total_fee: int,
        body: str,
        product_id: str,
        spbill_create_ip: str = "127.0.0.1",
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建Native扫码支付订单

        Args:
            out_trade_no: 商户订单号
            total_fee: 订单金额(单位:分)
            body: 商品描述
            product_id: 商品ID
            spbill_create_ip: 终端IP
            **kwargs: 其他可选参数

        Returns:
            包含success, data, message的字典
        """
        try:
            # 确保已获取沙箱密钥
            if not self.sandbox_signkey:
                key_result = self.get_sandbox_signkey()
                if not key_result["success"]:
                    return key_result

            # 构建请求参数
            params = {
                "appid": self.appid,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str(),
                "body": body,
                "out_trade_no": out_trade_no,
                "total_fee": total_fee,
                "spbill_create_ip": spbill_create_ip,
                "notify_url": self.notify_url,
                "trade_type": "NATIVE",
                "product_id": product_id
            }

            # 添加可选参数
            optional_fields = ["attach", "detail", "fee_type", "time_start", "time_expire", "goods_tag"]
            for field in optional_fields:
                if field in kwargs and kwargs[field]:
                    params[field] = kwargs[field]

            # 生成签名(使用沙箱密钥)
            params["sign"] = self._generate_sign(params, self.sandbox_signkey)

            # 转换为XML
            xml_data = self._dict_to_xml(params)

            # 发送请求
            url = f"{self.SANDBOX_BASE_URL}/pay/unifiedorder"
            response = requests.post(
                url,
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )

            # 解析响应
            result = self._xml_to_dict(response.text)

            # 验证签名
            return_sign = result.pop("sign", "")
            calculated_sign = self._generate_sign(result, self.sandbox_signkey)

            if return_sign != calculated_sign:
                logger.error("返回签名验证失败")
                return {
                    "success": False,
                    "data": None,
                    "message": "返回签名验证失败"
                }

            # 检查返回结果
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                logger.info(f"创建Native订单成功: {out_trade_no}")
                return {
                    "success": True,
                    "data": {
                        "code_url": result.get("code_url"),
                        "prepay_id": result.get("prepay_id"),
                        "trade_type": result.get("trade_type")
                    },
                    "message": "创建订单成功"
                }
            else:
                error_msg = result.get("err_code_des") or result.get("return_msg", "创建订单失败")
                logger.error(f"创建Native订单失败: {error_msg}")
                return {
                    "success": False,
                    "data": None,
                    "message": error_msg
                }

        except Exception as e:
            logger.error(f"创建Native订单异常: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"创建订单异常: {str(e)}"
            }

    def query_order(
        self,
        out_trade_no: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询订单

        Args:
            out_trade_no: 商户订单号
            transaction_id: 微信订单号

        Returns:
            包含success, data, message的字典
        """
        try:
            if not out_trade_no and not transaction_id:
                return {
                    "success": False,
                    "data": None,
                    "message": "商户订单号和微信订单号至少填一个"
                }

            # 确保已获取沙箱密钥
            if not self.sandbox_signkey:
                key_result = self.get_sandbox_signkey()
                if not key_result["success"]:
                    return key_result

            # 构建请求参数
            params = {
                "appid": self.appid,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str()
            }

            if transaction_id:
                params["transaction_id"] = transaction_id
            else:
                params["out_trade_no"] = out_trade_no

            # 生成签名
            params["sign"] = self._generate_sign(params, self.sandbox_signkey)

            # 转换为XML
            xml_data = self._dict_to_xml(params)

            # 发送请求
            url = f"{self.SANDBOX_BASE_URL}/pay/orderquery"
            response = requests.post(
                url,
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )

            # 解析响应
            result = self._xml_to_dict(response.text)

            # 验证签名
            return_sign = result.pop("sign", "")
            calculated_sign = self._generate_sign(result, self.sandbox_signkey)

            if return_sign != calculated_sign:
                logger.error("返回签名验证失败")
                return {
                    "success": False,
                    "data": None,
                    "message": "返回签名验证失败"
                }

            # 检查返回结果
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                logger.info(f"查询订单成功: {out_trade_no or transaction_id}")
                return {
                    "success": True,
                    "data": {
                        "trade_state": result.get("trade_state"),
                        "trade_state_desc": result.get("trade_state_desc"),
                        "transaction_id": result.get("transaction_id"),
                        "out_trade_no": result.get("out_trade_no"),
                        "total_fee": result.get("total_fee"),
                        "time_end": result.get("time_end")
                    },
                    "message": "查询订单成功"
                }
            else:
                error_msg = result.get("err_code_des") or result.get("return_msg", "查询订单失败")
                logger.error(f"查询订单失败: {error_msg}")
                return {
                    "success": False,
                    "data": None,
                    "message": error_msg
                }

        except Exception as e:
            logger.error(f"查询订单异常: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"查询订单异常: {str(e)}"
            }

    def close_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        关闭订单

        Args:
            out_trade_no: 商户订单号

        Returns:
            包含success, data, message的字典
        """
        try:
            # 确保已获取沙箱密钥
            if not self.sandbox_signkey:
                key_result = self.get_sandbox_signkey()
                if not key_result["success"]:
                    return key_result

            # 构建请求参数
            params = {
                "appid": self.appid,
                "mch_id": self.mch_id,
                "out_trade_no": out_trade_no,
                "nonce_str": self._generate_nonce_str()
            }

            # 生成签名
            params["sign"] = self._generate_sign(params, self.sandbox_signkey)

            # 转换为XML
            xml_data = self._dict_to_xml(params)

            # 发送请求
            url = f"{self.SANDBOX_BASE_URL}/pay/closeorder"
            response = requests.post(
                url,
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )

            # 解析响应
            result = self._xml_to_dict(response.text)

            # 验证签名
            return_sign = result.pop("sign", "")
            calculated_sign = self._generate_sign(result, self.sandbox_signkey)

            if return_sign != calculated_sign:
                logger.error("返回签名验证失败")
                return {
                    "success": False,
                    "data": None,
                    "message": "返回签名验证失败"
                }

            # 检查返回结果
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                logger.info(f"关闭订单成功: {out_trade_no}")
                return {
                    "success": True,
                    "data": None,
                    "message": "关闭订单成功"
                }
            else:
                error_msg = result.get("err_code_des") or result.get("return_msg", "关闭订单失败")
                logger.error(f"关闭订单失败: {error_msg}")
                return {
                    "success": False,
                    "data": None,
                    "message": error_msg
                }

        except Exception as e:
            logger.error(f"关闭订单异常: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"关闭订单异常: {str(e)}"
            }

    def verify_notify(self, xml_data: str) -> Dict[str, Any]:
        """
        验证支付回调通知

        Args:
            xml_data: 回调通知的XML数据

        Returns:
            包含success, data, message的字典
        """
        try:
            # 解析XML
            result = self._xml_to_dict(xml_data)

            # 确保已获取沙箱密钥
            if not self.sandbox_signkey:
                key_result = self.get_sandbox_signkey()
                if not key_result["success"]:
                    return key_result

            # 验证签名
            return_sign = result.pop("sign", "")
            calculated_sign = self._generate_sign(result, self.sandbox_signkey)

            if return_sign != calculated_sign:
                logger.error("回调签名验证失败")
                return {
                    "success": False,
                    "data": None,
                    "message": "签名验证失败"
                }

            # 检查返回结果
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                logger.info(f"回调验证成功: {result.get('out_trade_no')}")
                return {
                    "success": True,
                    "data": result,
                    "message": "验证成功"
                }
            else:
                error_msg = result.get("err_code_des") or result.get("return_msg", "支付失败")
                logger.error(f"回调验证失败: {error_msg}")
                return {
                    "success": False,
                    "data": result,
                    "message": error_msg
                }

        except Exception as e:
            logger.error(f"回调验证异常: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"回调验证异常: {str(e)}"
            }

