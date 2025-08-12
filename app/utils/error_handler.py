"""
錯誤處理工具模組。

提供統一的錯誤處理機制，包括錯誤類型定義、錯誤回應格式化和錯誤日誌記錄。
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status
from pydantic import ValidationError as PydanticValidationError

from app.utils.timezone import get_utc_timestamp

# 設定 logger
logger = logging.getLogger(__name__)


class ErrorCode:
    """錯誤代碼常數類別"""

    # 驗證錯誤
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # 業務邏輯錯誤
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    SCHEDULE_OVERLAP = "SCHEDULE_OVERLAP"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"
    GIVER_NOT_FOUND = "GIVER_NOT_FOUND"
    INVALID_STATUS_TRANSITION = "INVALID_STATUS_TRANSITION"

    # 資料庫錯誤
    DATABASE_ERROR = "DATABASE_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TRANSACTION_ERROR = "TRANSACTION_ERROR"

    # 認證授權錯誤
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # 系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class APIError(Exception):
    """API 錯誤基礎類別"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.context = context
        super().__init__(self.message)


class ValidationError(APIError):
    """資料驗證錯誤"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class BusinessLogicError(APIError):
    """業務邏輯錯誤"""

    def __init__(
        self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class DatabaseError(APIError):
    """資料庫錯誤"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class AuthenticationError(APIError):
    """認證錯誤"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(APIError):
    """授權錯誤"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(APIError):
    """資源不存在錯誤"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Union[int, str],
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource_type}不存在: ID={resource_id}"
        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


def format_error_response(
    error: Exception, include_traceback: bool = False, request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    格式化錯誤回應。

    Args:
        error: 錯誤物件
        include_traceback: 是否包含堆疊追蹤（僅在開發環境）
        request_id: 請求 ID（用於追蹤）

    Returns:
        Dict[str, Any]: 格式化的錯誤回應
    """
    if isinstance(error, APIError):
        error_response = {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "status_code": error.status_code,
                "timestamp": get_utc_timestamp(),
                "request_id": request_id,
            }
        }

        if error.details:
            error_response["error"]["details"] = error.details

        if error.context:
            error_response["error"]["context"] = error.context

    elif isinstance(error, PydanticValidationError):
        error_response = {
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "資料驗證失敗",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "timestamp": get_utc_timestamp(),
                "request_id": request_id,
                "details": error.errors() if hasattr(error, 'errors') else str(error),
            }
        }

    elif isinstance(error, HTTPException):
        error_response = {
            "error": {
                "code": "HTTP_ERROR",
                "message": error.detail,
                "status_code": error.status_code,
                "timestamp": get_utc_timestamp(),
                "request_id": request_id,
            }
        }

    else:
        # 未知錯誤
        error_response = {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "內部伺服器錯誤",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "timestamp": get_utc_timestamp(),
                "request_id": request_id,
            }
        }

        # 僅在開發環境包含詳細錯誤資訊
        if include_traceback:
            error_response["error"]["details"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

    return error_response


def log_error(
    error: Exception,
    context: str = "API",
    request_info: Optional[Dict[str, Any]] = None,
    user_info: Optional[Dict[str, Any]] = None,
) -> None:
    """
    記錄錯誤資訊。

    Args:
        error: 錯誤物件
        context: 錯誤上下文
        request_info: 請求資訊
        user_info: 使用者資訊
    """
    error_data: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }

    if request_info:
        error_data["request"] = request_info

    if user_info:
        error_data["user"] = user_info

    # 根據錯誤類型選擇適當的日誌級別
    if isinstance(error, (ValidationError, BusinessLogicError)):
        logger.warning(f"{context} 錯誤: {str(error_data)}")
    elif isinstance(error, (AuthenticationError, AuthorizationError)):
        logger.warning(f"{context} 認證/授權錯誤: {str(error_data)}")
    elif isinstance(error, NotFoundError):
        logger.info(f"{context} 資源不存在: {str(error_data)}")
    else:
        logger.error(f"{context} 系統錯誤: {str(error_data)}")


def handle_database_error(error: Exception, operation: str) -> DatabaseError:
    """
    處理資料庫錯誤。

    Args:
        error: 原始錯誤
        operation: 操作描述

    Returns:
        DatabaseError: 格式化的資料庫錯誤
    """
    error_message = f"資料庫操作失敗 ({operation}): {str(error)}"

    # 根據錯誤類型提供更具體的錯誤訊息
    if "connection" in str(error).lower():
        error_message = f"資料庫連線失敗 ({operation})"
    elif "transaction" in str(error).lower():
        error_message = f"資料庫交易失敗 ({operation})"
    else:
        error_message = f"資料庫操作失敗 ({operation}): {str(error)}"

    return DatabaseError(
        error_message, {"operation": operation, "original_error": str(error)}
    )


def handle_validation_error(
    error: PydanticValidationError, context: str = "資料驗證"
) -> ValidationError:
    """
    處理 Pydantic 驗證錯誤。

    Args:
        error: Pydantic 驗證錯誤
        context: 錯誤上下文

    Returns:
        ValidationError: 格式化的驗證錯誤
    """
    error_details = []

    for validation_error in error.errors():
        detail = {
            "field": " -> ".join(str(loc) for loc in validation_error["loc"]),
            "message": validation_error["msg"],
            "type": validation_error["type"],
        }
        error_details.append(detail)

    return ValidationError(
        message=f"{context}失敗", details={"validation_errors": error_details}
    )


def create_http_exception_from_api_error(error: APIError) -> HTTPException:
    """
    將 APIError 轉換為 HTTPException。

    Args:
        error: APIError 實例

    Returns:
        HTTPException: FastAPI HTTPException
    """
    return HTTPException(
        status_code=error.status_code, detail=format_error_response(error)
    )


def safe_execute(
    func,
    *args,
    error_context: str = "操作",
    default_error_message: str = "操作失敗",
    **kwargs,
):
    """
    安全執行函數，提供統一的錯誤處理。

    Args:
        func: 要執行的函數
        *args: 函數參數
        error_context: 錯誤上下文
        default_error_message: 預設錯誤訊息
        **kwargs: 函數關鍵字參數

    Returns:
        函數執行結果

    Raises:
        APIError: 當執行失敗時
    """
    try:
        return func(*args, **kwargs)
    except APIError:
        # 重新拋出 APIError
        raise
    except PydanticValidationError as e:
        # 處理 Pydantic 驗證錯誤
        raise handle_validation_error(e, error_context)
    except Exception as e:
        # 記錄錯誤
        log_error(e, context=error_context)

        # 拋出通用錯誤
        raise APIError(
            message=f"{error_context}失敗: {default_error_message}",
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"original_error": str(e)},
        )


# 常用錯誤工廠函數
def create_schedule_overlap_error(
    overlapping_schedules: list, schedule_date: str
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


def create_user_not_found_error(user_id: int) -> NotFoundError:
    """創建使用者不存在錯誤"""
    return NotFoundError("使用者", user_id)


def create_schedule_not_found_error(schedule_id: int) -> NotFoundError:
    """創建時段不存在錯誤"""
    return NotFoundError("時段", schedule_id)


def create_giver_not_found_error(giver_id: int) -> NotFoundError:
    """創建諮詢師不存在錯誤"""
    return NotFoundError("諮詢師", giver_id)


def create_invalid_status_transition_error(
    current_status: str, target_status: str, allowed_transitions: list
) -> BusinessLogicError:
    """創建無效狀態轉換錯誤"""
    return BusinessLogicError(
        message="無效的狀態轉換",
        error_code=ErrorCode.INVALID_STATUS_TRANSITION,
        details={
            "current_status": current_status,
            "target_status": target_status,
            "allowed_transitions": allowed_transitions,
        },
    )
