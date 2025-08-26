"""
錯誤處理模組。

提供統一的錯誤處理機制，包括錯誤類型定義、錯誤處理函式和格式化功能。
"""

from .error_codes.cors import CORSErrorCode
from .error_codes.crud import CRUDErrorCode

# ===== 本地模組 =====
from .error_codes.router import RouterErrorCode
from .error_codes.service import ServiceErrorCode
from .error_codes.system import SystemErrorCode
from .exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    LivenessCheckError,
    ReadinessCheckError,
    ScheduleNotFoundError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from .formatters import format_error_response
from .handlers import (
    create_business_logic_error,
    create_database_error,
    create_liveness_check_error,
    create_readiness_check_error,
    create_schedule_not_found_error,
    create_schedule_overlap_error,
    create_service_unavailable_error,
    create_user_not_found_error,
)

__all__ = [
    # 錯誤代碼
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
    "ScheduleNotFoundError",
    "UserNotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ServiceUnavailableError",
    "LivenessCheckError",
    "ReadinessCheckError",
    # 錯誤處理函式
    # Service 層級
    "create_schedule_not_found_error",
    "create_user_not_found_error",
    "create_schedule_overlap_error",
    "create_business_logic_error",
    # CRUD 層級
    "create_database_error",
    # System 層級
    "create_liveness_check_error",
    "create_readiness_check_error",
    "create_service_unavailable_error",
    # 錯誤格式化
    "format_error_response",
]
