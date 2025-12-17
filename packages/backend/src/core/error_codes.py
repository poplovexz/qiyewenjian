"""
统一错误码定义

错误码格式: XXYYYY
- XX: 模块代码 (10-99)
- YYYY: 具体错误码 (0001-9999)

模块划分:
- 10: 通用错误
- 11: 认证授权
- 12: 数据验证
- 20: 用户管理
- 30: 客户管理
- 40: 合同管理
- 50: 财务管理
- 60: 线索管理
- 70: 外部服务
"""
from enum import Enum
from typing import NamedTuple


class ErrorInfo(NamedTuple):
    """错误信息结构"""
    code: str
    message: str
    http_status: int


class ErrorCode(Enum):
    """统一错误码枚举"""

    # ========== 10xxxx 通用错误 ==========
    UNKNOWN_ERROR = ErrorInfo("100000", "未知错误", 500)
    INTERNAL_ERROR = ErrorInfo("100001", "服务器内部错误", 500)
    SERVICE_UNAVAILABLE = ErrorInfo("100002", "服务暂时不可用", 503)
    REQUEST_TIMEOUT = ErrorInfo("100003", "请求超时", 408)
    RATE_LIMIT_EXCEEDED = ErrorInfo("100004", "请求过于频繁，请稍后重试", 429)
    INVALID_REQUEST = ErrorInfo("100005", "无效的请求", 400)
    RESOURCE_NOT_FOUND = ErrorInfo("100006", "资源不存在", 404)
    RESOURCE_CONFLICT = ErrorInfo("100007", "资源冲突", 409)
    METHOD_NOT_ALLOWED = ErrorInfo("100008", "请求方法不允许", 405)

    # ========== 11xxxx 认证授权 ==========
    AUTH_FAILED = ErrorInfo("110001", "认证失败", 401)
    TOKEN_EXPIRED = ErrorInfo("110002", "登录已过期，请重新登录", 401)
    TOKEN_INVALID = ErrorInfo("110003", "无效的令牌", 401)
    TOKEN_MISSING = ErrorInfo("110004", "未提供认证令牌", 401)
    PERMISSION_DENIED = ErrorInfo("110005", "权限不足", 403)
    ACCOUNT_DISABLED = ErrorInfo("110006", "账户已被禁用", 403)
    ACCOUNT_LOCKED = ErrorInfo("110007", "账户已被锁定", 403)
    LOGIN_FAILED = ErrorInfo("110008", "用户名或密码错误", 401)
    PASSWORD_EXPIRED = ErrorInfo("110009", "密码已过期，请修改密码", 401)
    REFRESH_TOKEN_INVALID = ErrorInfo("110010", "刷新令牌无效", 401)

    # ========== 12xxxx 数据验证 ==========
    VALIDATION_ERROR = ErrorInfo("120001", "数据验证失败", 422)
    MISSING_REQUIRED_FIELD = ErrorInfo("120002", "缺少必填字段", 422)
    INVALID_FIELD_FORMAT = ErrorInfo("120003", "字段格式不正确", 422)
    FIELD_VALUE_OUT_OF_RANGE = ErrorInfo("120004", "字段值超出范围", 422)
    DUPLICATE_ENTRY = ErrorInfo("120005", "数据已存在", 409)
    INVALID_PHONE_FORMAT = ErrorInfo("120006", "手机号格式不正确", 422)
    INVALID_EMAIL_FORMAT = ErrorInfo("120007", "邮箱格式不正确", 422)
    INVALID_ID_CARD_FORMAT = ErrorInfo("120008", "身份证号格式不正确", 422)
    FILE_TOO_LARGE = ErrorInfo("120009", "文件大小超出限制", 413)
    INVALID_FILE_TYPE = ErrorInfo("120010", "不支持的文件类型", 415)

    # ========== 20xxxx 用户管理 ==========
    USER_NOT_FOUND = ErrorInfo("200001", "用户不存在", 404)
    USER_ALREADY_EXISTS = ErrorInfo("200002", "用户已存在", 409)
    USER_CREATE_FAILED = ErrorInfo("200003", "创建用户失败", 500)
    USER_UPDATE_FAILED = ErrorInfo("200004", "更新用户失败", 500)
    USER_DELETE_FAILED = ErrorInfo("200005", "删除用户失败", 500)
    PASSWORD_TOO_WEAK = ErrorInfo("200006", "密码强度不够", 422)
    OLD_PASSWORD_WRONG = ErrorInfo("200007", "原密码错误", 400)

    # ========== 30xxxx 客户管理 ==========
    CUSTOMER_NOT_FOUND = ErrorInfo("300001", "客户不存在", 404)
    CUSTOMER_ALREADY_EXISTS = ErrorInfo("300002", "客户已存在", 409)
    CUSTOMER_CREATE_FAILED = ErrorInfo("300003", "创建客户失败", 500)
    CUSTOMER_UPDATE_FAILED = ErrorInfo("300004", "更新客户失败", 500)
    CUSTOMER_DELETE_FAILED = ErrorInfo("300005", "删除客户失败", 500)
    CUSTOMER_HAS_CONTRACTS = ErrorInfo("300006", "客户存在有效合同，无法删除", 400)

    # ========== 40xxxx 合同管理 ==========
    CONTRACT_NOT_FOUND = ErrorInfo("400001", "合同不存在", 404)
    CONTRACT_ALREADY_EXISTS = ErrorInfo("400002", "合同已存在", 409)
    CONTRACT_CREATE_FAILED = ErrorInfo("400003", "创建合同失败", 500)
    CONTRACT_UPDATE_FAILED = ErrorInfo("400004", "更新合同失败", 500)
    CONTRACT_DELETE_FAILED = ErrorInfo("400005", "删除合同失败", 500)
    CONTRACT_STATUS_INVALID = ErrorInfo("400006", "合同状态不允许此操作", 400)
    CONTRACT_EXPIRED = ErrorInfo("400007", "合同已过期", 400)
    CONTRACT_SIGN_FAILED = ErrorInfo("400008", "合同签署失败", 500)

    # ========== 50xxxx 财务管理 ==========
    PAYMENT_NOT_FOUND = ErrorInfo("500001", "付款记录不存在", 404)
    PAYMENT_FAILED = ErrorInfo("500002", "支付失败", 500)
    REFUND_FAILED = ErrorInfo("500003", "退款失败", 500)
    INVOICE_NOT_FOUND = ErrorInfo("500004", "发票不存在", 404)
    INVOICE_CREATE_FAILED = ErrorInfo("500005", "创建发票失败", 500)
    INSUFFICIENT_BALANCE = ErrorInfo("500006", "余额不足", 400)
    AMOUNT_INVALID = ErrorInfo("500007", "金额无效", 422)

    # ========== 60xxxx 线索管理 ==========
    LEAD_NOT_FOUND = ErrorInfo("600001", "线索不存在", 404)
    LEAD_ALREADY_EXISTS = ErrorInfo("600002", "线索已存在", 409)
    LEAD_CREATE_FAILED = ErrorInfo("600003", "创建线索失败", 500)
    LEAD_UPDATE_FAILED = ErrorInfo("600004", "更新线索失败", 500)
    LEAD_CONVERT_FAILED = ErrorInfo("600005", "线索转化失败", 500)
    QUOTE_NOT_FOUND = ErrorInfo("600006", "报价不存在", 404)
    QUOTE_CREATE_FAILED = ErrorInfo("600007", "创建报价失败", 500)

    # ========== 70xxxx 外部服务 ==========
    EXTERNAL_SERVICE_ERROR = ErrorInfo("700001", "外部服务调用失败", 502)
    SMS_SEND_FAILED = ErrorInfo("700002", "短信发送失败", 500)
    EMAIL_SEND_FAILED = ErrorInfo("700003", "邮件发送失败", 500)
    WECHAT_API_ERROR = ErrorInfo("700004", "微信接口调用失败", 502)
    ALIPAY_API_ERROR = ErrorInfo("700005", "支付宝接口调用失败", 502)
    OSS_UPLOAD_FAILED = ErrorInfo("700006", "文件上传失败", 500)
    OCR_FAILED = ErrorInfo("700007", "OCR识别失败", 500)

    # ========== 80xxxx 数据库错误 ==========
    DATABASE_ERROR = ErrorInfo("800001", "数据库错误", 500)
    DATABASE_CONNECTION_FAILED = ErrorInfo("800002", "数据库连接失败", 503)
    DATABASE_QUERY_FAILED = ErrorInfo("800003", "数据库查询失败", 500)
    DATABASE_TRANSACTION_FAILED = ErrorInfo("800004", "数据库事务失败", 500)

    @property
    def code(self) -> str:
        return self.value.code

    @property
    def message(self) -> str:
        return self.value.message

    @property
    def http_status(self) -> int:
        return self.value.http_status

