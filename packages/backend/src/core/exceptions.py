"""
自定义异常类

企业级异常处理：
- 统一错误码
- HTTP 状态码映射
- 结构化错误响应
"""
from typing import Any, Dict, Optional, Union

from core.error_codes import ErrorCode


class BaseCustomException(Exception):
    """
    基础自定义异常类

    支持两种初始化方式：
    1. 使用 ErrorCode 枚举: raise BusinessException(ErrorCode.USER_NOT_FOUND)
    2. 传统方式: raise BusinessException("用户不存在", "USER_NOT_FOUND")
    """

    # 默认 HTTP 状态码
    default_http_status: int = 500

    def __init__(
        self,
        error: Union[ErrorCode, str] = "An error occurred",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        if isinstance(error, ErrorCode):
            # 使用 ErrorCode 枚举初始化
            self.message = error.message
            self.error_code = error.code
            self.http_status = error.http_status
        else:
            # 传统方式初始化
            self.message = error
            self.error_code = error_code or "UNKNOWN_ERROR"
            self.http_status = http_status or self.default_http_status

        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于 API 响应"""
        result = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class BusinessException(BaseCustomException):
    """业务逻辑异常"""
    default_http_status = 400

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Business logic error",
        error_code: Optional[str] = "BUSINESS_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ValidationException(BaseCustomException):
    """数据验证异常"""
    default_http_status = 422

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Validation error",
        error_code: Optional[str] = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class AuthenticationException(BaseCustomException):
    """认证异常"""
    default_http_status = 401

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Authentication failed",
        error_code: Optional[str] = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class AuthorizationException(BaseCustomException):
    """授权异常"""
    default_http_status = 403

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Authorization failed",
        error_code: Optional[str] = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ResourceNotFoundException(BaseCustomException):
    """资源未找到异常"""
    default_http_status = 404

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Resource not found",
        error_code: Optional[str] = "RESOURCE_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ResourceConflictException(BaseCustomException):
    """资源冲突异常"""
    default_http_status = 409

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Resource conflict",
        error_code: Optional[str] = "RESOURCE_CONFLICT",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class DatabaseException(BaseCustomException):
    """数据库异常"""
    default_http_status = 500

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Database error",
        error_code: Optional[str] = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ExternalServiceException(BaseCustomException):
    """外部服务异常"""
    default_http_status = 502

    def __init__(
        self,
        error: Union[ErrorCode, str] = "External service error",
        error_code: Optional[str] = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ConfigurationException(BaseCustomException):
    """配置异常"""
    default_http_status = 500

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Configuration error",
        error_code: Optional[str] = "CONFIG_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class RateLimitException(BaseCustomException):
    """频率限制异常"""
    default_http_status = 429

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Rate limit exceeded",
        error_code: Optional[str] = "RATE_LIMIT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class PaymentException(BaseCustomException):
    """支付异常"""
    default_http_status = 500

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Payment error",
        error_code: Optional[str] = "PAYMENT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class AuditException(BaseCustomException):
    """审核异常"""
    default_http_status = 400

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Audit error",
        error_code: Optional[str] = "AUDIT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class ContractException(BaseCustomException):
    """合同异常"""
    default_http_status = 400

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Contract error",
        error_code: Optional[str] = "CONTRACT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)


class SignatureException(BaseCustomException):
    """签署异常"""
    default_http_status = 400

    def __init__(
        self,
        error: Union[ErrorCode, str] = "Signature error",
        error_code: Optional[str] = "SIGNATURE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None
    ):
        super().__init__(error, error_code, details, http_status or self.default_http_status)
