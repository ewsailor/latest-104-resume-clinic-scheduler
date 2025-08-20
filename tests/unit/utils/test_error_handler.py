"""
錯誤處理工具測試模組。

測試錯誤處理機制的各種功能。
"""

import pytest
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.utils.error_handler import (
    APIError,
    BusinessLogicError,
    DatabaseError,
    ErrorCode,
    NotFoundError,
)
from app.utils.error_handler import ValidationError as CustomValidationError
from app.utils.error_handler import (
    create_http_exception_from_api_error,
    create_schedule_not_found_error,
    create_user_not_found_error,
    format_error_response,
    handle_database_error,
    log_error,
    safe_execute,
)
from tests.logger import log_test_info


class TestErrorCode:
    """測試錯誤代碼常數"""

    def test_error_codes_defined(self):
        """測試錯誤代碼是否正確定義"""
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.BUSINESS_LOGIC_ERROR == "BUSINESS_LOGIC_ERROR"
        assert ErrorCode.DATABASE_ERROR == "DATABASE_ERROR"
        assert ErrorCode.AUTHENTICATION_ERROR == "AUTHENTICATION_ERROR"
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"


class TestAPIError:
    """測試 APIError 基礎類別"""

    def test_api_error_creation(self):
        """測試 APIError 創建"""
        error = APIError(
            message="測試錯誤",
            error_code="TEST_ERROR",
            status_code=400,
            details={"field": "test"},
            context="測試",
        )

        assert error.message == "測試錯誤"
        assert error.error_code == "TEST_ERROR"
        assert error.status_code == 400
        assert error.details == {"field": "test"}
        assert error.context == "測試"
        assert str(error) == "測試錯誤"

    def test_api_error_default_values(self):
        """測試 APIError 預設值"""
        error = APIError("測試錯誤", "TEST_ERROR")

        assert error.status_code == 400
        assert error.details == {}
        assert error.context is None


class TestCustomErrors:
    """測試自定義錯誤類別"""

    def test_validation_error(self):
        """測試驗證錯誤"""
        error = CustomValidationError("驗證失敗", {"field": "email"})

        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.status_code == 422
        assert error.details == {"field": "email"}

    def test_business_logic_error(self):
        """測試業務邏輯錯誤"""
        error = BusinessLogicError("業務邏輯錯誤", "BUSINESS_ERROR", {"reason": "test"})

        assert error.error_code == "BUSINESS_ERROR"
        assert error.status_code == 400
        assert error.details == {"reason": "test"}

    def test_database_error(self):
        """測試資料庫錯誤"""
        error = DatabaseError("資料庫錯誤", {"operation": "select"})

        assert error.error_code == ErrorCode.DATABASE_ERROR
        assert error.status_code == 500
        assert error.details == {"operation": "select"}

    def test_not_found_error(self):
        """測試資源不存在錯誤"""
        error = NotFoundError("使用者", 123)

        assert error.error_code == "使用者_NOT_FOUND"
        assert error.status_code == 404
        assert error.message == "使用者不存在: ID=123"


class TestErrorFactoryFunctions:
    """測試錯誤工廠函數"""

    def test_create_user_not_found_error(self):
        """測試創建使用者不存在錯誤"""
        error = create_user_not_found_error(123)

        assert isinstance(error, NotFoundError)
        assert error.error_code == "使用者_NOT_FOUND"
        assert error.status_code == 404

    def test_create_schedule_not_found_error(self):
        """測試創建時段不存在錯誤"""
        error = create_schedule_not_found_error(456)

        assert isinstance(error, NotFoundError)
        assert error.error_code == "時段_NOT_FOUND"
        assert error.status_code == 404


class TestFormatErrorResponse:
    """測試錯誤回應格式化"""

    def test_format_api_error_response(self):
        """測試格式化 APIError 回應"""
        error = APIError("測試錯誤", "TEST_ERROR", 400, {"detail": "test"})
        response = format_error_response(error)

        assert "error" in response
        assert response["error"]["code"] == "TEST_ERROR"
        assert response["error"]["message"] == "測試錯誤"
        assert response["error"]["status_code"] == 400
        assert response["error"]["details"] == {"detail": "test"}

    def test_format_http_exception_response(self):
        """測試格式化 HTTPException 回應"""
        error = HTTPException(status_code=404, detail="Not Found")
        response = format_error_response(error)

        assert "error" in response
        assert response["error"]["code"] == "HTTP_ERROR"
        assert response["error"]["message"] == "Not Found"
        assert response["error"]["status_code"] == 404

    def test_format_validation_error_response(self):
        """測試格式化 Pydantic ValidationError 回應"""
        try:
            # 創建一個 Pydantic 驗證錯誤
            raise ValidationError.from_exception_data(
                "TestModel",
                [{"loc": ("field",), "msg": "field required", "type": "missing"}],
            )
        except ValidationError as e:
            response = format_error_response(e)

            assert "error" in response
            assert response["error"]["code"] == ErrorCode.VALIDATION_ERROR
            assert response["error"]["status_code"] == 422

    def test_format_unknown_error_response(self):
        """測試格式化未知錯誤回應"""
        error = Exception("未知錯誤")
        response = format_error_response(error)

        assert "error" in response
        assert response["error"]["code"] == ErrorCode.INTERNAL_ERROR
        assert response["error"]["status_code"] == 500

    def test_format_error_response_with_request_id(self):
        """測試格式化錯誤回應包含請求 ID"""
        error = APIError("測試錯誤", "TEST_ERROR")
        response = format_error_response(error, request_id="test-123")

        assert response["error"]["request_id"] == "test-123"


