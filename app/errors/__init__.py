"""
錯誤處理模組。

提供統一的錯誤處理機制，包括錯誤類型定義、錯誤處理函式和格式化功能。
"""

# ===== 本地模組 =====
from .constants import (
    CORSErrorCode,
    CRUDErrorCode,
    ErrorCode,
    RouterErrorCode,
    ServiceErrorCode,
    SystemErrorCode,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from .formatters import format_error_response
from .handlers import (
    create_http_exception_from_api_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_user_not_found_error,
    handle_business_logic_error,
    handle_database_error,
    handle_validation_error,
)

__all__ = [
    # 錯誤代碼
    "ErrorCode",
    "RouterErrorCode",
    "ServiceErrorCode",
    "CRUDErrorCode",
    "CORSErrorCode",
    "SystemErrorCode",
    # 錯誤類別
    "APIError",
    "ValidationError",
    "BusinessLogicError",
    "DatabaseError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ServiceUnavailableError",
    # 錯誤處理函式
    "handle_database_error",
    "handle_business_logic_error",
    "handle_validation_error",
    "create_http_exception_from_api_error",
    "create_user_not_found_error",
    "create_schedule_not_found_error",
    "create_schedule_overlap_error",
    # 錯誤格式化
    "format_error_response",
]
