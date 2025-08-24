"""
錯誤處理工具模組。

提供各種錯誤處理和轉換功能。
"""

from typing import Any

from fastapi import HTTPException

from .constants import ErrorCode
from .exceptions import BusinessLogicError, DatabaseError, ValidationError


def create_http_exception_from_api_error(error: Any) -> HTTPException:
    """將 APIError 轉換為 HTTPException"""
    # 直接創建錯誤回應格式，避免循環導入
    error_detail = {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "status_code": error.status_code,
            "details": error.details,
        }
    }
    return HTTPException(status_code=error.status_code, detail=error_detail)


def create_user_not_found_error(user_id: int) -> BusinessLogicError:
    """創建使用者不存在錯誤"""
    message = f"使用者不存在: ID={user_id}"
    return BusinessLogicError(message, ErrorCode.USER_NOT_FOUND)


def create_schedule_not_found_error(schedule_id: int) -> BusinessLogicError:
    """創建時段不存在錯誤"""
    message = f"時段不存在: ID={schedule_id}"
    return BusinessLogicError(message, ErrorCode.SCHEDULE_NOT_FOUND)


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


def handle_database_error(error: Exception, operation: str) -> DatabaseError:
    """
    處理資料庫錯誤

    將一般異常轉換為 DatabaseError，並記錄操作上下文。

    Args:
        error: 原始錯誤
        operation: 操作描述

    Returns:
        DatabaseError: 格式化的資料庫錯誤
    """
    error_message = f"資料庫操作失敗 ({operation}): {str(error)}"
    return DatabaseError(
        error_message,
        {"operation": operation, "original_error": str(error)},
    )


def handle_business_logic_error(
    error: Exception, context: str, error_code: str | None = None
) -> BusinessLogicError:
    """
    處理業務邏輯錯誤

    將一般異常轉換為 BusinessLogicError，並記錄操作上下文。

    Args:
        error: 原始錯誤
        context: 操作上下文
        error_code: 錯誤代碼（可選）

    Returns:
        BusinessLogicError: 格式化的業務邏輯錯誤
    """
    error_message = f"業務邏輯錯誤 ({context}): {str(error)}"
    return BusinessLogicError(
        error_message,
        error_code or "BUSINESS_LOGIC_ERROR",
        {"context": context, "original_error": str(error)},
    )


def handle_validation_error(
    error: Exception, field: str, value: Any = None
) -> ValidationError:
    """
    處理驗證錯誤

    將一般異常轉換為 ValidationError，並記錄欄位資訊。

    Args:
        error: 原始錯誤
        field: 驗證失敗的欄位名稱
        value: 驗證失敗的值（可選）

    Returns:
        ValidationError: 格式化的驗證錯誤
    """
    error_message = f"驗證錯誤 ({field}): {str(error)}"
    details = {"field": field, "original_error": str(error)}
    if value is not None:
        details["value"] = str(value)

    return ValidationError(error_message, details)
