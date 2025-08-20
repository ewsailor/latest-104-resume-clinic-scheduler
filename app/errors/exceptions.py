"""
錯誤類別模組。

定義系統中使用的所有錯誤類別。
"""

from typing import Any

from fastapi import status

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
