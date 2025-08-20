"""
錯誤格式化模組。

提供錯誤訊息的格式化功能。
"""

import logging
from typing import Any

from fastapi import HTTPException, status

from app.utils.timezone import get_utc_timestamp

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
