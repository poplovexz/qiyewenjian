"""
自定义异常类
"""
from typing import Any, Dict, Optional


class BaseCustomException(Exception):
    """基础自定义异常类"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessException(BaseCustomException):
    """业务逻辑异常"""
    
    def __init__(
        self,
        message: str = "Business logic error",
        error_code: str = "BUSINESS_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ValidationException(BaseCustomException):
    """数据验证异常"""
    
    def __init__(
        self,
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthenticationException(BaseCustomException):
    """认证异常"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthorizationException(BaseCustomException):
    """授权异常"""
    
    def __init__(
        self,
        message: str = "Authorization failed",
        error_code: str = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ResourceNotFoundException(BaseCustomException):
    """资源未找到异常"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "RESOURCE_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ResourceConflictException(BaseCustomException):
    """资源冲突异常"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "RESOURCE_CONFLICT",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class DatabaseException(BaseCustomException):
    """数据库异常"""
    
    def __init__(
        self,
        message: str = "Database error",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ExternalServiceException(BaseCustomException):
    """外部服务异常"""
    
    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ConfigurationException(BaseCustomException):
    """配置异常"""
    
    def __init__(
        self,
        message: str = "Configuration error",
        error_code: str = "CONFIG_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class RateLimitException(BaseCustomException):
    """频率限制异常"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class PaymentException(BaseCustomException):
    """支付异常"""
    
    def __init__(
        self,
        message: str = "Payment error",
        error_code: str = "PAYMENT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuditException(BaseCustomException):
    """审核异常"""
    
    def __init__(
        self,
        message: str = "Audit error",
        error_code: str = "AUDIT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ContractException(BaseCustomException):
    """合同异常"""
    
    def __init__(
        self,
        message: str = "Contract error",
        error_code: str = "CONTRACT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class SignatureException(BaseCustomException):
    """签署异常"""
    
    def __init__(
        self,
        message: str = "Signature error",
        error_code: str = "SIGNATURE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
