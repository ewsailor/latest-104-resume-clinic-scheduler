"""
錯誤處理工具模組。

提供統一的錯誤處理機制，包括錯誤類型定義、錯誤回應格式化和錯誤日誌記錄。

架構說明：
- 此模組作為整個應用程式的錯誤處理核心
- 所有其他模組（routers、crud、middleware）都應該使用此模組的錯誤類型
- 不建議在其他資料夾創建獨立的 error_handler.py
- 如需特定業務邏輯錯誤，應在此模組中擴展，而不是創建新的錯誤處理模組

使用方式：
1. 在路由層：使用預定義的錯誤類型（如 NotFoundError、BusinessLogicError）
2. 在業務邏輯層：使用 safe_execute 函數包裝可能出錯的操作
3. 在中間件層：使用 format_error_response 格式化錯誤回應
"""

# ===== 標準函式庫 =====
import logging  # 日誌記錄
import traceback
from datetime import datetime  # 日期時間處理
from typing import Any, Union  # 保留這些，因為它們沒有內建替代

# ===== 第三方套件 =====
from fastapi import HTTPException, status
from pydantic import ValidationError as PydanticValidationError

from app.schemas.schedule import ScheduleResponse
from app.utils.timezone import get_utc_timestamp

# 設定 logger
logger = logging.getLogger(__name__)


# ===== 錯誤訊息常數 =====
class ErrorMessages:
    """錯誤訊息常數類別

    集中管理所有錯誤訊息，避免重複定義和維護困難
    """

    # 時段相關錯誤訊息
    SCHEDULE_CREATE_FAILED = "建立時段時發生內部錯誤"
    SCHEDULE_LIST_QUERY_FAILED = "查詢時段列表失敗"
    SCHEDULE_DETAIL_QUERY_FAILED = "查詢單一時段失敗"
    SCHEDULE_UPDATE_FAILED = "更新時段失敗"
    SCHEDULE_DELETE_FAILED = "刪除時段失敗"

    # 使用者相關錯誤訊息
    USER_QUERY_FAILED = "查詢使用者失敗"
    USER_CREATE_FAILED = "建立使用者失敗"
    USER_UPDATE_FAILED = "更新使用者失敗"
    USER_DELETE_FAILED = "刪除使用者失敗"

    # 通用錯誤訊息
    DATABASE_OPERATION_FAILED = "資料庫操作失敗"
    VALIDATION_FAILED = "資料驗證失敗"
    AUTHENTICATION_FAILED = "認證失敗"
    AUTHORIZATION_FAILED = "授權失敗"


# ===== 錯誤代碼常數 =====
class ErrorCode:
    """錯誤代碼常數類別

    注意：所有錯誤代碼都應在此處定義，避免在其他模組中重複定義
    """

    # 驗證錯誤 (422)
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 422 - 資料驗證失敗
    INVALID_INPUT = "INVALID_INPUT"  # 422 - 無效輸入
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"  # 422 - 缺少必要欄位

    # 業務邏輯錯誤 (400)
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"  # 400 - 業務邏輯錯誤
    SCHEDULE_OVERLAP = "SCHEDULE_OVERLAP"  # 400 - 時段重疊
    USER_NOT_FOUND = "USER_NOT_FOUND"  # 404 - 使用者不存在
    SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"  # 404 - 時段不存在
    GIVER_NOT_FOUND = "GIVER_NOT_FOUND"  # 404 - 諮詢師不存在
    INVALID_STATUS_TRANSITION = "INVALID_STATUS_TRANSITION"  # 400 - 無效狀態轉換

    # 資料庫錯誤 (500)
    DATABASE_ERROR = "DATABASE_ERROR"  # 500 - 資料庫錯誤
    CONNECTION_ERROR = "CONNECTION_ERROR"  # 500 - 資料庫連線錯誤
    TRANSACTION_ERROR = "TRANSACTION_ERROR"  # 500 - 資料庫交易錯誤

    # 認證授權錯誤
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"  # 401 - 認證錯誤
    UNAUTHORIZED = "UNAUTHORIZED"  # 401 - 未授權
    FORBIDDEN = "FORBIDDEN"  # 403 - 禁止訪問
    INVALID_TOKEN = "INVALID_TOKEN"  # 401 - 無效 Token
    TOKEN_EXPIRED = "TOKEN_EXPIRED"  # 401 - Token 過期

    # 系統錯誤
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - 內部伺服器錯誤
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"  # 502 - 外部服務錯誤
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"  # 429 - 請求頻率超限
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 503 - 服務不可用

    # HTTP 標準錯誤
    BAD_REQUEST = "BAD_REQUEST"  # 400 - 請求格式錯誤
    NOT_FOUND = "NOT_FOUND"  # 404 - 資源不存在
    CONFLICT = "CONFLICT"  # 409 - 資源衝突


