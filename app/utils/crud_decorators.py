"""
CRUD 操作裝飾器模組。

提供統一的錯誤處理裝飾器，減少重複的 try-except 程式碼。
"""

import logging
from functools import wraps
from typing import Any, Callable

from app.utils.error_handler import APIError, handle_database_error

logger = logging.getLogger(__name__)


def handle_crud_errors(error_context: str, enable_logging: bool = True):
    """
    CRUD 錯誤處理裝飾器。

    統一處理 CRUD 操作中的錯誤，包括：
    - 重新拋出 APIError
    - 將其他錯誤轉換為 DatabaseError
    - 可選的日誌記錄

    Args:
        error_context: 錯誤上下文描述
        enable_logging: 是否啟用日誌記錄

    Returns:
        裝飾器函數
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except APIError:
                # 重新拋出 APIError，不轉換
                raise
            except Exception as e:
                # 記錄錯誤（如果啟用）
                if enable_logging:
                    logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)

                # 將其他錯誤轉換為 DatabaseError
                raise handle_database_error(e, error_context)

        return wrapper

    return decorator


def handle_crud_errors_with_rollback(error_context: str, db_param_name: str = "db"):
    """
    帶回滾功能的 CRUD 錯誤處理裝飾器。

    適用於需要事務管理的操作（如 create、update、delete）。

    Args:
        error_context: 錯誤上下文描述
        db_param_name: 資料庫會話參數名稱

    Returns:
        裝飾器函數
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 取得資料庫會話
            db = None

            # 1. 先從關鍵字參數中尋找
            if db_param_name in kwargs:
                db = kwargs[db_param_name]
            # 2. 從位置參數中尋找
            elif len(args) > 0:
                # 檢查函數簽名來確定 db 參數的位置
                import inspect

                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                # 跳過 self 參數（如果是實例方法）
                start_idx = 1 if args and hasattr(args[0], '__class__') else 0

                # 尋找 db 參數的位置
                for i, param_name in enumerate(
                    param_names[start_idx:], start=start_idx
                ):
                    if param_name == db_param_name and i < len(args):
                        db = args[i]
                        break

                # 如果還是沒有找到，嘗試簡單的方法
                if db is None and len(args) > 0:
                    db = args[0]

            try:
                return func(*args, **kwargs)
            except APIError:
                # 重新拋出 APIError
                raise
            except Exception as e:
                # 回滾資料庫事務
                if db:
                    try:
                        db.rollback()
                        logger.debug(f"{error_context}時發生錯誤，已回滾資料庫事務")
                    except Exception as rollback_error:
                        logger.error(f"回滾資料庫事務失敗: {str(rollback_error)}")

                # 記錄錯誤
                logger.error(f"{error_context}時發生錯誤: {str(e)}", exc_info=True)

                # 轉換為 DatabaseError
                raise handle_database_error(e, error_context)

        return wrapper

    return decorator


def validate_parameters(*param_validators: Callable):
    """
    參數驗證裝飾器。

    用於驗證函數參數的有效性。

    Args:
        *param_validators: 參數驗證函數列表

    Returns:
        裝飾器函數
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 執行所有參數驗證
            for validator in param_validators:
                validator(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_crud_operation(
    operation_name: str, log_args: bool = True, log_result: bool = False
):
    """
    CRUD 操作日誌裝飾器。

    記錄 CRUD 操作的開始、結束和結果。

    Args:
        operation_name: 操作名稱
        log_args: 是否記錄參數
        log_result: 是否記錄結果

    Returns:
        裝飾器函數
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 記錄操作開始
            if log_args:
                logger.info(f"開始{operation_name}: args={args}, kwargs={kwargs}")
            else:
                logger.info(f"開始{operation_name}")

            try:
                result = func(*args, **kwargs)

                # 記錄操作成功
                if log_result:
                    logger.info(f"{operation_name}成功: result={result}")
                else:
                    logger.info(f"{operation_name}成功")

                return result

            except Exception as e:
                # 記錄操作失敗
                logger.error(f"{operation_name}失敗: {str(e)}")
                # 重新拋出異常，讓上層裝飾器處理
                raise e

        return wrapper

    return decorator
