"""
錯誤類別模組。

定義系統中使用的所有錯誤類別。
"""

# ===== 標準函式庫 =====
from typing import Any

# ===== 第三方套件 =====
from fastapi import status

# ===== 本地模組 =====
from .constants import ErrorCode


class APIError(Exception):
    """API 錯誤基礎類別"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """資料驗證錯誤"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class BusinessLogicError(APIError):
    """業務邏輯錯誤"""

    def __init__(
        self, message: str, error_code: str, details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class DatabaseError(APIError):
    """資料庫錯誤"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        error_code: str = ErrorCode.DATABASE_ERROR,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class NotFoundError(APIError):
    """資源不存在錯誤"""

    def __init__(self, resource_type: str, resource_id: int | str):
        message = f"{resource_type}不存在: ID={resource_id}"
        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AuthenticationError(APIError):
    """認證錯誤"""

    def __init__(
        self, message: str = "認證失敗", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(APIError):
    """權限錯誤"""

    def __init__(
        self, message: str = "權限不足", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ConflictError(APIError):
    """資源衝突錯誤"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ServiceUnavailableError(APIError):
    """服務不可用錯誤"""

    def __init__(
        self, message: str = "服務暫時不可用", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.SYSTEM.SERVICE_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )
