"""
錯誤處理函式模組。

提供常用的錯誤處理和創建函式。
"""

from typing import Any

from fastapi import HTTPException

from .constants import ErrorCode
from .exceptions import BusinessLogicError, DatabaseError, NotFoundError
from .formatters import format_error_response


def handle_database_error(error: Exception, operation: str) -> DatabaseError:
    """處理資料庫錯誤"""
    error_message = f"資料庫操作失敗 ({operation}): {str(error)}"
    return DatabaseError(
        error_message,
        {"operation": operation, "original_error": str(error)},
    )


def create_http_exception_from_api_error(error: Any) -> HTTPException:
    """將 APIError 轉換為 HTTPException"""
    return HTTPException(
        status_code=error.status_code, detail=format_error_response(error)
    )


def create_user_not_found_error(user_id: int) -> NotFoundError:
    """創建使用者不存在錯誤"""
    return NotFoundError("使用者", user_id)


def create_schedule_not_found_error(schedule_id: int) -> NotFoundError:
    """創建時段不存在錯誤"""
    return NotFoundError("時段", schedule_id)


def create_schedule_overlap_error(
    overlapping_schedules: list[Any], schedule_date: str
) -> BusinessLogicError:
    """創建時段重疊錯誤"""
    return BusinessLogicError(
        message="時段重疊",
        error_code=ErrorCode.SCHEDULE_OVERLAP,
        details={
            "overlapping_schedules": overlapping_schedules,
            "schedule_date": schedule_date,
        },
    )
