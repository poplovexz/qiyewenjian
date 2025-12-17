"""
统一异常处理器

将所有异常转换为统一格式的 API 响应
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError

from core.exceptions import BaseCustomException
from core.error_codes import ErrorCode
from core.logging import get_logger, request_id_var

logger = get_logger(__name__)


def create_error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: dict = None
) -> JSONResponse:
    """
    创建统一格式的错误响应

    响应格式:
    {
        "success": false,
        "error": {
            "code": "110001",
            "message": "认证失败",
            "details": {...},
            "request_id": "abc-123"
        }
    }
    """
    error_body = {
        "code": error_code,
        "message": message,
        "request_id": request_id_var.get()
    }

    if details:
        error_body["details"] = details

    response = JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error_body
        }
    )

    # 添加 CORS 头
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Expose-Headers"] = "*"

    return response


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """处理自定义业务异常"""
    logger.warning(
        f"业务异常: [{exc.error_code}] {exc.message}",
        extra={"extra_data": {
            "error_code": exc.error_code,
            "details": exc.details,
            "path": str(request.url.path)
        }}
    )

    return create_error_response(
        request=request,
        status_code=exc.http_status,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details if exc.details else None
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理 FastAPI HTTPException"""
    # 映射 HTTP 状态码到错误码
    error_code_map = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.AUTH_FAILED,
        403: ErrorCode.PERMISSION_DENIED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        405: ErrorCode.METHOD_NOT_ALLOWED,
        409: ErrorCode.RESOURCE_CONFLICT,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }

    error_info = error_code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR)

    # 使用异常详情作为消息，如果是字符串的话
    message = exc.detail if isinstance(exc.detail, str) else error_info.message

    logger.warning(
        f"HTTP异常: {exc.status_code} - {message}",
        extra={"extra_data": {"path": str(request.url.path)}}
    )

    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=error_info.code,
        message=message
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理 Pydantic 验证错误"""
    # 格式化验证错误
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field": field,
            "message": error.get("msg", "验证失败"),
            "type": error.get("type", "unknown")
        })

    logger.warning(
        f"数据验证失败: {len(errors)} 个错误",
        extra={"extra_data": {
            "errors": errors,
            "path": str(request.url.path)
        }}
    )

    return create_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=ErrorCode.VALIDATION_ERROR.code,
        message="数据验证失败",
        details={"errors": errors}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常"""
    logger.error(
        f"未捕获异常: {type(exc).__name__}: {str(exc)[:200]}",
        exc_info=True,
        extra={"extra_data": {
            "exception_type": type(exc).__name__,
            "path": str(request.url.path),
            "method": request.method
        }}
    )

    return create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_ERROR.code,
        message="服务器内部错误，请稍后重试"
    )

