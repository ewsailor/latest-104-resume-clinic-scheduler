"""
CRUD 裝飾器測試模組。

測試 CRUD 裝飾器的各種功能，包括錯誤處理、回滾機制等。
"""

from unittest.mock import Mock, patch

import pytest

from app.utils.crud_decorators import (
    handle_crud_errors,
    handle_crud_errors_with_rollback,
    log_crud_operation,
)
from app.utils.error_handler import APIError, DatabaseError


class TestHandleCrudErrors:
    """測試 handle_crud_errors 裝飾器"""

    def test_successful_execution(self):
        """測試正常執行"""

        @handle_crud_errors("測試操作")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_api_error_passthrough(self):
        """測試 APIError 直接傳遞"""

        @handle_crud_errors("測試操作")
        def test_func():
            raise APIError("測試錯誤", "TEST_ERROR", 400)

        with pytest.raises(APIError) as exc_info:
            test_func()

        assert str(exc_info.value) == "測試錯誤"

    def test_general_error_conversion(self):
        """測試一般錯誤轉換為 DatabaseError"""

        @handle_crud_errors("測試操作")
        def test_func():
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError) as exc_info:
            test_func()

        assert "測試操作" in str(exc_info.value)

    def test_logging_disabled(self):
        """測試日誌記錄被禁用"""
        with patch('app.utils.crud_decorators.logger') as mock_logger:

            @handle_crud_errors("測試操作", enable_logging=False)
            def test_func():
                raise ValueError("參數錯誤")

            with pytest.raises(DatabaseError):
                test_func()

            # 驗證沒有記錄錯誤日誌
            mock_logger.error.assert_not_called()


class TestHandleCrudErrorsWithRollback:
    """測試 handle_crud_errors_with_rollback 裝飾器"""

    def test_successful_execution(self):
        """測試正常執行"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        def test_func(db):
            return "success"

        result = test_func(mock_db)
        assert result == "success"
        # 驗證沒有回滾
        mock_db.rollback.assert_not_called()

    def test_api_error_passthrough(self):
        """測試 APIError 直接傳遞，不回滾"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        def test_func(db):
            raise APIError("測試錯誤", "TEST_ERROR", 400)

        with pytest.raises(APIError):
            test_func(mock_db)

        # 驗證沒有回滾
        mock_db.rollback.assert_not_called()

    def test_general_error_with_rollback(self):
        """測試一般錯誤時執行回滾"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        def test_func(db):
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError):
            test_func(mock_db)

        # 驗證執行了回滾
        mock_db.rollback.assert_called_once()

    def test_rollback_failure(self):
        """測試回滾失敗的情況"""
        mock_db = Mock()
        mock_db.rollback.side_effect = Exception("回滾失敗")

        @handle_crud_errors_with_rollback("測試操作")
        def test_func(db):
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError):
            test_func(mock_db)

        # 驗證嘗試了回滾
        mock_db.rollback.assert_called_once()

    def test_db_parameter_detection(self):
        """測試資料庫參數的自動檢測"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作", db_param_name="database")
        def test_func(database):
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError):
            test_func(mock_db)

        # 驗證執行了回滾
        mock_db.rollback.assert_called_once()

    def test_db_from_positional_args(self):
        """測試從位置參數中取得資料庫會話"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        def test_func(self, db):
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError):
            test_func("self", mock_db)

        # 驗證執行了回滾
        mock_db.rollback.assert_called_once()


class TestLogCrudOperation:
    """測試 log_crud_operation 裝飾器"""

    def test_successful_execution_with_args(self):
        """測試成功執行並記錄參數"""
        with patch('app.utils.crud_decorators.logger') as mock_logger:

            @log_crud_operation("測試操作", log_args=True, log_result=False)
            def test_func(arg1, arg2):
                return "success"

            result = test_func("value1", "value2")

            assert result == "success"
            # 驗證記錄了開始和成功
            assert mock_logger.info.call_count == 2
            # 驗證記錄了參數
            mock_logger.info.assert_any_call(
                "開始測試操作: args=('value1', 'value2'), kwargs={}"
            )

    def test_successful_execution_without_args(self):
        """測試成功執行但不記錄參數"""
        with patch('app.utils.crud_decorators.logger') as mock_logger:

            @log_crud_operation("測試操作", log_args=False, log_result=True)
            def test_func():
                return "success"

            result = test_func()

            assert result == "success"
            # 驗證記錄了開始和成功
            assert mock_logger.info.call_count == 2
            # 驗證沒有記錄參數
            mock_logger.info.assert_any_call("開始測試操作")
            mock_logger.info.assert_any_call("測試操作成功: result=success")

    def test_failed_execution(self):
        """測試執行失敗的情況"""
        with patch('app.utils.crud_decorators.logger') as mock_logger:

            @log_crud_operation("測試操作", log_args=False)
            def test_func():
                raise ValueError("操作失敗")

            with pytest.raises(ValueError):
                test_func()

            # 驗證記錄了開始和失敗
            assert mock_logger.info.call_count == 1
            assert mock_logger.error.call_count == 1
            mock_logger.info.assert_called_with("開始測試操作")
            mock_logger.error.assert_called_with("測試操作失敗: 操作失敗")


class TestDecoratorCombination:
    """測試裝飾器組合使用"""

    def test_multiple_decorators(self):
        """測試多個裝飾器組合"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        @log_crud_operation("測試操作", log_args=False)
        def test_func(db):
            return "success"

        result = test_func(mock_db)
        assert result == "success"
        # 驗證沒有回滾
        mock_db.rollback.assert_not_called()

    def test_multiple_decorators_with_error(self):
        """測試多個裝飾器組合且發生錯誤"""
        mock_db = Mock()

        @handle_crud_errors_with_rollback("測試操作")
        @log_crud_operation("測試操作", log_args=False)
        def test_func(db):
            raise ValueError("參數錯誤")

        with pytest.raises(DatabaseError):
            test_func(mock_db)

        # 驗證執行了回滾
        mock_db.rollback.assert_called_once()


class TestRealWorldScenario:
    """測試真實世界場景"""

    def test_crud_method_simulation(self):
        """模擬真實的 CRUD 方法"""
        mock_db = Mock()

        @log_crud_operation("建立時段", log_args=False)
        @handle_crud_errors_with_rollback("建立時段")
        def create_schedule(db, schedule_data):
            # 模擬業務邏輯
            if schedule_data.get("invalid"):
                raise ValueError("無效的時段資料")

            # 模擬資料庫操作
            db.add("schedule")
            db.commit()
            return {"id": 1, "status": "created"}

        # 測試成功情況
        result = create_schedule(mock_db, {"name": "test"})
        assert result["id"] == 1
        mock_db.add.assert_called_with("schedule")
        mock_db.commit.assert_called_once()
        mock_db.rollback.assert_not_called()

        # 測試失敗情況
        with pytest.raises(DatabaseError):
            create_schedule(mock_db, {"invalid": True})

        # 驗證執行了回滾
        assert mock_db.rollback.call_count == 1
