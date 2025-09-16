"""
日誌裝飾器測試模組。

測試日誌記錄裝飾器的功能。
"""

import inspect

# ===== 標準函式庫 =====
from unittest.mock import patch

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.decorators.logging import log_operation


class TestLoggingDecorator:
    """日誌裝飾器測試類別。"""

    @patch('app.decorators.logging.logger')
    def test_log_operation_success(self, mock_logger):
        """測試日誌裝飾器成功情況。"""

        @log_operation("測試操作")
        def test_func():
            return "success"

        result = test_func()

        assert result == "success"
        mock_logger.info.assert_any_call("開始測試操作")
        mock_logger.info.assert_any_call("測試操作成功")

    @patch('app.decorators.logging.logger')
    def test_log_operation_failure(self, mock_logger):
        """測試日誌裝飾器失敗情況。"""

        @log_operation("測試操作")
        def test_func():
            raise ValueError("測試錯誤")

        with pytest.raises(ValueError) as exc_info:
            test_func()

        assert "測試錯誤" in str(exc_info.value)
        mock_logger.info.assert_called_with("開始測試操作")
        mock_logger.error.assert_called_with("測試操作失敗: 測試錯誤")

    @patch('app.decorators.logging.logger')
    def test_log_operation_with_parameters(self, mock_logger):
        """測試日誌裝飾器帶參數的函數。"""

        @log_operation("計算操作")
        def test_func(x, y, operation="add"):
            if operation == "add":
                return x + y
            elif operation == "multiply":
                return x * y
            else:
                raise ValueError(f"不支援的操作: {operation}")

        # 測試加法
        result = test_func(2, 3, "add")
        assert result == 5
        mock_logger.info.assert_any_call("開始計算操作")
        mock_logger.info.assert_any_call("計算操作成功")

        # 測試乘法
        result = test_func(2, 3, "multiply")
        assert result == 6

        # 測試錯誤情況
        with pytest.raises(ValueError):
            test_func(2, 3, "divide")

    @patch('app.decorators.logging.logger')
    def test_log_operation_with_kwargs(self, mock_logger):
        """測試日誌裝飾器帶關鍵字參數的函數。"""

        @log_operation("配置操作")
        def test_func(**kwargs):
            return kwargs

        result = test_func(key1="value1", key2="value2")

        assert result == {"key1": "value1", "key2": "value2"}
        mock_logger.info.assert_any_call("開始配置操作")
        mock_logger.info.assert_any_call("配置操作成功")

    @patch('app.decorators.logging.logger')
    def test_log_operation_with_args_and_kwargs(self, mock_logger):
        """測試日誌裝飾器帶位置參數和關鍵字參數的函數。"""

        @log_operation("混合操作")
        def test_func(*args, **kwargs):
            return {"args": args, "kwargs": kwargs}

        result = test_func("arg1", "arg2", key1="value1", key2="value2")

        expected = {
            "args": ("arg1", "arg2"),
            "kwargs": {"key1": "value1", "key2": "value2"},
        }
        assert result == expected
        mock_logger.info.assert_any_call("開始混合操作")
        mock_logger.info.assert_any_call("混合操作成功")

    @patch('app.decorators.logging.logger')
    def test_log_operation_no_return_value(self, mock_logger):
        """測試日誌裝飾器無返回值函數。"""

        @log_operation("無返回值操作")
        def test_func():
            pass

        result = test_func()

        assert result is None
        mock_logger.info.assert_any_call("開始無返回值操作")
        mock_logger.info.assert_any_call("無返回值操作成功")

    @patch('app.decorators.logging.logger')
    def test_log_operation_complex_return_value(self, mock_logger):
        """測試日誌裝飾器複雜返回值。"""

        @log_operation("複雜操作")
        def test_func():
            return {
                "data": [1, 2, 3],
                "nested": {"key": "value"},
                "boolean": True,
                "none": None,
            }

        result = test_func()

        expected = {
            "data": [1, 2, 3],
            "nested": {"key": "value"},
            "boolean": True,
            "none": None,
        }
        assert result == expected
        mock_logger.info.assert_any_call("開始複雜操作")
        mock_logger.info.assert_any_call("複雜操作成功")

    @patch('app.decorators.logging.logger')
    def test_log_operation_exception_propagation(self, mock_logger):
        """測試日誌裝飾器異常傳播。"""

        @log_operation("異常操作")
        def test_func():
            raise RuntimeError("運行時錯誤")

        with pytest.raises(RuntimeError) as exc_info:
            test_func()

        assert "運行時錯誤" in str(exc_info.value)
        mock_logger.info.assert_called_with("開始異常操作")
        mock_logger.error.assert_called_with("異常操作失敗: 運行時錯誤")

    @patch('app.decorators.logging.logger')
    def test_log_operation_custom_exception(self, mock_logger):
        """測試日誌裝飾器自定義異常。"""

        class CustomException(Exception):
            def __init__(self, message, code):
                super().__init__(message)
                self.code = code

        @log_operation("自定義異常操作")
        def test_func():
            raise CustomException("自定義錯誤", 123)

        with pytest.raises(CustomException) as exc_info:
            test_func()

        assert "自定義錯誤" in str(exc_info.value)
        assert exc_info.value.code == 123
        mock_logger.info.assert_called_with("開始自定義異常操作")
        mock_logger.error.assert_called_with("自定義異常操作失敗: 自定義錯誤")

    def test_log_operation_preserves_function_metadata(self):
        """測試日誌裝飾器保留函數元數據。"""

        @log_operation("元數據測試操作")
        def test_func(param1: str, param2: int = 10) -> str:
            """測試函數文檔字符串。"""
            return f"{param1}_{param2}"

        # 檢查函數名稱
        assert test_func.__name__ == "test_func"

        # 檢查文檔字符串
        assert test_func.__doc__ == "測試函數文檔字符串。"

        # 檢查函數簽名
        sig = inspect.signature(test_func)
        assert "param1" in sig.parameters
        assert "param2" in sig.parameters

    @patch('app.decorators.logging.logger')
    def test_log_operation_multiple_calls(self, mock_logger):
        """測試日誌裝飾器多次調用。"""

        @log_operation("多次調用操作")
        def test_func(value):
            return value * 2

        # 第一次調用
        result1 = test_func(5)
        assert result1 == 10

        # 第二次調用
        result2 = test_func(10)
        assert result2 == 20

        # 檢查日誌調用次數
        assert mock_logger.info.call_count == 4  # 2次開始 + 2次成功
        assert mock_logger.error.call_count == 0

    @patch('app.decorators.logging.logger')
    def test_log_operation_decorator_chain(self, mock_logger):
        """測試日誌裝飾器鏈式使用。"""

        @log_operation("外層操作")
        @log_operation("內層操作")
        def test_func():
            return "success"

        result = test_func()

        assert result == "success"
        # 應該記錄兩層操作的日誌
        assert mock_logger.info.call_count == 4  # 2層 × 2次日誌

    @patch('app.decorators.logging.logger')
    def test_log_operation_with_different_operation_names(self, mock_logger):
        """測試不同操作名稱的日誌裝飾器。"""

        @log_operation("操作A")
        def func_a():
            return "A"

        @log_operation("操作B")
        def func_b():
            return "B"

        result_a = func_a()
        result_b = func_b()

        assert result_a == "A"
        assert result_b == "B"

        # 檢查正確的操作名稱被記錄
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert "開始操作A" in info_calls
        assert "操作A成功" in info_calls
        assert "開始操作B" in info_calls
        assert "操作B成功" in info_calls
