"""
錯誤處理工具函式模組。

提供錯誤處理相關的工具函式，避免循環導入。
"""

from datetime import datetime, timezone


def get_utc_timestamp() -> str:
    """
    取得 UTC 時間戳記。

    Returns:
        str: ISO 格式的 UTC 時間戳記
    """
    return datetime.now(timezone.utc).isoformat()
