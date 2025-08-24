"""
日誌裝飾器模組。

提供各種日誌記錄裝飾器，用於記錄函式執行情況。
"""

from functools import wraps
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_operation(operation_name: str):
    """
    操作日誌裝飾器。

    記錄操作的開始、成功和失敗狀態，適用於 CRUD 層和 Service 層。

    Args:
        operation_name: 操作名稱，用於日誌記錄
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"開始{operation_name}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation_name}成功")
                return result
            except Exception as e:
                logger.error(f"{operation_name}失敗: {str(e)}")
                raise e

        return wrapper

    return decorator
