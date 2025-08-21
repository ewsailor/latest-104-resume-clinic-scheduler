"""
CRUD 操作裝飾器模組。

提供統一的錯誤處理裝飾器，減少重複的 try-except 程式碼。
"""

from functools import wraps
import logging
from typing import Any, Callable

from app.errors import APIError, handle_database_error

logger = logging.getLogger(__name__)


def handle_crud_errors(error_context: str):
    """CRUD 錯誤處理裝飾器。"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except APIError:
                raise
            except Exception as e:
                logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)
                raise handle_database_error(e, error_context)

        return wrapper

    return decorator


def handle_crud_errors_with_rollback(error_context: str):
    """帶回滾功能的 CRUD 錯誤處理裝飾器。"""

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
                raise handle_database_error(e, error_context)

        return wrapper

    return decorator


def log_crud_operation(operation_name: str):
    """CRUD 操作日誌裝飾器。"""

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
