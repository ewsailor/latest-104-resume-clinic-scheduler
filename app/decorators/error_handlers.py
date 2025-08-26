"""
錯誤處理裝飾器模組。

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
from app.errors.handlers import create_http_exception_from_api_error

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


def handle_api_errors(
    success_status_code: int | None = None,
    conflict_status_code: int = 409,
    internal_error_status_code: int = 500,
    not_found_status_code: int = 404,
    bad_request_status_code: int = 400,
):
    """
    API 錯誤處理裝飾器。

    提供統一的 API 錯誤處理邏輯，自動處理各種異常並轉換為適當的 HTTP 回應。
    如果未指定 success_status_code，會根據 HTTP 方法自動設定。

    Args:
        success_status_code: 成功時的 HTTP 狀態碼（None 時自動檢測）
        conflict_status_code: 衝突時的 HTTP 狀態碼（如重複資料）
        internal_error_status_code: 內部錯誤時的 HTTP 狀態碼
        not_found_status_code: 找不到資源時的 HTTP 狀態碼
        bad_request_status_code: 請求錯誤時的 HTTP 狀態碼
    """

    def get_default_status_code(func: Callable) -> int:
        """
        根據函數的 FastAPI 路由資訊自動檢測預設狀態碼。

        Args:
            func: FastAPI 路由函數

        Returns:
            int: 預設的 HTTP 狀態碼
        """
        # 嘗試從 FastAPI 路由資訊中獲取狀態碼
        if hasattr(func, '__wrapped__'):
            # 檢查是否有 FastAPI 路由裝飾器
            wrapped = func.__wrapped__
            if hasattr(wrapped, 'status_code'):
                return wrapped.status_code

        # 檢查函數是否有 FastAPI 路由資訊
        if hasattr(func, '__name__'):
            func_name = func.__name__.lower()

            # 根據函數名稱推測 HTTP 方法（備用方案）
            if func_name.startswith('get'):
                return 200
            elif func_name.startswith('post'):
                return 201
            elif func_name.startswith('put'):
                return 200
            elif func_name.startswith('patch'):
                return 200
            elif func_name.startswith('delete'):
                return 204

        # 預設返回 200
        return 200

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 自動檢測 HTTP 方法和路由資訊
            auto_success_code = success_status_code
            if auto_success_code is None:
                # 嘗試從 FastAPI 路由資訊中獲取預設狀態碼
                auto_success_code = get_default_status_code(func)

            try:
                return await func(*args, **kwargs)
            except APIError as e:
                # 處理自定義 API 錯誤
                raise create_http_exception_from_api_error(e)
            except ValueError as e:
                # 處理驗證錯誤（如重複 email）
                logger.warning(f"驗證錯誤: {str(e)}")
                raise HTTPException(
                    status_code=conflict_status_code,
                    detail=str(e),
                )
            except HTTPException:
                # 重新拋出 HTTPException，避免被 Exception 捕獲
                raise
            except Exception as e:
                # 處理其他未預期的錯誤
                logger.error(f"API 端點發生未預期錯誤: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=internal_error_status_code,
                    detail=f"內部伺服器錯誤: {str(e)}",
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
            except ValueError:
                # 讓 ValueError 直接向上傳遞，由 API 層處理
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
