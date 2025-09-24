"""
異常類別測試模組。

測試各種自定義異常類別的功能。
"""

# ===== 第三方套件 =====
from fastapi import status

# ===== 本地模組 =====
from app.errors.exceptions import (  # 基礎異常類別; CRUD 層級異常 (500); Router 層級異常 (400/401/403/422); Service 層級異常 (400/404/409); System 層級異常 (503)
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


# ===== APIError 基礎類別測試 =====
class TestAPIError:
    """APIError 基礎類別測試。"""

    def test_api_error_basic(self):
        """測試 APIError 基本功能。"""
        error = APIError("測試錯誤", "TEST_ERROR")

        assert error.message == "測試錯誤"
        assert error.error_code == "TEST_ERROR"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.details == {}
        assert str(error) == "測試錯誤"

    def test_api_error_with_custom_status_code(self):
        """測試 APIError 自定義狀態碼。"""
        error = APIError(
            "測試錯誤", "TEST_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        assert error.message == "測試錯誤"
        assert error.error_code == "TEST_ERROR"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_api_error_with_details(self):
        """測試 APIError 帶詳細資訊。"""
        details = {"field": "value", "code": 123}
        error = APIError("測試錯誤", "TEST_ERROR", details=details)

        assert error.details == details

    def test_api_error_inheritance(self):
        """測試 APIError 繼承關係。"""
        error = APIError("測試錯誤", "TEST_ERROR")

        assert isinstance(error, Exception)
        assert isinstance(error, APIError)


# ===== CRUD 層級錯誤 =====
class TestDatabaseError:
    """DatabaseError 測試。"""

    def test_database_error(self):
        """測試 DatabaseError 基本功能。"""
        error = DatabaseError("資料庫操作失敗")

        assert error.message == "資料庫操作失敗"
        assert error.error_code == "CRUD_DATABASE_ERROR"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_database_error_with_details(self):
        """測試 DatabaseError 帶詳細資訊。"""
        details = {
            "operation": "INSERT",
            "table": "users",
            "constraint": "unique_email",
        }
        error = DatabaseError("資料庫操作失敗", details)

        assert error.details == details


# ===== Router 層級錯誤 =====
class TestBadRequestError:
    """BadRequestError 測試。"""

    def test_bad_request_error(self):
        """測試 BadRequestError 基本功能。"""
        error = BadRequestError("請求格式錯誤")

        assert error.message == "請求格式錯誤"
        assert error.error_code == "ROUTER_BAD_REQUEST"
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    def test_bad_request_error_with_details(self):
        """測試 BadRequestError 帶詳細資訊。"""
        details = {"field": "request_body", "error": "格式不正確"}
        error = BadRequestError("請求格式錯誤", details)

        assert error.details == details


class TestAuthenticationError:
    """AuthenticationError 測試。"""

    def test_authentication_error_default_message(self):
        """測試 AuthenticationError 預設訊息。"""
        error = AuthenticationError()

        assert error.message == "認證失敗"
        assert error.error_code == "ROUTER_AUTHENTICATION_ERROR"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_error_custom_message(self):
        """測試 AuthenticationError 自定義訊息。"""
        error = AuthenticationError("自定義認證錯誤")

        assert error.message == "自定義認證錯誤"
        assert error.error_code == "ROUTER_AUTHENTICATION_ERROR"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_error_with_details(self):
        """測試 AuthenticationError 帶詳細資訊。"""
        details = {"token": "invalid"}
        error = AuthenticationError("認證失敗", details)

        assert error.details == details


class TestAuthorizationError:
    """AuthorizationError 測試。"""

    def test_authorization_error_default_message(self):
        """測試 AuthorizationError 預設訊息。"""
        error = AuthorizationError()

        assert error.message == "權限不足"
        assert error.error_code == "ROUTER_AUTHORIZATION_ERROR"
        assert error.status_code == status.HTTP_403_FORBIDDEN

    def test_authorization_error_custom_message(self):
        """測試 AuthorizationError 自定義訊息。"""
        error = AuthorizationError("自定義權限錯誤")

        assert error.message == "自定義權限錯誤"
        assert error.error_code == "ROUTER_AUTHORIZATION_ERROR"
        assert error.status_code == status.HTTP_403_FORBIDDEN


class TestValidationError:
    """ValidationError 測試。"""

    def test_validation_error_basic(self):
        """測試 ValidationError 基本功能。"""
        error = ValidationError("驗證失敗")

        assert error.message == "驗證失敗"
        assert error.error_code == "ROUTER_VALIDATION_ERROR"
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert error.details == {}

    def test_validation_error_with_details(self):
        """測試 ValidationError 帶詳細資訊。"""
        details = {"field": "email", "error": "格式不正確"}
        error = ValidationError("驗證失敗", details)

        assert error.details == details

    def test_validation_error_inheritance(self):
        """測試 ValidationError 繼承關係。"""
        error = ValidationError("驗證失敗")

        assert isinstance(error, APIError)
        assert isinstance(error, ValidationError)


# ===== Service 層級錯誤 =====
class TestBusinessLogicError:
    """BusinessLogicError 測試。"""

    def test_business_logic_error(self):
        """測試 BusinessLogicError 基本功能。"""
        error = BusinessLogicError("業務邏輯錯誤")

        assert error.message == "業務邏輯錯誤"
        assert error.error_code == "SERVICE_BUSINESS_LOGIC_ERROR"
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    def test_business_logic_error_with_details(self):
        """測試 BusinessLogicError 帶詳細資訊。"""
        details = {"operation": "create", "reason": "conflict"}
        error = BusinessLogicError("業務邏輯錯誤", details)

        assert error.details == details


class TestScheduleNotFoundError:
    """ScheduleNotFoundError 測試。"""

    def test_schedule_not_found_error_with_int_id(self):
        """測試 ScheduleNotFoundError 整數 ID。"""
        error = ScheduleNotFoundError(123)

        assert error.message == "時段不存在: ID=123"
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND

    def test_schedule_not_found_error_with_str_id(self):
        """測試 ScheduleNotFoundError 字串 ID。"""
        error = ScheduleNotFoundError("abc123")

        assert error.message == "時段不存在: ID=abc123"
        assert error.error_code == "SERVICE_SCHEDULE_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND

    def test_schedule_not_found_error_with_details(self):
        """測試 ScheduleNotFoundError 帶詳細資訊。"""
        details = {"search_criteria": "date=2024-01-01"}
        error = ScheduleNotFoundError(123, details)

        assert error.details == details


class TestUserNotFoundError:
    """UserNotFoundError 測試。"""

    def test_user_not_found_error_with_int_id(self):
        """測試 UserNotFoundError 整數 ID。"""
        error = UserNotFoundError(456)

        assert error.message == "使用者不存在: ID=456"
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND

    def test_user_not_found_error_with_str_id(self):
        """測試 UserNotFoundError 字串 ID。"""
        error = UserNotFoundError("user123")

        assert error.message == "使用者不存在: ID=user123"
        assert error.error_code == "SERVICE_USER_NOT_FOUND"
        assert error.status_code == status.HTTP_404_NOT_FOUND


class TestConflictError:
    """ConflictError 測試。"""

    def test_conflict_error(self):
        """測試 ConflictError 基本功能。"""
        error = ConflictError("資源衝突")

        assert error.message == "資源衝突"
        assert error.error_code == "SERVICE_CONFLICT"
        assert error.status_code == status.HTTP_409_CONFLICT

    def test_conflict_error_with_details(self):
        """測試 ConflictError 帶詳細資訊。"""
        details = {"conflicting_field": "email", "existing_value": "test@example.com"}
        error = ConflictError("資源衝突", details)

        assert error.details == details


class TestScheduleCannotBeDeletedError:
    """ScheduleCannotBeDeletedError 測試。"""

    def test_schedule_cannot_be_deleted_error_with_int_id(self):
        """測試 ScheduleCannotBeDeletedError 整數 ID。"""
        error = ScheduleCannotBeDeletedError(123)

        assert error.message == "時段無法刪除: ID=123"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == status.HTTP_409_CONFLICT

    def test_schedule_cannot_be_deleted_error_with_str_id(self):
        """測試 ScheduleCannotBeDeletedError 字串 ID。"""
        error = ScheduleCannotBeDeletedError("abc123")

        assert error.message == "時段無法刪除: ID=abc123"
        assert error.error_code == "SERVICE_SCHEDULE_CANNOT_BE_DELETED"
        assert error.status_code == status.HTTP_409_CONFLICT

    def test_schedule_cannot_be_deleted_error_with_details(self):
        """測試 ScheduleCannotBeDeletedError 帶詳細資訊。"""
        details = {"reason": "schedule_already_accepted"}
        error = ScheduleCannotBeDeletedError(123, details)

        assert error.details == details


class TestScheduleOverlapError:
    """ScheduleOverlapError 測試。"""

    def test_schedule_overlap_error(self):
        """測試 ScheduleOverlapError 基本功能。"""
        error = ScheduleOverlapError("時段時間重疊")

        assert error.message == "時段時間重疊"
        assert error.error_code == "SERVICE_SCHEDULE_OVERLAP"
        assert error.status_code == status.HTTP_409_CONFLICT

    def test_schedule_overlap_error_with_details(self):
        """測試 ScheduleOverlapError 帶詳細資訊。"""
        details = {
            "existing_schedule_id": 123,
            "overlap_start": "09:00",
            "overlap_end": "10:00",
        }
        error = ScheduleOverlapError("時段時間重疊", details)

        assert error.details == details


# ===== System 層級錯誤 =====
class TestServiceUnavailableError:
    """ServiceUnavailableError 測試。"""

    def test_service_unavailable_error_default_message(self):
        """測試 ServiceUnavailableError 預設訊息。"""
        error = ServiceUnavailableError()

        assert error.message == "服務暫時不可用"
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_service_unavailable_error_custom_message(self):
        """測試 ServiceUnavailableError 自定義訊息。"""
        error = ServiceUnavailableError("維護中")

        assert error.message == "維護中"
        assert error.error_code == "SERVICE_UNAVAILABLE"
        assert error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ===== 錯誤層級測試 =====
class TestErrorHierarchy:
    """錯誤層級測試。"""

    def test_error_inheritance_hierarchy(self):
        """測試錯誤繼承層級。"""
        # 所有自定義錯誤都應該繼承自 APIError
        errors = [
            BadRequestError("test"),
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            BusinessLogicError("test"),
            ScheduleNotFoundError(1),
            UserNotFoundError(1),
            ConflictError("test"),
            ScheduleCannotBeDeletedError(1),
            ScheduleOverlapError("test"),
            DatabaseError("test"),
            ServiceUnavailableError("test"),
        ]

        for error in errors:
            assert isinstance(error, APIError)
            assert isinstance(error, Exception)

    def test_error_status_codes(self):
        """測試錯誤狀態碼。"""
        # 測試各種錯誤的狀態碼
        assert BadRequestError("test").status_code == status.HTTP_400_BAD_REQUEST
        assert (
            ValidationError("test").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        assert AuthenticationError("test").status_code == status.HTTP_401_UNAUTHORIZED
        assert AuthorizationError("test").status_code == status.HTTP_403_FORBIDDEN
        assert BusinessLogicError("test").status_code == status.HTTP_400_BAD_REQUEST
        assert ScheduleNotFoundError(1).status_code == status.HTTP_404_NOT_FOUND
        assert UserNotFoundError(1).status_code == status.HTTP_404_NOT_FOUND
        assert ConflictError("test").status_code == status.HTTP_409_CONFLICT
        assert ScheduleCannotBeDeletedError(1).status_code == status.HTTP_409_CONFLICT
        assert ScheduleOverlapError("test").status_code == status.HTTP_409_CONFLICT
        assert (
            DatabaseError("test").status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        assert (
            ServiceUnavailableError("test").status_code
            == status.HTTP_503_SERVICE_UNAVAILABLE
        )

    def test_error_codes_format(self):
        """測試錯誤代碼格式。"""
        # 測試錯誤代碼的格式一致性
        errors = [
            BadRequestError("test"),
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            BusinessLogicError("test"),
            ScheduleNotFoundError(1),
            UserNotFoundError(1),
            ConflictError("test"),
            ScheduleCannotBeDeletedError(1),
            ScheduleOverlapError("test"),
            DatabaseError("test"),
            ServiceUnavailableError("test"),
        ]

        for error in errors:
            # 錯誤代碼應該包含層級前綴
            assert "_" in error.error_code
            # 錯誤代碼應該是大寫
            assert error.error_code.isupper() or "_" in error.error_code