class TestHandleDatabaseError:
    """測試資料庫錯誤處理"""

    def test_handle_connection_error(self):
        """測試處理連線錯誤"""
        original_error = Exception("connection failed")
        error = handle_database_error(original_error, "查詢")

        assert isinstance(error, DatabaseError)
        assert error.error_code == ErrorCode.CONNECTION_ERROR
        assert "連線失敗" in error.message

    def test_handle_transaction_error(self):
        """測試處理交易錯誤"""
        original_error = Exception("transaction failed")
        error = handle_database_error(original_error, "更新")

        assert isinstance(error, DatabaseError)
        assert error.error_code == ErrorCode.TRANSACTION_ERROR
        assert "交易失敗" in error.message

    def test_handle_general_database_error(self):
        """測試處理一般資料庫錯誤"""
        original_error = Exception("general database error")
        error = handle_database_error(original_error, "刪除")

        assert isinstance(error, DatabaseError)
        assert error.error_code == ErrorCode.DATABASE_ERROR
        assert "資料庫操作失敗" in error.message


class TestSafeExecute:
    """測試安全執行函數"""

    def test_safe_execute_success(self):
        """測試安全執行成功"""

        def test_func(a, b):
            return a + b

        result = safe_execute(test_func, 1, 2, error_context="測試")
        assert result == 3

    def test_safe_execute_with_api_error(self):
        """測試安全執行遇到 APIError"""

        def test_func():
            raise APIError("測試錯誤", "TEST_ERROR")

        with pytest.raises(APIError) as exc_info:
            safe_execute(test_func, error_context="測試")

        assert exc_info.value.message == "測試錯誤"
        assert exc_info.value.error_code == "TEST_ERROR"

    def test_safe_execute_with_validation_error(self):
        """測試安全執行遇到 Pydantic ValidationError"""

        def test_func():
            raise ValidationError.from_exception_data(
                "TestModel",
                [{"loc": ("field",), "msg": "field required", "type": "missing"}],
            )

        with pytest.raises(CustomValidationError) as exc_info:
            safe_execute(test_func, error_context="測試")

        assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
        assert exc_info.value.status_code == 422

    def test_safe_execute_with_general_exception(self):
        """測試安全執行遇到一般異常"""

        def test_func():
            raise Exception("一般錯誤")

        with pytest.raises(APIError) as exc_info:
            safe_execute(
                test_func, error_context="測試", default_error_message="操作失敗"
            )

        assert exc_info.value.error_code == ErrorCode.INTERNAL_ERROR
        assert exc_info.value.status_code == 500
        assert "操作失敗" in exc_info.value.message


class TestLogError:
    """測試錯誤日誌記錄"""

    def test_log_error_with_api_error(self, caplog):
        """測試記錄 APIError"""
        error = APIError("測試錯誤", "TEST_ERROR")
        log_error(error, context="測試")

        assert "測試錯誤" in caplog.text

    def test_log_error_with_request_info(self, caplog):
        """測試記錄錯誤包含請求資訊"""
        error = APIError("測試錯誤", "TEST_ERROR")
        request_info = {"method": "GET", "url": "/test"}

        log_error(error, context="測試", request_info=request_info)

        assert "測試錯誤" in caplog.text

    def test_log_error_with_user_info(self, caplog):
        """測試記錄錯誤包含使用者資訊"""
        error = APIError("測試錯誤", "TEST_ERROR")
        user_info = {"user_id": 123, "role": "admin"}

        log_error(error, context="測試", user_info=user_info)

        assert "測試錯誤" in caplog.text


class TestErrorHandlerIntegration:
    """測試錯誤處理器整合"""

    def test_error_chain(self):
        """測試錯誤鏈處理"""

        # 模擬資料庫層拋出錯誤
        def database_operation():
            raise Exception("資料庫連線失敗")

        # 模擬 CRUD 層處理
        def crud_operation():
            try:
                database_operation()
            except Exception as e:
                raise handle_database_error(e, "查詢使用者")

        # 模擬 API 層處理
        def api_operation():
            try:
                crud_operation()
            except DatabaseError as e:
                raise create_http_exception_from_api_error(e)

        # 測試整個錯誤鏈
        with pytest.raises(HTTPException) as exc_info:
            api_operation()

        assert exc_info.value.status_code == 500
        assert "資料庫連線失敗" in str(exc_info.value.detail)
