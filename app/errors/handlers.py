"""
錯誤處理工具模組。

提供各種錯誤處理和轉換功能。
"""

# ===== 標準函式庫 =====
from typing import Any

# ===== 第三方套件 =====
from fastapi import HTTPException

# ===== 本地模組 =====
from .exceptions import (
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    ScheduleNotFoundError,
    UserNotFoundError,
    ValidationError,
)


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


def create_user_not_found_error(user_id: int) -> UserNotFoundError:
    """創建使用者不存在錯誤 (Service 層級)"""
    return UserNotFoundError(user_id)


def create_schedule_not_found_error(schedule_id: int) -> ScheduleNotFoundError:
    """創建時段不存在錯誤 (Service 層級)"""
    return ScheduleNotFoundError(schedule_id)


def create_schedule_overlap_error(
    overlapping_schedules: list[Any], schedule_date: str
) -> ConflictError:
    """創建時段重疊錯誤 (Service 層級)"""
    return ConflictError(
        message="時段重疊",
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


def handle_business_logic_error(error: Exception, context: str) -> BusinessLogicError:
    """
    處理業務邏輯錯誤

    將一般異常轉換為 BusinessLogicError，並記錄操作上下文。

    Args:
        error: 原始錯誤
        context: 操作上下文

    Returns:
        BusinessLogicError: 格式化的業務邏輯錯誤
    """
    error_message = f"業務邏輯錯誤 ({context}): {str(error)}"
    return BusinessLogicError(
        error_message,
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
