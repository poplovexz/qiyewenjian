"""
企业级结构化日志系统

功能：
- JSON 格式日志输出
- 请求追踪 ID (X-Request-ID)
- 多级别日志 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 按环境配置日志级别
- 上下文日志 (用户ID、请求路径等)
"""
import logging
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Optional
from contextvars import ContextVar

# 上下文变量，用于存储请求追踪信息
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[Optional[int]] = ContextVar("user_id", default=None)
request_path_var: ContextVar[str] = ContextVar("request_path", default="-")

class JSONFormatter(logging.Formatter):
    """JSON 格式化器，输出结构化日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加用户ID（如果有）
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # 添加请求路径（如果有）
        request_path = request_path_var.get()
        if request_path != "-":
            log_data["path"] = request_path

        # 添加额外字段
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False, default=str)

class PrettyFormatter(logging.Formatter):
    """开发环境友好的格式化器"""

    COLORS = {
        "DEBUG": "\033[36m",     # 青色
        "INFO": "\033[32m",      # 绿色
        "WARNING": "\033[33m",   # 黄色
        "ERROR": "\033[31m",     # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        request_id = request_id_var.get()[:8] if request_id_var.get() != "-" else "-"

        # 格式: [时间] [级别] [请求ID] 模块:行号 - 消息
        formatted = (
            f"{color}[{datetime.now().strftime('%H:%M:%S')}] "
            f"[{record.levelname:8}] "
            f"[{request_id}] "
            f"{record.module}:{record.lineno} - "
            f"{record.getMessage()}{self.RESET}"
        )

        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted

def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: 是否使用 JSON 格式（生产环境推荐）
        log_file: 日志文件路径（可选）

    Returns:
        配置好的根日志器
    """
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除已有处理器
    root_logger.handlers.clear()

    # 选择格式化器
    formatter = JSONFormatter() if json_format else PrettyFormatter()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())  # 文件始终用 JSON
        root_logger.addHandler(file_handler)

    # 降低第三方库日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return root_logger

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)

def generate_request_id() -> str:
    """生成唯一请求ID"""
    return str(uuid.uuid4())

def set_request_context(
    request_id: str,
    user_id: Optional[int] = None,
    request_path: str = "-"
) -> None:
    """设置请求上下文"""
    request_id_var.set(request_id)
    user_id_var.set(user_id)
    request_path_var.set(request_path)

def clear_request_context() -> None:
    """清除请求上下文"""
    request_id_var.set("-")
    user_id_var.set(None)
    request_path_var.set("-")
