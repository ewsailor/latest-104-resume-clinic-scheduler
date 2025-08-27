"""錯誤處理裝飾器模組。

提供統一的錯誤處理裝飾器，減少重複的 try-except 程式碼。
"""

# ===== 標準函式庫 =====
from functools import wraps
import logging
from typing import Any, Callable

# ===== 第三方套件 =====
from fastapi import HTTPException

# ===== 本地模組 =====
from app.errors.exceptions import APIError, DatabaseError

logger = logging.getLogger(__name__)


def handle_api_errors() -> Callable:
    """API 錯誤處理裝飾器。"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except APIError:
                # 向上傳遞 APIError，讓中間件處理
                raise
            except HTTPException:
                # 重新拋出 HTTPException
                raise
            except Exception as e:
                # 處理其他未預期的錯誤
                logger.error(f"API 端點發生未預期錯誤: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="內部伺服器錯誤")

        return wrapper

    return decorator


def handle_service_errors(error_context: str) -> Callable:
    """Service 層錯誤處理裝飾器。"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 假設第一個參數是 db
            db = args[0] if args else None

            try:
                return func(*args, **kwargs)
            except APIError:
                # 向上傳遞 APIError，讓中間件處理
                raise
            except HTTPException:
                # 重新拋出 HTTPException
                raise
            except Exception as e:
                # 回滾資料庫事務
                if db and hasattr(db, "rollback"):
                    try:
                        db.rollback()
                        logger.debug(f"{error_context}時發生錯誤，已回滾資料庫事務")
                    except Exception as rollback_error:
                        logger.error(f"回滾資料庫事務失敗: {str(rollback_error)}")

                logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)
                raise DatabaseError(
                    f"資料庫操作失敗 ({error_context}): {str(e)}",
                    {"operation": error_context, "original_error": str(e)},
                )

        return wrapper

    return decorator