# ===== 錯誤類型定義 =====


class APIError(Exception):
    """API 錯誤基礎類別"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
        context: str | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.context = context
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


class AuthenticationError(APIError):
    """認證錯誤"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(APIError):
    """授權錯誤"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(APIError):
    """資源不存在錯誤"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Union[int, str],
        details: dict[str, Any] | None = None,
    ):
        message = f"{resource_type}不存在: ID={resource_id}"
        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


def format_error_response(
    error: Exception, include_traceback: bool = False, request_id: str | None = None
) -> dict[str, Any]:
    """
    格式化錯誤回應。

    Args:
        error: 錯誤物件
        include_traceback: 是否包含堆疊追蹤（僅在開發環境）
        request_id: 請求 ID（用於追蹤）

    Returns:
        dict[str, Any]: 格式化的錯誤回應
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
    request_info: dict[str, Any] | None = None,
    user_info: dict[str, Any] | None = None,
) -> None:
    """
    記錄錯誤資訊。

    Args:
        error: 錯誤物件
        context: 錯誤上下文
        request_info: 請求資訊
        user_info: 使用者資訊
    """
    error_data: dict[str, Any] = {
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
    error_str = str(error).lower()

    # 根據錯誤類型提供更具體的錯誤訊息和代碼
    if "connection" in error_str:
        error_message = f"資料庫連線失敗 ({operation})"
        error_code = ErrorCode.CONNECTION_ERROR
    elif "transaction" in error_str:
        error_message = f"資料庫交易失敗 ({operation})"
        error_code = ErrorCode.TRANSACTION_ERROR
    else:
        error_message = f"資料庫操作失敗 ({operation}): {str(error)}"
        error_code = ErrorCode.DATABASE_ERROR

    return DatabaseError(
        error_message,
        {"operation": operation, "original_error": str(error)},
        error_code=error_code,
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


# ===== OpenAPI 回應定義 =====
#
# 架構設計理念：
# 1. get_common_error_responses(): 定義所有 API 都可能遇到的通用錯誤（401、403、422、500、503等）
# 2. get_*_specific_error_responses(): 定義特定業務模組特有的錯誤（如時段重疊、使用者不存在等）
# 3. get_*_error_responses(): 組合通用錯誤和特定錯誤，提供完整的錯誤回應定義
# 4. get_*_*_responses(): 組合成功回應和錯誤回應，提供完整的 API 回應定義
#
# 使用方式：
# - 簡單的 API（如列表查詢）：使用 get_common_error_responses()
# - 複雜的 API（如建立、更新、刪除）：使用 get_*_error_responses()
# - 避免重複定義相同的錯誤回應


def get_schedule_example_data() -> dict[str, Any]:
    """取得時段範例資料"""
    return {
        "id": 17,
        "giver_id": 1,
        "taker_id": None,
        "status": "AVAILABLE",
        "date": "2025-08-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "note": "線上討論履歷",
        "created_at": "2025-07-27T09:12:00",
        "created_by": 1,
        "created_by_role": "GIVER",
        "updated_at": "2025-07-27T09:12:00",
        "updated_by": 1,
        "updated_by_role": "GIVER",
        "deleted_at": None,
        "deleted_by": None,
        "deleted_by_role": None,
    }


def get_schedule_list_example() -> list[dict[str, Any]]:
    """取得時段列表範例資料"""
    return [get_schedule_example_data()]


def get_common_error_responses() -> dict[int, dict[str, Any]]:
    """
    取得通用錯誤回應定義，包含所有 API 都可能遇到的錯誤

    400 錯誤範例包括：
    - BAD_REQUEST: 請求格式錯誤或業務邏輯錯誤
    401 錯誤範例包括：
    - UNAUTHORIZED: 未授權，如未提供 JWT、尚未登入
    403 錯誤範例包括：
    - FORBIDDEN: 禁止訪問，如權限不足
    404 錯誤範例包括：
    - NOT_FOUND: 資源不存在
    409 錯誤範例包括：
    - CONFLICT: 資源衝突，如時段重疊
    422 錯誤範例包括：
    - VALIDATION_ERROR: 資料驗證失敗
    500 錯誤範例包括：
    - INTERNAL_ERROR: 伺服器內部錯誤
    503 錯誤範例包括：
    - SERVICE_UNAVAILABLE: 服務不可用，如維護或超載
    """
    return {
        400: {
            "description": "請求格式錯誤或業務邏輯錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "BAD_REQUEST",
                            "message": "請求格式錯誤或業務邏輯錯誤",
                            "status_code": 400,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        401: {
            "description": "未授權，如未提供 JWT、尚未登入",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "未授權，請先登入",
                            "status_code": 401,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        403: {
            "description": "禁止訪問，如權限不足",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "權限不足，無法執行此操作",
                            "status_code": 403,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        404: {
            "description": "資源不存在",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "NOT_FOUND",
                            "message": "請求的資源不存在",
                            "status_code": 404,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        409: {
            "description": "資源衝突，如時段重疊",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "CONFLICT",
                            "message": "資源衝突，如時段重疊",
                            "status_code": 409,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        422: {
            "description": "請求語義錯誤、Pydantic 資料驗證失敗",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "資料驗證失敗",
                            "status_code": 422,
                            "timestamp": "2025-07-27T09:12:00Z",
                            "details": {
                                "validation_errors": [
                                    {
                                        "field": "email",
                                        "message": "無效的電子郵件格式",
                                        "type": "value_error.email",
                                    }
                                ]
                            },
                        }
                    }
                }
            },
        },
        500: {
            "description": "伺服器內部錯誤，如資料庫錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "message": "伺服器內部錯誤",
                            "status_code": 500,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        503: {
            "description": "服務不可用，如維護或超載",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "SERVICE_UNAVAILABLE",
                            "message": "服務暫時不可用，請稍後再試",
                            "status_code": 503,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
    }


def get_schedule_specific_error_responses() -> dict[int, dict[str, Any]]:
    """取得時段特有的錯誤回應定義

    400 錯誤範例包括：
    - INVALID_STATUS_TRANSITION: 無效狀態轉換
    - 時間邏輯錯誤: 結束時間早於開始時間
    - 日期限制錯誤: 建立過去的時段
    404 錯誤範例包括：
    - 使用者不存在
    - 時段不存在
    409 錯誤範例包括：
    - 時段重疊
    """
    return {
        400: {
            "description": "時段業務邏輯錯誤",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "INVALID_STATUS_TRANSITION",
                            "message": "無效的狀態轉換",
                            "status_code": 400,
                            "timestamp": "2025-07-27T09:12:00Z",
                            "details": {
                                "current_status": "BOOKED",
                                "target_status": "AVAILABLE",
                                "allowed_transitions": ["CANCELLED", "COMPLETED"],
                                "message": "已預約的時段無法直接設為可預約狀態",
                            },
                        }
                    }
                }
            },
        },
        404: {
            "description": "時段不存在",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "SCHEDULE_NOT_FOUND",
                            "message": "時段不存在: ID=17",
                            "status_code": 404,
                            "timestamp": "2025-07-27T09:12:00Z",
                        }
                    }
                }
            },
        },
        409: {
            "description": "時段重疊衝突",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "SCHEDULE_OVERLAP",
                            "message": "時段重疊",
                            "status_code": 409,
                            "timestamp": "2025-07-27T09:12:00Z",
                            "details": {
                                "overlapping_schedules": [
                                    {
                                        "id": 15,
                                        "date": "2025-08-01",
                                        "start_time": "10:00:00",
                                        "end_time": "11:00:00",
                                    }
                                ],
                                "schedule_date": "2025-08-01",
                            },
                        }
                    }
                }
            },
        },
    }


def get_schedule_error_responses() -> dict[int, dict[str, Any]]:
    """取得時段相關錯誤回應定義（包含通用錯誤和時段特有錯誤）"""
    return get_schedule_specific_error_responses() | get_common_error_responses()


def get_schedule_create_responses() -> dict[int, dict[str, Any]]:
    """取得建立時段的完整回應定義"""
    return {
        201: {
            "description": "成功建立時段",
            "model": list[ScheduleResponse],
            "content": {"application/json": {"example": get_schedule_list_example()}},
        }
    } | get_schedule_error_responses()


def get_schedule_list_responses() -> dict[int, dict[str, Any]]:
    """取得時段列表的完整回應定義"""
    return {
        200: {
            "description": "成功取得時段列表",
            "model": list[ScheduleResponse],
            "content": {"application/json": {"example": get_schedule_list_example()}},
        }
    } | get_common_error_responses()


def get_schedule_detail_responses() -> dict[int, dict[str, Any]]:
    """取得單一時段的完整回應定義"""
    return {
        200: {
            "description": "成功取得時段資料",
            "model": ScheduleResponse,
            "content": {"application/json": {"example": get_schedule_example_data()}},
        }
    } | get_schedule_error_responses()


def get_schedule_update_responses() -> dict[int, dict[str, Any]]:
    """取得更新時段的完整回應定義"""
    return {
        200: {
            "description": "成功更新時段",
            "model": ScheduleResponse,
            "content": {"application/json": {"example": get_schedule_example_data()}},
        }
    } | get_schedule_error_responses()


def get_schedule_delete_responses() -> dict[int, dict[str, Any]]:
    """取得刪除時段的完整回應定義"""
    return {204: {"description": "成功刪除時段"}} | get_schedule_error_responses()
