"""
錯誤處理裝飾器模組。

提供統一的錯誤處理裝飾器，減少重複的 try-except 程式碼。
"""

# ===== 標準函式庫 =====
from functools import wraps
import logging
from typing import Any, Callable

# ===== 本地模組 =====
from app.errors.exceptions import APIError, DatabaseError

logger = logging.getLogger(__name__)


def handle_crud_errors(error_context: str):
    """
    CRUD 錯誤處理裝飾器。

    提供統一的錯誤處理邏輯，自動記錄錯誤並轉換為 APIError。

    Args:
        error_context: 錯誤上下文描述，用於日誌記錄
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except APIError:
                raise
            except Exception as e:
                logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)
                error_message = f"資料庫操作失敗 ({error_context}): {str(e)}"
                raise DatabaseError(
                    error_message,
                    {"operation": error_context, "original_error": str(e)},
                )

        return wrapper

    return decorator


def handle_crud_errors_with_rollback(error_context: str):
    """
    帶回滾功能的 CRUD 錯誤處理裝飾器。

    提供統一的錯誤處理邏輯，包含資料庫事務回滾功能。

    Args:
        error_context: 錯誤上下文描述，用於日誌記錄
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 簡單地假設第一個參數是 db（通常是這樣）
            db = args[0] if args else None

            try:
                return func(*args, **kwargs)
            except APIError:
                raise
            except Exception as e:
                # 回滾資料庫事務
                if db and hasattr(db, 'rollback'):
                    try:
                        db.rollback()
                        logger.debug(f"{error_context}時發生錯誤，已回滾資料庫事務")
                    except Exception as rollback_error:
                        logger.error(f"回滾資料庫事務失敗: {str(rollback_error)}")

                logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)
                error_message = f"資料庫操作失敗 ({error_context}): {str(e)}"
                raise DatabaseError(
                    error_message,
                    {"operation": error_context, "original_error": str(e)},
                )

        return wrapper

    return decorator
