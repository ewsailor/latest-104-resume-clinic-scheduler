"""
錯誤處理裝飾器測試模組。

測試各種錯誤處理裝飾器的功能。
"""

# ===== 標準函式庫 =====
import asyncio
from unittest.mock import Mock, patch

# ===== 第三方套件 =====
from fastapi import HTTPException
import pytest

# ===== 本地模組 =====
from app.decorators.error_handlers import (
    handle_api_errors_async,
    handle_generic_errors_async,
    handle_generic_errors_sync,
    handle_service_errors_sync,
)
from app.errors.exceptions import APIError, DatabaseError


class TestErrorHandlers:
    """錯誤處理裝飾器測試類別。"""

    def test_handle_api_errors_async_success(self):
        """測試 API 錯誤處理裝飾器成功情況。"""

        @handle_api_errors_async()
        async def test_func():
            return "success"

        async def run_test():
            result = await test_func()
            assert result == "success"

        asyncio.run(run_test())

    def test_handle_api_errors_async_api_error(self):
        """測試 API 錯誤處理裝飾器處理 APIError。"""

        @handle_api_errors_async()
        async def test_func():
            raise APIError("API 錯誤", {"code": "TEST_ERROR"})

        async def run_test():
            with pytest.raises(APIError) as exc_info:
                await test_func()
            assert "API 錯誤" in str(exc_info.value)

        asyncio.run(run_test())

    def test_handle_api_errors_async_http_exception(self):
        """測試 API 錯誤處理裝飾器處理 HTTPException。"""

        @handle_api_errors_async()
        async def test_func():
            raise HTTPException(status_code=400, detail="Bad Request")

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await test_func()
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Bad Request"

        asyncio.run(run_test())

    @patch('app.decorators.error_handlers.logger')
    def test_handle_api_errors_async_generic_exception(self, mock_logger):
        """測試 API 錯誤處理裝飾器處理一般異常。"""

        @handle_api_errors_async()
        async def test_func():
            raise ValueError("一般錯誤")

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await test_func()
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "內部伺服器錯誤"
            mock_logger.error.assert_called_once()

        asyncio.run(run_test())

    def test_handle_service_errors_sync_success(self):
        """測試 Service 錯誤處理裝飾器成功情況。"""

        @handle_service_errors_sync("測試操作")
        def test_func(db):
            return "success"

        mock_db = Mock()
        result = test_func(mock_db)
        assert result == "success"

    def test_handle_service_errors_sync_api_error(self):
        """測試 Service 錯誤處理裝飾器處理 APIError。"""

        @handle_service_errors_sync("測試操作")
        def test_func(db):
            raise APIError("API 錯誤", {"code": "TEST_ERROR"})

        mock_db = Mock()
        with pytest.raises(APIError) as exc_info:
            test_func(mock_db)
        assert "API 錯誤" in str(exc_info.value)

    def test_handle_service_errors_sync_http_exception(self):
        """測試 Service 錯誤處理裝飾器處理 HTTPException。"""

        @handle_service_errors_sync("測試操作")
        def test_func(db):
            raise HTTPException(status_code=400, detail="Bad Request")

        mock_db = Mock()
        with pytest.raises(HTTPException) as exc_info:
            test_func(mock_db)
        assert exc_info.value.status_code == 400

    @patch('app.decorators.error_handlers.logger')
    def test_handle_service_errors_sync_generic_exception_with_rollback(
        self, mock_logger
    ):
        """測試 Service 錯誤處理裝飾器處理一般異常並回滾。"""

        @handle_service_errors_sync("測試操作")
        def test_func(db):
            raise ValueError("一般錯誤")

        mock_db = Mock()
        mock_db.rollback = Mock()

        with pytest.raises(DatabaseError) as exc_info:
            test_func(mock_db)

        assert "資料庫操作失敗" in str(exc_info.value)
        mock_db.rollback.assert_called_once()
        mock_logger.debug.assert_called_once()
        mock_logger.error.assert_called_once()

    @patch('app.decorators.error_handlers.logger')
    def test_handle_service_errors_sync_rollback_failure(self, mock_logger):
        """測試 Service 錯誤處理裝飾器回滾失敗情況。"""

        @handle_service_errors_sync("測試操作")
        def test_func(db):
            raise ValueError("一般錯誤")

        mock_db = Mock()
        mock_db.rollback = Mock(side_effect=Exception("回滾失敗"))

        with pytest.raises(DatabaseError) as exc_info:
            test_func(mock_db)

        assert "資料庫操作失敗" in str(exc_info.value)
        mock_logger.error.assert_called()
        # 應該記錄回滾失敗的錯誤
        rollback_error_calls = [
            call
            for call in mock_logger.error.call_args_list
            if "回滾資料庫事務失敗" in str(call)
        ]
        assert len(rollback_error_calls) > 0

    def test_handle_service_errors_sync_no_db_parameter(self):
        """測試 Service 錯誤處理裝飾器沒有 db 參數的情況。"""

        @handle_service_errors_sync("測試操作")
        def test_func():
            raise ValueError("一般錯誤")

        with pytest.raises(DatabaseError) as exc_info:
            test_func()

        assert "資料庫操作失敗" in str(exc_info.value)

    def test_handle_generic_errors_sync_success(self):
        """測試通用錯誤處理裝飾器成功情況。"""

        @handle_generic_errors_sync("測試操作")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_handle_generic_errors_sync_api_error(self):
        """測試通用錯誤處理裝飾器處理 APIError。"""

        @handle_generic_errors_sync("測試操作")
        def test_func():
            raise APIError("API 錯誤", {"code": "TEST_ERROR"})

        with pytest.raises(APIError) as exc_info:
            test_func()
        assert "API 錯誤" in str(exc_info.value)

    def test_handle_generic_errors_sync_http_exception(self):
        """測試通用錯誤處理裝飾器處理 HTTPException。"""

        @handle_generic_errors_sync("測試操作")
        def test_func():
            raise HTTPException(status_code=400, detail="Bad Request")

        with pytest.raises(HTTPException) as exc_info:
            test_func()
        assert exc_info.value.status_code == 400

    @patch('app.decorators.error_handlers.logger')
    def test_handle_generic_errors_sync_generic_exception(self, mock_logger):
        """測試通用錯誤處理裝飾器處理一般異常。"""

        @handle_generic_errors_sync("測試操作")
        def test_func():
            raise ValueError("一般錯誤")

        with pytest.raises(ValueError) as exc_info:
            test_func()
        assert "一般錯誤" in str(exc_info.value)
        mock_logger.error.assert_called_once()

    @patch('app.decorators.error_handlers.logger')
    def test_handle_generic_errors_sync_custom_log_level(self, mock_logger):
        """測試通用錯誤處理裝飾器自定義日誌級別。"""

        @handle_generic_errors_sync("測試操作", log_level="warning")
        def test_func():
            raise ValueError("一般錯誤")

        with pytest.raises(ValueError):
            test_func()
        mock_logger.warning.assert_called_once()

    def test_handle_generic_errors_async_success(self):
        """測試通用錯誤處理裝飾器（非同步）成功情況。"""

        @handle_generic_errors_async("測試操作")
        async def test_func():
            return "success"

        async def run_test():
            result = await test_func()
            assert result == "success"

        asyncio.run(run_test())

    def test_handle_generic_errors_async_api_error(self):
        """測試通用錯誤處理裝飾器（非同步）處理 APIError。"""

        @handle_generic_errors_async("測試操作")
        async def test_func():
            raise APIError("API 錯誤", {"code": "TEST_ERROR"})

        async def run_test():
            with pytest.raises(APIError) as exc_info:
                await test_func()
            assert "API 錯誤" in str(exc_info.value)

        asyncio.run(run_test())

    def test_handle_generic_errors_async_http_exception(self):
        """測試通用錯誤處理裝飾器（非同步）處理 HTTPException。"""

        @handle_generic_errors_async("測試操作")
        async def test_func():
            raise HTTPException(status_code=400, detail="Bad Request")

        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await test_func()
            assert exc_info.value.status_code == 400

        asyncio.run(run_test())

    @patch('app.decorators.error_handlers.logger')
    def test_handle_generic_errors_async_generic_exception(self, mock_logger):
        """測試通用錯誤處理裝飾器（非同步）處理一般異常。"""

        @handle_generic_errors_async("測試操作")
        async def test_func():
            raise ValueError("一般錯誤")

        async def run_test():
            with pytest.raises(ValueError) as exc_info:
                await test_func()
            assert "一般錯誤" in str(exc_info.value)
            mock_logger.error.assert_called_once()

        asyncio.run(run_test())

    @patch('app.decorators.error_handlers.logger')
    def test_handle_generic_errors_async_custom_log_level(self, mock_logger):
        """測試通用錯誤處理裝飾器（非同步）自定義日誌級別。"""

        @handle_generic_errors_async("測試操作", log_level="warning")
        async def test_func():
            raise ValueError("一般錯誤")

        async def run_test():
            with pytest.raises(ValueError):
                await test_func()
            mock_logger.warning.assert_called_once()

        asyncio.run(run_test())

    def test_decorator_preserves_function_metadata(self):
        """測試裝飾器保留函數元數據。"""

        @handle_generic_errors_sync("測試操作")
        def test_func(param1: str, param2: int = 10) -> str:
            """測試函數文檔字符串。"""
            return f"{param1}_{param2}"

        # 檢查函數名稱
        assert test_func.__name__ == "test_func"

        # 檢查文檔字符串
        assert test_func.__doc__ == "測試函數文檔字符串。"

        # 檢查函數簽名
        import inspect

        sig = inspect.signature(test_func)
        assert "param1" in sig.parameters
        assert "param2" in sig.parameters

    def test_decorator_with_args_and_kwargs(self):
        """測試裝飾器處理函數參數和關鍵字參數。"""

        @handle_generic_errors_sync("測試操作")
        def test_func(*args, **kwargs):
            return {"args": args, "kwargs": kwargs}

        result = test_func("arg1", "arg2", key1="value1", key2="value2")
        assert result["args"] == ("arg1", "arg2")
        assert result["kwargs"] == {"key1": "value1", "key2": "value2"}

    def test_decorator_chain(self):
        """測試裝飾器鏈式使用。"""

        @handle_generic_errors_sync("外層操作")
        @handle_generic_errors_sync("內層操作")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"
