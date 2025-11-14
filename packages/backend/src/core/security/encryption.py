"""
AES加密工具类
用于加密存储敏感信息（如支付密钥、证书等）
"""
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
from typing import Optional

from core.config import settings


class AESEncryption:
    """AES加密工具类"""
    
    def __init__(self, key: Optional[str] = None):
        """
        初始化AES加密工具
        
        Args:
            key: 加密密钥，如果不提供则使用配置中的SECRET_KEY
        """
        if key is None:
            key = settings.SECRET_KEY
        
        # 使用SHA256将密钥转换为32字节
        self.key = hashlib.sha256(key.encode()).digest()
        self.backend = default_backend()
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密字符串
        
        Args:
            plaintext: 明文字符串
            
        Returns:
            加密后的Base64编码字符串
        """
        if not plaintext:
            return ""
        
        # 生成随机IV（初始化向量）
        iv = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 填充明文到AES块大小（128位=16字节）
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        
        # 加密
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 将IV和密文组合，然后Base64编码
        result = base64.b64encode(iv + ciphertext).decode('utf-8')
        
        return result
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密字符串
        
        Args:
            ciphertext: 加密后的Base64编码字符串
            
        Returns:
            解密后的明文字符串
        """
        if not ciphertext:
            return ""
        
        try:
            # Base64解码
            encrypted_data = base64.b64decode(ciphertext)
            
            # 提取IV和密文
            iv = encrypted_data[:16]
            actual_ciphertext = encrypted_data[16:]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # 解密
            padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
            
            # 去除填充
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            return plaintext.decode('utf-8')
        
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        加密字典中的指定字段
        
        Args:
            data: 要加密的字典
            fields: 需要加密的字段列表
            
        Returns:
            加密后的字典
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        解密字典中的指定字段
        
        Args:
            data: 要解密的字典
            fields: 需要解密的字段列表
            
        Returns:
            解密后的字典
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                try:
                    result[field] = self.decrypt(str(result[field]))
                except Exception:
                    # 如果解密失败，保持原值（可能是未加密的数据）
                    pass
        return result


# 创建全局加密实例
encryption = AESEncryption()


def encrypt_sensitive_data(data: str) -> str:
    """
    加密敏感数据的便捷函数
    
    Args:
        data: 要加密的数据
        
    Returns:
        加密后的数据
    """
    return encryption.encrypt(data)


def decrypt_sensitive_data(data: str) -> str:
    """
    解密敏感数据的便捷函数
    
    Args:
        data: 要解密的数据
        
    Returns:
        解密后的数据
    """
    return encryption.decrypt(data)

