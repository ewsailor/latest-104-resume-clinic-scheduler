"""
模型輔助工具模組。

提供共用的模型相關工具函式，避免重複代碼。
"""

from typing import Any


def format_datetime(dt) -> str | None:
    """
    格式化日期時間為 ISO 字串，如果為 None 則返回 None。

    Args:
        dt: 日期時間物件或 None

    Returns:
        str | None: ISO 格式的字串或 None
    """
    return dt.isoformat() if dt else None


def safe_getattr(obj: Any, attr_name: str, default=None) -> Any:
    """
    安全地取得物件屬性，避免 AttributeError。

    Args:
        obj: 要取得屬性的物件
        attr_name: 屬性名稱
        default: 預設值，當屬性不存在或發生錯誤時返回

    Returns:
        Any: 屬性值或預設值
    """
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default
