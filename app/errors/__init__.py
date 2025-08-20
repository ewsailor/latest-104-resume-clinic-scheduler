"""
錯誤處理模組。

提供統一的錯誤處理機制，包括錯誤類型定義、錯誤處理函式和格式化功能。
"""

from .constants import ErrorCode
from .exceptions import (
    APIError,
    BusinessLogicError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from .formatters import format_error_response, format_schedule_overlap_error_message
from .handlers import (
    create_http_exception_from_api_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_user_not_found_error,
    handle_database_error,
)

__all__ = [
    # 錯誤代碼
    "ErrorCode",
    # 錯誤類別
    "APIError",
    "ValidationError",
    "BusinessLogicError",
    "DatabaseError",
    "NotFoundError",
    # 錯誤處理函式
    "handle_database_error",
    "create_http_exception_from_api_error",
    "create_user_not_found_error",
    "create_schedule_not_found_error",
    "create_schedule_overlap_error",
    # 錯誤格式化
    "format_error_response",
    "format_schedule_overlap_error_message",
]
