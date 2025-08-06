"""
時區處理工具模組。

提供時區轉換和本地時間處理的實用函數。
"""

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# 台灣時區 (UTC+8)
TAIWAN_TIMEZONE = timezone(timedelta(hours=8))


def get_local_now() -> datetime:
    """
    取得當前本地時間（台灣時間）。

    Returns:
        datetime: 當前本地時間，包含時區資訊
    """
    return datetime.now(TAIWAN_TIMEZONE)


def get_local_now_naive() -> datetime:
    """
    取得當前本地時間（台灣時間），不包含時區資訊。

    Returns:
        datetime: 當前本地時間，不包含時區資訊
    """
    return datetime.now(TAIWAN_TIMEZONE).replace(tzinfo=None)


def format_datetime_for_display(dt: datetime) -> str:
    """
    格式化日期時間為顯示字串。

    Args:
        dt: 要格式化的日期時間

    Returns:
        str: 格式化後的日期時間字串
    """
    if dt is None:
        return None

    # 如果沒有時區資訊，假設為 UTC
    if dt.tzinfo is None:
        logger.warning(f"輸入時間沒有時區資訊，假設為 UTC: {dt}")
        dt = dt.replace(tzinfo=timezone.utc)

    # 轉換為台灣時間
    taiwan_time = dt.astimezone(TAIWAN_TIMEZONE)

    # 格式化為字串
    return taiwan_time.strftime("%Y-%m-%d %H:%M:%S")


def convert_utc_to_local(utc_dt: datetime) -> datetime:
    """
    將 UTC 時間轉換為本地時間。

    Args:
        utc_dt: UTC 時間

    Returns:
        datetime: 本地時間
    """
    if utc_dt is None:
        return None

    # 如果沒有時區資訊，假設為 UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    return utc_dt.astimezone(TAIWAN_TIMEZONE)


def convert_local_to_utc(local_dt: datetime) -> datetime:
    """
    將本地時間轉換為 UTC 時間。

    Args:
        local_dt: 本地時間

    Returns:
        datetime: UTC 時間
    """
    if local_dt is None:
        return None

    # 如果沒有時區資訊，假設為本地時間
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=TAIWAN_TIMEZONE)

    return local_dt.astimezone(timezone.utc)
