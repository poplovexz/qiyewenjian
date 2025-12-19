"""
Sentry 错误监控集成
用于捕获和上报后端异常、性能数据
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

from core.config import settings


def init_sentry() -> bool:
    """
    初始化 Sentry SDK
    
    Returns:
        bool: 是否成功初始化
    """
    dsn = settings.SENTRY_DSN
    
    if not dsn:
        return False
    
    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=settings.SENTRY_ENVIRONMENT,
            release="qiyewenjian-backend@1.0.0",
            
            # 性能监控
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            
            # 集成配置
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            
            # 错误过滤
            before_send=before_send_filter,
            
            # 敏感数据处理
            send_default_pii=False,  # 不发送个人身份信息
            
            # 附加信息
            attach_stacktrace=True,
        )
        
        return True
        
    except Exception as e:
        return False


def before_send_filter(event, hint):
    """
    发送前过滤器，用于过滤不需要上报的错误
    """
    # 获取异常信息
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]
        
        # 过滤常见的非关键错误
        ignored_exceptions = [
            "ConnectionResetError",
            "BrokenPipeError", 
            "ClientDisconnected",
        ]
        
        if exc_type.__name__ in ignored_exceptions:
            return None
        
        # 过滤 404 错误
        if hasattr(exc_value, "status_code") and exc_value.status_code == 404:
            return None
    
    return event


def set_user_context(user_id: int, username: str = None, role: str = None):
    """设置用户上下文"""
    sentry_sdk.set_user({
        "id": str(user_id),
        "username": username,
        "role": role,
    })


def clear_user_context():
    """清除用户上下文"""
    sentry_sdk.set_user(None)


def capture_exception(error: Exception, **extra):
    """手动捕获异常"""
    with sentry_sdk.push_scope() as scope:
        for key, value in extra.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info"):
    """手动捕获消息"""
    sentry_sdk.capture_message(message, level=level)


def add_breadcrumb(message: str, category: str = "custom", data: dict = None):
    """添加面包屑"""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        data=data or {},
    )

