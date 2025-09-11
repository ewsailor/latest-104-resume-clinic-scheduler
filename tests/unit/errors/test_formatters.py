"""
錯誤格式化測試模組。

測試錯誤格式化功能。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

# ===== 第三方套件 =====
from fastapi import HTTPException

# ===== 本地模組 =====
from app.errors.exceptions import (
    AuthenticationError,
    BusinessLogicError,
    DatabaseError,
    ValidationError,
)
from app.errors.formatters import format_error_response


class TestFormatErrorResponse:
    """format_error_response 函數測試。"""

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_api_error(self, mock_timestamp):
        """測試格式化 APIError。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = ValidationError("驗證失敗", {"field": "email"})
        result = format_error_response(error)

        expected = {
            "error": {
                "message": "驗證失敗",
                "status_code": 422,
                "code": "ROUTER_VALIDATION_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"field": "email"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_api_error_without_details(self, mock_timestamp):
        """測試格式化沒有詳細資訊的 APIError。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = AuthenticationError("認證失敗")
        result = format_error_response(error)

        expected = {
            "error": {
                "message": "認證失敗",
                "status_code": 401,
                "code": "ROUTER_AUTHENTICATION_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_http_exception_with_detail(self, mock_timestamp):
        """測試格式化帶詳細資訊的 HTTPException。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = HTTPException(status_code=400, detail="請求參數錯誤")
        result = format_error_response(error)

        expected = {
            "error": {
                "message": "請求參數錯誤",
                "status_code": 400,
                "code": "HTTP_400",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"detail": "請求參數錯誤"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_http_exception_without_detail(self, mock_timestamp):
        """測試格式化沒有詳細資訊的 HTTPException。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = HTTPException(status_code=500)
        result = format_error_response(error)

        # HTTPException 會自動生成 detail
        expected = {
            "error": {
                "message": "Internal Server Error",
                "status_code": 500,
                "code": "HTTP_500",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"detail": "Internal Server Error"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_http_exception_with_none_detail(self, mock_timestamp):
        """測試格式化 detail 為 None 的 HTTPException。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = HTTPException(status_code=404, detail=None)
        result = format_error_response(error)

        # HTTPException 會自動生成 detail
        expected = {
            "error": {
                "message": "Not Found",
                "status_code": 404,
                "code": "HTTP_404",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"detail": "Not Found"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_generic_exception(self, mock_timestamp):
        """測試格式化一般異常。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = ValueError("一般錯誤")
        result = format_error_response(error)

        expected = {
            "error": {
                "message": "一般錯誤",
                "status_code": 500,
                "code": "INTERNAL_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"error": "一般錯誤"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_exception_without_message(self, mock_timestamp):
        """測試格式化沒有訊息的異常。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = Exception()
        result = format_error_response(error)

        expected = {
            "error": {
                "message": "",
                "status_code": 500,
                "code": "INTERNAL_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"error": ""},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_different_api_errors(self, mock_timestamp):
        """測試格式化不同類型的 APIError。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        # 測試 BusinessLogicError
        business_error = BusinessLogicError("業務邏輯錯誤", {"operation": "create"})
        result = format_error_response(business_error)

        expected = {
            "error": {
                "message": "業務邏輯錯誤",
                "status_code": 400,
                "code": "SERVICE_BUSINESS_LOGIC_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"operation": "create"},
            }
        }
        assert result == expected

        # 測試 DatabaseError
        db_error = DatabaseError("資料庫錯誤", {"table": "users"})
        result = format_error_response(db_error)

        expected = {
            "error": {
                "message": "資料庫錯誤",
                "status_code": 500,
                "code": "CRUD_DATABASE_ERROR",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {"table": "users"},
            }
        }
        assert result == expected

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_error_response_structure(self, mock_timestamp):
        """測試錯誤回應結構。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        error = ValidationError("測試錯誤", {"field": "test"})
        result = format_error_response(error)

        # 檢查回應結構
        assert "error" in result
        error_obj = result["error"]

        # 檢查必要欄位
        required_fields = ["message", "status_code", "code", "timestamp", "details"]
        for field in required_fields:
            assert field in error_obj

        # 檢查欄位類型
        assert isinstance(error_obj["message"], str)
        assert isinstance(error_obj["status_code"], int)
        assert isinstance(error_obj["code"], str)
        assert isinstance(error_obj["timestamp"], str)
        assert isinstance(error_obj["details"], dict)

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_error_response_timestamp_consistency(self, mock_timestamp):
        """測試錯誤回應時間戳一致性。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        # 多次調用應該使用相同的時間戳
        error1 = ValidationError("錯誤1")
        error2 = BusinessLogicError("錯誤2")

        result1 = format_error_response(error1)
        result2 = format_error_response(error2)

        assert result1["error"]["timestamp"] == "2024-01-01T00:00:00Z"
        assert result2["error"]["timestamp"] == "2024-01-01T00:00:00Z"
        assert result1["error"]["timestamp"] == result2["error"]["timestamp"]

    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_error_response_logging(self, mock_timestamp):
        """測試錯誤格式化日誌記錄。"""
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"

        with patch('app.errors.formatters.logger') as mock_logger:
            error = ValidationError("測試錯誤")
            format_error_response(error)

            # 檢查是否記錄了日誌
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "格式化錯誤: ValidationError" in call_args

    def test_format_error_response_with_complex_details(self):
        """測試格式化帶複雜詳細資訊的錯誤。"""
        with patch('app.errors.formatters.get_utc_timestamp') as mock_timestamp:
            mock_timestamp.return_value = "2024-01-01T00:00:00Z"

            complex_details = {
                "validation_errors": [
                    {"field": "email", "message": "格式不正確"},
                    {"field": "password", "message": "長度不足"},
                ],
                "request_id": "req-123",
                "user_id": 456,
            }

            error = ValidationError("多個驗證錯誤", complex_details)
            result = format_error_response(error)

            assert result["error"]["details"] == complex_details
            assert len(result["error"]["details"]["validation_errors"]) == 2
            assert result["error"]["details"]["request_id"] == "req-123"
            assert result["error"]["details"]["user_id"] == 456
