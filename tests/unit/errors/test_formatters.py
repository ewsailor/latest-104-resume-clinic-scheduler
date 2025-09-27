"""
錯誤格式化測試模組。

測試錯誤格式化功能。
"""

# ===== 標準函式庫 =====
from unittest.mock import patch

from fastapi import HTTPException

# ===== 第三方套件 =====
import pytest

# ===== 本地模組 =====
from app.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    ScheduleCannotBeDeletedError,
    ScheduleNotFoundError,
    ScheduleOverlapError,
    ServiceUnavailableError,
    UserNotFoundError,
    ValidationError,
)
from app.errors.formatters import format_error_response


class TestFormatErrorResponse:
    """format_error_response 函數測試。"""

    @pytest.mark.parametrize(
        "error_factory,expected_message,expected_status_code,expected_code,expected_details",
        [
            # ===== APIError 基礎類別測試 =====
            # 基本測試
            (
                lambda: APIError("基礎錯誤", "TEST_ERROR"),
                "基礎錯誤",
                400,
                "TEST_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: APIError("基礎錯誤", "TEST_ERROR", 400, {}),
                "基礎錯誤",
                400,
                "TEST_ERROR",
                {},
            ),
            # 自定義狀態碼測試
            (
                lambda: APIError("基礎錯誤", "TEST_ERROR", 500),
                "基礎錯誤",
                500,
                "TEST_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: APIError("基礎錯誤", "TEST_ERROR", 400, {"test": "value"}),
                "基礎錯誤",
                400,
                "TEST_ERROR",
                {"test": "value"},
            ),
            # ===== CRUD 層級錯誤測試 =====
            # DatabaseError 測試
            # 基本測試
            (
                lambda: DatabaseError("資料庫錯誤"),
                "資料庫錯誤",
                500,
                "CRUD_DATABASE_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: DatabaseError("資料庫錯誤", {}),
                "資料庫錯誤",
                500,
                "CRUD_DATABASE_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: DatabaseError("資料庫錯誤", {"table": "users"}),
                "資料庫錯誤",
                500,
                "CRUD_DATABASE_ERROR",
                {"table": "users"},
            ),
            # ===== Router 層級錯誤測試 =====
            # BadRequestError 測試
            # 基本測試
            (
                lambda: BadRequestError("請求錯誤"),
                "請求錯誤",
                400,
                "ROUTER_BAD_REQUEST",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: BadRequestError("請求錯誤", {}),
                "請求錯誤",
                400,
                "ROUTER_BAD_REQUEST",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: BadRequestError("請求錯誤", {"field": "body"}),
                "請求錯誤",
                400,
                "ROUTER_BAD_REQUEST",
                {"field": "body"},
            ),
            # AuthenticationError 測試
            # 基本測試
            (
                lambda: AuthenticationError("認證錯誤"),
                "認證錯誤",
                401,
                "ROUTER_AUTHENTICATION_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: AuthenticationError("認證錯誤", {}),
                "認證錯誤",
                401,
                "ROUTER_AUTHENTICATION_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: AuthenticationError("認證錯誤", {"token": "invalid"}),
                "認證錯誤",
                401,
                "ROUTER_AUTHENTICATION_ERROR",
                {"token": "invalid"},
            ),
            # AuthorizationError 測試
            # 基本測試
            (
                lambda: AuthorizationError("權限錯誤"),
                "權限錯誤",
                403,
                "ROUTER_AUTHORIZATION_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: AuthorizationError("權限錯誤", {}),
                "權限錯誤",
                403,
                "ROUTER_AUTHORIZATION_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: AuthorizationError("權限錯誤", {"resource": "admin"}),
                "權限錯誤",
                403,
                "ROUTER_AUTHORIZATION_ERROR",
                {"resource": "admin"},
            ),
            # ValidationError 測試
            # 基本測試
            (
                lambda: ValidationError("驗證錯誤"),
                "驗證錯誤",
                422,
                "ROUTER_VALIDATION_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ValidationError("驗證錯誤", {}),
                "驗證錯誤",
                422,
                "ROUTER_VALIDATION_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ValidationError("驗證錯誤", {"field": "email"}),
                "驗證錯誤",
                422,
                "ROUTER_VALIDATION_ERROR",
                {"field": "email"},
            ),
            # ===== Service 層級錯誤測試 =====
            # BusinessLogicError 測試
            # 基本測試
            (
                lambda: BusinessLogicError("業務邏輯錯誤"),
                "業務邏輯錯誤",
                400,
                "SERVICE_BUSINESS_LOGIC_ERROR",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: BusinessLogicError("業務邏輯錯誤", {}),
                "業務邏輯錯誤",
                400,
                "SERVICE_BUSINESS_LOGIC_ERROR",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: BusinessLogicError("業務邏輯錯誤", {"operation": "create"}),
                "業務邏輯錯誤",
                400,
                "SERVICE_BUSINESS_LOGIC_ERROR",
                {"operation": "create"},
            ),
            # ScheduleNotFoundError 測試
            # 基本測試
            (
                lambda: ScheduleNotFoundError(123),
                "時段不存在: ID=123",
                404,
                "SERVICE_SCHEDULE_NOT_FOUND",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ScheduleNotFoundError(123, {}),
                "時段不存在: ID=123",
                404,
                "SERVICE_SCHEDULE_NOT_FOUND",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ScheduleNotFoundError(123, {"search": "date=2024-01-01"}),
                "時段不存在: ID=123",
                404,
                "SERVICE_SCHEDULE_NOT_FOUND",
                {"search": "date=2024-01-01"},
            ),
            # UserNotFoundError 測試
            # 基本測試
            (
                lambda: UserNotFoundError(456),
                "使用者不存在: ID=456",
                404,
                "SERVICE_USER_NOT_FOUND",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: UserNotFoundError(456, {}),
                "使用者不存在: ID=456",
                404,
                "SERVICE_USER_NOT_FOUND",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: UserNotFoundError(456, {"email": "test@example.com"}),
                "使用者不存在: ID=456",
                404,
                "SERVICE_USER_NOT_FOUND",
                {"email": "test@example.com"},
            ),
            # ConflictError 測試
            # 基本測試
            (
                lambda: ConflictError("衝突錯誤"),
                "衝突錯誤",
                409,
                "SERVICE_CONFLICT",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ConflictError("衝突錯誤", {}),
                "衝突錯誤",
                409,
                "SERVICE_CONFLICT",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ConflictError("衝突錯誤", {"field": "email"}),
                "衝突錯誤",
                409,
                "SERVICE_CONFLICT",
                {"field": "email"},
            ),
            # ScheduleCannotBeDeletedError 測試
            # 基本測試
            (
                lambda: ScheduleCannotBeDeletedError(123),
                "時段無法刪除: ID=123",
                409,
                "SERVICE_SCHEDULE_CANNOT_BE_DELETED",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ScheduleCannotBeDeletedError(123, {}),
                "時段無法刪除: ID=123",
                409,
                "SERVICE_SCHEDULE_CANNOT_BE_DELETED",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ScheduleCannotBeDeletedError(123, {"reason": "accepted"}),
                "時段無法刪除: ID=123",
                409,
                "SERVICE_SCHEDULE_CANNOT_BE_DELETED",
                {"reason": "accepted"},
            ),
            # ScheduleOverlapError 測試
            # 基本測試
            (
                lambda: ScheduleOverlapError("時段重疊錯誤"),
                "時段重疊錯誤",
                409,
                "SERVICE_SCHEDULE_OVERLAP",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ScheduleOverlapError("時段重疊錯誤", {}),
                "時段重疊錯誤",
                409,
                "SERVICE_SCHEDULE_OVERLAP",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ScheduleOverlapError("時段重疊錯誤", {"existing": 123}),
                "時段重疊錯誤",
                409,
                "SERVICE_SCHEDULE_OVERLAP",
                {"existing": 123},
            ),
            # ===== System 層級錯誤測試 =====
            # ServiceUnavailableError 測試
            # 基本測試
            (
                lambda: ServiceUnavailableError("服務錯誤"),
                "服務錯誤",
                503,
                "SERVICE_UNAVAILABLE",
                {},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: ServiceUnavailableError("服務錯誤", {}),
                "服務錯誤",
                503,
                "SERVICE_UNAVAILABLE",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: ServiceUnavailableError("服務錯誤", {"duration": "2小時"}),
                "服務錯誤",
                503,
                "SERVICE_UNAVAILABLE",
                {"duration": "2小時"},
            ),
            # ===== HTTPException 測試 =====
            # 基本測試：有 detail 屬性
            (
                lambda: HTTPException(status_code=400, detail="HTTP錯誤"),
                "HTTP錯誤",
                400,
                "HTTP_400",
                {"detail": "HTTP錯誤"},
            ),
            # 邊界測試：空 detail 屬性
            (
                lambda: HTTPException(status_code=400, detail=''),
                "請求錯誤",
                400,
                "HTTP_400",
                {},
            ),
            # 帶詳細資訊測試
            (
                lambda: HTTPException(status_code=404, detail="Not Found"),
                "Not Found",
                404,
                "HTTP_404",
                {"detail": "Not Found"},
            ),
            # ===== 一般異常測試 =====
            # 基本測試
            (
                lambda: ValueError("一般錯誤"),
                "一般錯誤",
                500,
                "INTERNAL_ERROR",
                {"error": "一般錯誤"},
            ),
            # 邊界測試：空詳細資訊
            (
                lambda: Exception(),
                "",
                500,
                "INTERNAL_ERROR",
                {"error": ""},
            ),
            # 帶詳細資訊測試
            (
                lambda: Exception("一般錯誤", {"error": "一般錯誤"}),
                "('一般錯誤', {'error': '一般錯誤'})",
                500,
                "INTERNAL_ERROR",
                {"error": "('一般錯誤', {'error': '一般錯誤'})"},
            ),
        ],
    )
    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_error_response(
        self,
        mock_timestamp,
        error_factory,
        expected_message,
        expected_status_code,
        expected_code,
        expected_details,
    ):
        """測試格式化各種錯誤類型。"""
        # Given: 準備測試環境和預期結果
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"
        expected = {
            "error": {
                "message": expected_message,
                "status_code": expected_status_code,
                "code": expected_code,
                "timestamp": "2024-01-01T00:00:00Z",
                "details": expected_details,
            }
        }

        # When: 建立錯誤並格式化
        error = error_factory()
        result = format_error_response(error)

        # Then: 驗證格式化結果
        assert result == expected

    @pytest.mark.parametrize(
        "error_factory",
        [
            # APIError 基礎類別
            lambda: APIError("基礎錯誤", "TEST_ERROR"),
            # CRUD 層級
            lambda: DatabaseError("資料庫錯誤"),
            # Router 層級
            lambda: BadRequestError("請求錯誤"),
            lambda: AuthenticationError("認證錯誤"),
            lambda: AuthorizationError("權限錯誤"),
            lambda: ValidationError("驗證錯誤"),
            # Service 層級
            lambda: BusinessLogicError("業務錯誤"),
            lambda: ScheduleNotFoundError(123),
            lambda: UserNotFoundError(456),
            lambda: ConflictError("衝突錯誤"),
            lambda: ScheduleCannotBeDeletedError(123),
            lambda: ScheduleOverlapError("時段重疊錯誤"),
            # System 層級
            lambda: ServiceUnavailableError("服務錯誤"),
            # HTTPException
            lambda: HTTPException(status_code=400, detail="HTTP錯誤"),
            # 一般錯誤
            lambda: ValueError("一般錯誤"),
        ],
    )
    @patch('app.errors.formatters.get_utc_timestamp')
    def test_format_error_response_structure(self, mock_timestamp, error_factory):
        """測試錯誤回應結構。"""
        # Given: 準備測試環境
        mock_timestamp.return_value = "2024-01-01T00:00:00Z"
        required_fields = ["message", "status_code", "code", "timestamp", "details"]

        # When: 建立錯誤並格式化
        error = error_factory()
        result = format_error_response(error)

        # Then: 驗證回應結構
        assert "error" in result
        error_obj = result["error"]

        # 驗證必要欄位存在
        for field in required_fields:
            assert field in error_obj

        # 驗證欄位類型
        assert isinstance(error_obj["message"], str)
        assert isinstance(error_obj["status_code"], int)
        assert isinstance(error_obj["code"], str)
        assert isinstance(error_obj["timestamp"], str)
        assert isinstance(error_obj["details"], dict)
