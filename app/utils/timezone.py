"""
時區處理工具模組。

提供時區轉換和本地時間處理的實用函數。
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

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


def parse_datetime_from_display(display_str: str) -> Optional[datetime]:
    """
    從顯示字串解析日期時間。

    Args:
        display_str: 顯示格式的日期時間字串 (YYYY-MM-DD HH:MM:SS)

    Returns:
        Optional[datetime]: 解析後的 UTC 日期時間，解析失敗時返回 None
    """
    if not display_str:
        return None

    try:
        # 解析本地時間字串
        local_dt = datetime.strptime(display_str, "%Y-%m-%d %H:%M:%S")
        # 轉換為 UTC
        return convert_local_to_utc(local_dt)
    except ValueError as e:
        logger.error(f"解析日期時間字串失敗: {display_str}, 錯誤: {e}")
        return None


def convert_utc_to_local(utc_dt: datetime) -> Optional[datetime]:
    """
    將 UTC 時間轉換為本地時間。

    Args:
        utc_dt: UTC 時間

    Returns:
        Optional[datetime]: 本地時間，輸入為 None 時返回 None
    """
    if utc_dt is None:
        return None

    # 如果沒有時區資訊，假設為 UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    return utc_dt.astimezone(TAIWAN_TIMEZONE)


def convert_local_to_utc(local_dt: datetime) -> Optional[datetime]:
    """
    將本地時間轉換為 UTC 時間。

    Args:
        local_dt: 本地時間

    Returns:
        Optional[datetime]: UTC 時間，輸入為 None 時返回 None
    """
    if local_dt is None:
        return None

    # 如果沒有時區資訊，假設為本地時間
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=TAIWAN_TIMEZONE)

    return local_dt.astimezone(timezone.utc)


def get_utc_timestamp() -> str:
    """
    取得 UTC 時間戳記，格式為 ISO 8601。

    使用現代的方法來處理時間戳記，避免警告。

    Returns:
        str: ISO 8601 格式的 UTC 時間戳記
    """
    logger.debug("get_utc_timestamp() called: 生成 UTC 時間戳記")
    # 使用 datetime.now(timezone.utc) 然後格式化，避免 replace() 警告
    utc_now = datetime.now(timezone.utc)
    # 格式化為 ISO 8601，移除微秒部分
    timestamp = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"get_utc_timestamp() success: 生成時間戳記 {timestamp}")
    return timestamp


# 為了向後相容性，提供別名函數
def now_local() -> datetime:
    """
    取得當前本地時間（台灣時間）的別名函數。

    Returns:
        datetime: 當前本地時間，包含時區資訊
    """
    return get_local_now()


def now_utc() -> datetime:
    """
    取得當前 UTC 時間的別名函數。

    Returns:
        datetime: 當前 UTC 時間
    """
    return datetime.now(timezone.utc)


def utc_to_local(utc_dt: datetime) -> Optional[datetime]:
    """
    將 UTC 時間轉換為本地時間的別名函數。

    Args:
        utc_dt: UTC 時間

    Returns:
        Optional[datetime]: 本地時間，輸入為 None 時返回 None
    """
    return convert_utc_to_local(utc_dt)


def local_to_utc(local_dt: datetime) -> Optional[datetime]:
    """
    將本地時間轉換為 UTC 時間的別名函數。

    Args:
        local_dt: 本地時間

    Returns:
        Optional[datetime]: UTC 時間，輸入為 None 時返回 None
    """
    return convert_local_to_utc(local_dt)
