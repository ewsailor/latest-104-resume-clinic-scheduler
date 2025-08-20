"""
錯誤處理工具模組。

提供統一的錯誤處理機制，包括錯誤類型定義和基本錯誤處理功能。
"""

import logging
from typing import Any

from fastapi import HTTPException, status

from app.utils.timezone import get_utc_timestamp

logger = logging.getLogger(__name__)


# ===== 錯誤代碼常數 =====
class ErrorCode:
    """錯誤代碼常數類別"""

    # 驗證錯誤
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 422 - 資料驗證失敗

    # 業務邏輯錯誤
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"  # 400 - 業務邏輯錯誤
    SCHEDULE_OVERLAP = "SCHEDULE_OVERLAP"  # 400 - 時段重疊
    USER_NOT_FOUND = "USER_NOT_FOUND"  # 404 - 使用者不存在
    SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"  # 404 - 時段不存在

    # 資料庫錯誤
    DATABASE_ERROR = "DATABASE_ERROR"  # 500 - 資料庫操作失敗

    # 系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - 內部伺服器錯誤


# ===== 錯誤類型定義 =====
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


# ===== 錯誤處理函數 =====
def format_error_response(error: Exception) -> dict[str, Any]:
    """
    格式化錯誤回應

    將不同類型的錯誤轉換為統一的錯誤回應格式，包含錯誤代碼、訊息、狀態碼、
    時間戳記和詳細資訊。支援 APIError、HTTPException 和其他一般異常。

    Args:
        error: 要格式化的錯誤物件

    Returns:
        包含格式化錯誤資訊的字典
    """
    logger.info(
        f"format_error_response: 開始格式化錯誤，錯誤類型: {type(error).__name__}"
    )

    # 處理自定義 APIError
    if isinstance(error, APIError):
        logger.debug(
            f"format_error_response: 處理 APIError，錯誤代碼: {error.error_code}"
        )
        return {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "status_code": error.status_code,
                "timestamp": get_utc_timestamp(),
                "details": error.details,
            }
        }

    # 處理 FastAPI HTTPException
    if isinstance(error, HTTPException):
        logger.debug(
            f"format_error_response: 處理 HTTPException，狀態碼: {error.status_code}"
        )
        # 從 HTTPException 的 detail 中提取訊息
        if error.detail:
            # 如果 detail 是字典，直接使用它作為 message
            if isinstance(error.detail, dict):
                detail_message: Any = error.detail
            else:
                # 如果 detail 是字串，使用它作為 message
                detail_message = str(error.detail)
        else:
            detail_message = "內部伺服器錯誤"

        return {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": detail_message,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "timestamp": get_utc_timestamp(),
                "details": {"detail": error.detail} if error.detail else {},
            }
        }

    # 處理 ValueError
    if isinstance(error, ValueError):
        logger.debug(f"format_error_response: 處理 ValueError")
        return {
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": str(error),
                "status_code": status.HTTP_400_BAD_REQUEST,
                "timestamp": get_utc_timestamp(),
                "details": {"validation_error": str(error)},
            }
        }

    # 處理其他未知錯誤
    logger.warning(f"format_error_response: 處理未知錯誤類型: {type(error).__name__}")
    return {
        "error": {
            "code": ErrorCode.INTERNAL_ERROR,
            "message": "內部伺服器錯誤",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": get_utc_timestamp(),
            "details": {"error": str(error)},
        }
    }


def handle_database_error(error: Exception, operation: str) -> DatabaseError:
    """處理資料庫錯誤"""
    error_message = f"資料庫操作失敗 ({operation}): {str(error)}"
    return DatabaseError(
        error_message,
        {"operation": operation, "original_error": str(error)},
    )


def create_http_exception_from_api_error(error: APIError) -> HTTPException:
    """將 APIError 轉換為 HTTPException"""
    return HTTPException(
        status_code=error.status_code, detail=format_error_response(error)
    )


# ===== 常用錯誤工廠函數 =====
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


def format_schedule_overlap_error_message(
    overlapping_schedules: list[Any],
    schedule_date: Any,
    context: str = "建立",
) -> str:
    """格式化重疊時段的錯誤訊息"""
    try:
        # 格式化日期為中文格式
        weekday_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
        weekday = weekday_names[schedule_date.weekday()]
        date_str = schedule_date.strftime("%Y/%m/%d")

        overlapping_info = []
        for schedule in overlapping_schedules:
            time_info = f"{schedule.start_time.strftime('%H:%M')}-{schedule.end_time.strftime('%H:%M')}"
            overlapping_info.append(f"{date_str}（{weekday}） {time_info}")

        return f"您正輸入的時段，和您之前曾輸入的「{', '.join(overlapping_info)}」時段重複或重疊，請重新輸入"
    except Exception as e:
        logger.warning(f"格式化重疊錯誤訊息失敗: {e}")
        return "時段重疊，請檢查時間安排"
