"""
錯誤格式化模組。

提供錯誤訊息的格式化功能。
"""

# ===== 標準函式庫 =====
import logging
from typing import Any

# ===== 第三方套件 =====
from fastapi import HTTPException, status

# ===== 本地模組 =====
# 絕對路徑導入（跨模組）
from app.utils.timezone import get_utc_timestamp

# 相對路徑導入（同模組）
from .constants import ErrorCode
from .exceptions import APIError

logger = logging.getLogger(__name__)


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

        # 根據狀態碼和錯誤訊息決定錯誤代碼
        if error.status_code == 409:
            # 409 通常是資源衝突
            error_code = ErrorCode.CONFLICT
        elif error.status_code == 404:
            # 404 需要根據錯誤訊息判斷是使用者還是時段
            if "使用者" in str(error.detail):
                error_code = ErrorCode.USER_NOT_FOUND
            elif "時段" in str(error.detail):
                error_code = ErrorCode.SCHEDULE_NOT_FOUND
            else:
                error_code = ErrorCode.USER_NOT_FOUND  # 預設
        elif error.status_code == 422:
            error_code = ErrorCode.VALIDATION_ERROR
        elif error.status_code == 400:
            error_code = ErrorCode.BAD_REQUEST
        else:
            error_code = ErrorCode.INTERNAL_ERROR

        return {
            "error": {
                "code": error_code,
                "message": detail_message,
                "status_code": error.status_code,
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
