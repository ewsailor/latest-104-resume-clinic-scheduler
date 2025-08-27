"""模型輔助工具模組。

提供共用的模型相關工具函式，避免重複代碼。
"""

# ===== 標準函式庫 =====
from typing import Any


def format_datetime(dt: Any) -> str | None:
    """格式化日期時間為 ISO 字串，如果為 None 則返回 None。"""
    return dt.isoformat() if dt else None


def safe_getattr(obj: Any, attr_name: str, default: Any = None) -> Any:
    """安全地取得物件屬性，避免 AttributeError。"""
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default
